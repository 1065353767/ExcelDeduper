import os
import sqlite3
from src.backendCode.database.app_constants import AppConstants


class ExcelDatabase:
    @staticmethod
    def _get_db_path():
        """获取并确保存储数据库的 data 目录存在，返回 db 文件绝对路径"""
        data_dir = os.path.join(AppConstants.BASE_DIR, "Repository", "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "company_cache.db")

    @classmethod
    def save_company_cache(cls, file_name, names):
        """保存并自动记录解析时间"""
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_master';")
        table_exists = cursor.fetchone()

        if table_exists:
            # 检查现有表是否包含 parsed_at 字段
            cursor.execute("PRAGMA table_info(company_master);")
            columns = [info[1] for info in cursor.fetchall()]
            if 'parsed_at' not in columns:
                # 如果没有该字段，说明是旧版表结构，安全删除旧表重建
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

        # 2. 先清空该文件之前的旧解析记录，实现覆盖更新
        cursor.execute("DELETE FROM company_master WHERE source_file = ?", (file_name,))

        # 3. 批量写入
        bulk_data = [(name, file_name) for name in names]
        cursor.executemany("""
                           INSERT INTO company_master (name, source_file, parsed_at)
                           VALUES (?, ?, DATETIME('now', 'localtime'))
                           """, bulk_data)

        # 建立索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON company_master(name);")

        conn.commit()
        conn.close()

    @classmethod
    def get_parsed_files_info(cls):
        """获取所有已解析的 Excel 文件名及最新解析时间"""
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
        """
        根据高级规则字典（包含 add/modify 和 精确/通配 del）更新数据库
        """
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        added_count = 0
        modified_count = 0
        deleted_count = 0

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS company_master
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL,
                           source_file
                           TEXT,
                           parsed_at
                           TEXT
                       )
                       """)

        # 1. 处理 add / modify 部分
        add_data = rules_dict.get("add", {})
        for k, v in add_data.items():
            k_clean = str(k).strip().lower()
            v_clean = str(v).strip().lower()

            if not k_clean:
                continue

            if not v_clean:
                # 纯新增
                cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (k_clean,))
                if not cursor.fetchone():
                    cursor.execute("""
                                   INSERT INTO company_master (name, source_file, parsed_at)
                                   VALUES (?, 'JSON规则新增', DATETIME('now', 'localtime'))
                                   """, (k_clean,))
                    added_count += 1
            else:
                # 修改：把旧的 k_clean 更新为 v_clean
                cursor.execute("SELECT id FROM company_master WHERE name = ?;", (k_clean,))
                if cursor.fetchall():
                    cursor.execute("UPDATE company_master SET name = ? WHERE name = ?;", (v_clean, k_clean))
                    modified_count += cursor.rowcount
                else:
                    # 如果原本不存在，直接作为新条目插入
                    cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (v_clean,))
                    if not cursor.fetchone():
                        cursor.execute("""
                                       INSERT INTO company_master (name, source_file, parsed_at)
                                       VALUES (?, 'JSON规则新增', DATETIME('now', 'localtime'))
                                       """, (v_clean,))
                        added_count += 1

        # 2. 处理 del 部分（支持精确删除与通配模糊删除）
        del_data = rules_dict.get("del", {})
        for k, v in del_data.items():
            k_clean = str(k).strip().lower()
            v_clean = str(v).strip().lower()

            if v_clean:
                # 后面有值，忽略前面，使用通配规则批量删除
                pattern = f"%{v_clean}%"
                cursor.execute("DELETE FROM company_master WHERE name LIKE ?;", (pattern,))
                deleted_count += cursor.rowcount
            else:
                # 后面为空，前面写要删除的条目（精确删除）
                if k_clean:
                    cursor.execute("DELETE FROM company_master WHERE name = ?;", (k_clean,))
                    deleted_count += cursor.rowcount

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON company_master(name);")
        conn.commit()
        conn.close()
        return added_count, modified_count, deleted_count

    @classmethod
    def deduplicate_database(cls):
        """全局数据库去重"""
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
    def find_matching_companies(cls, query_name):
        """
        执行双向包含查询：
        1. 数据库中的公司名包含剪贴板文本
        2. 剪贴板文本包含数据库中的公司名
        并在内存中通过 AppConstants.MATCH_LENGTH_TOLERANCE 进行宽容值筛选
        返回所有命中的公司名列表
        """
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

        # 先把所有通过包含关系查出来的结果拿出来
        raw_results = [row[0] for row in cursor.fetchall()]
        conn.close()

        # ================= 新增：内存筛选逻辑 =================
        filtered_results = []
        tolerance = AppConstants.MATCH_LENGTH_TOLERANCE

        for db_name in raw_results:
            # 计算数据库名称与剪贴板名称的长度差的绝对值
            length_diff = abs(len(db_name) - len(query_clean))

            # 只有长度差值小于等于宽容值，才被视为有效命中
            if length_diff <= tolerance:
                filtered_results.append(db_name)

        return filtered_results