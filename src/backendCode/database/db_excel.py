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
        """
        将解析出来的公司名称批量写入 SQLite 数据库，并自动建立索引
        """
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. 初始化总表
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
                           TEXT
                       )
                       """)

        # 2. 先清空该文件之前的旧解析记录，实现覆盖更新
        cursor.execute("DELETE FROM company_master WHERE source_file = ?", (file_name,))

        # 3. 批量写入
        bulk_data = [(name, file_name) for name in names]
        cursor.executemany("INSERT INTO company_master (name, source_file) VALUES (?, ?)", bulk_data)

        # 4. 对 name 字段建立索引，保障几万条数据查询时秒级响应
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_name ON company_master(name);")

        conn.commit()
        conn.close()

    @classmethod
    def check_company_exists(cls, query_name):
        """
        验证某个公司名称是否在本地数据库中（精确匹配）
        """
        db_path = cls._get_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM company_master WHERE name = ? LIMIT 1;", (query_name.strip(),))
        result = cursor.fetchone()

        conn.close()
        return result is not None