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
        """保存并自动记录解析时间（采用安全建表/重建策略，避开 SQLite 的 ALTER TABLE 限制）"""
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
    def apply_json_rules(cls, add_list, del_list):
        """根据 JSON 中的增加和删除规则更新数据库"""
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        added_count = 0
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

        if add_list:
            for name in add_list:
                clean_name = str(name).strip().lower()
                if clean_name:
                    cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (clean_name,))
                    if not cursor.fetchone():
                        cursor.execute("""
                                       INSERT INTO company_master (name, source_file, parsed_at)
                                       VALUES (?, 'JSON规则导入', DATETIME('now', 'localtime'))
                                       """, (clean_name,))
                        added_count += 1

        if del_list:
            for name in del_list:
                clean_name = str(name).strip().lower()
                if clean_name:
                    cursor.execute("DELETE FROM company_master WHERE name = ?;", (clean_name,))
                    deleted_count += cursor.rowcount

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON company_master(name);")
        conn.commit()
        conn.close()
        return added_count, deleted_count

    @classmethod
    def deduplicate_database(cls):
        """全局数据库去重：多次导入造成的重复数据只留一条"""
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
    def check_company_exists(cls, query_name):
        """验证某个公司名称是否在本地数据库中"""
        """
        验证某个公司名称是否在本地数据库中（精确匹配）
        """
        db_path = cls._get_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_master';")
        if not cursor.fetchone():
            conn.close()
            return False

        cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (query_name.strip().lower(),))
        result = cursor.fetchone()

        conn.close()
        return result is not None