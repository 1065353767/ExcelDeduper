import os
import sqlite3

from src.backendCode.database.app_constants import AppConstants


class ExcelDatabase:
    @staticmethod
    def _get_db_path():
        data_dir = os.path.join(AppConstants.BASE_DIR, "Repository", "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "company_cache.db")

    @classmethod
    def save_company_cache(cls, file_name, names):
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_master';")
        table_exists = cursor.fetchone()

        if table_exists:
            cursor.execute("PRAGMA table_info(company_master);")
            columns = [info[1] for info in cursor.fetchall()]
            if 'parsed_at' not in columns:
                cursor.execute("DROP TABLE company_master;")
                table_exists = False

        if not table_exists:
            cursor.execute("""
                           CREATE TABLE company_master
                           (
                               id          INTEGER PRIMARY KEY AUTOINCREMENT,
                               name        TEXT NOT NULL,
                               source_file TEXT,
                               parsed_at   TEXT
                           )
                           """)

        cursor.execute("DELETE FROM company_master WHERE source_file = ?", (file_name,))

        bulk_data = [(name, file_name) for name in names]
        cursor.executemany("""
                           INSERT INTO company_master (name, source_file, parsed_at)
                           VALUES (?, ?, DATETIME('now', 'localtime'))
                           """, bulk_data)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON company_master(name);")

        conn.commit()
        conn.close()

    @classmethod
    def get_parsed_files_info(cls):
        db_path = cls._get_db_path()
        if not os.path.exists(db_path):
            return []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_master';")
        if not cursor.fetchone():
            conn.close()
            return []

        try:
            cursor.execute("""
                           SELECT source_file, MAX(parsed_at)
                           FROM company_master
                           WHERE source_file IS NOT NULL
                           GROUP BY source_file
                           ORDER BY parsed_at DESC
                           """)
            results = cursor.fetchall()
        except sqlite3.OperationalError:
            results = []

        conn.close()
        return results

    @classmethod
    def apply_json_rules(cls, rules_dict):
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        added_count = 0
        modified_count = 0
        deleted_count = 0

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS company_master
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           source_file TEXT,
                           parsed_at TEXT
                       )
                       """)

        add_data = rules_dict.get("add", {})
        for k, v in add_data.items():
            k_clean = str(k).strip().lower()
            v_clean = str(v).strip().lower()

            if not k_clean:
                continue

            if not v_clean:
                cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (k_clean,))
                if not cursor.fetchone():
                    cursor.execute("""
                                   INSERT INTO company_master (name, source_file, parsed_at)
                                   VALUES (?, 'JSON规则新增', DATETIME('now', 'localtime'))
                                   """, (k_clean,))
                    added_count += 1
            else:
                cursor.execute("SELECT id FROM company_master WHERE name = ?;", (k_clean,))
                if cursor.fetchall():
                    cursor.execute("UPDATE company_master SET name = ? WHERE name = ?;", (v_clean, k_clean))
                    modified_count += cursor.rowcount
                else:
                    cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (v_clean,))
                    if not cursor.fetchone():
                        cursor.execute("""
                                       INSERT INTO company_master (name, source_file, parsed_at)
                                       VALUES (?, 'JSON规则新增', DATETIME('now', 'localtime'))
                                       """, (v_clean,))
                        added_count += 1

        del_data = rules_dict.get("del", {})
        for k, v in del_data.items():
            k_clean = str(k).strip().lower()
            v_clean = str(v).strip().lower()

            if v_clean:
                pattern = f"%{v_clean}%"
                cursor.execute("DELETE FROM company_master WHERE name LIKE ?;", (pattern,))
                deleted_count += cursor.rowcount
            else:
                if k_clean:
                    cursor.execute("DELETE FROM company_master WHERE name = ?;", (k_clean,))
                    deleted_count += cursor.rowcount

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON company_master(name);")
        conn.commit()
        conn.close()
        return added_count, modified_count, deleted_count

    @classmethod
    def deduplicate_database(cls):
        db_path = cls._get_db_path()
        if not os.path.exists(db_path):
            return 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_master';")
        if not cursor.fetchone():
            conn.close()
            return 0

        cursor.execute("""
                       DELETE
                       FROM company_master
                       WHERE id NOT IN (SELECT MIN(id)
                                        FROM company_master
                                        GROUP BY name);
                       """)

        deleted_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_rows

    @classmethod
    # ================= 新增 tolerance 参数 =================
    def find_matching_companies(cls, query_name, tolerance=3):
        db_path = cls._get_db_path()
        if not os.path.exists(db_path):
            return []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_master';")
        if not cursor.fetchone():
            conn.close()
            return []

        query_clean = query_name.strip().lower()
        pattern = f"%{query_clean}%"

        cursor.execute("""
                       SELECT DISTINCT name
                       FROM company_master
                       WHERE name LIKE ?
                          OR ? LIKE '%' || name || '%'
                       """, (pattern, query_clean))

        raw_results = [row[0] for row in cursor.fetchall()]
        conn.close()

        filtered_results = []
        for db_name in raw_results:
            length_diff = abs(len(db_name) - len(query_clean))
            # 直接使用传进来的 tolerance 变量
            if length_diff <= tolerance:
                filtered_results.append(db_name)

        return filtered_results