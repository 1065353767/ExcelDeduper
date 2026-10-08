import os
import re
import pandas as pd
from src.backendCode.database.db_excel import ExcelDatabase


class ExcelTask:
    @staticmethod
    def col_letter_to_index(letter_str):
        """
        将 Excel 列字母（如 a, b, aa）转换为 pandas 的 0-based 索引
        """
        indices = []
        for part in letter_str.split(','):
            part = part.strip().upper()
            if not part:
                continue
            col_num = 0
            for char in part:
                if 'A' <= char <= 'Z':
                    col_num = col_num * 26 + (ord(char) - ord('A') + 1)
            if col_num > 0:
                indices.append(col_num - 1)
        return indices

    @classmethod
    def execute_task(cls, file_name, excel_path, cols_input):
        """
        核心任务解析：列字母转换 -> 多列合并去重 -> 清洗（去空格/符号/转小写） -> 入库
        """
        col_indices = cls.col_letter_to_index(cols_input)
        if not col_indices:
            raise ValueError("未输入有效的列字母（例如: a, b）！")

        df = pd.read_excel(excel_path)
        if df.empty:
            raise ValueError("Excel 文件内容为空！")

        cleaned_set = set()
        max_col_idx = df.shape[1] - 1

        for col_idx in col_indices:
            if col_idx > max_col_idx:
                continue  # 超出表格总列数则跳过

            # 提取指定列并转为字符串
            col_data = df.iloc[:, col_idx].dropna().astype(str)

            for item in col_data:
                # 1. 去除前后空格
                val = item.strip()
                if not val or val.lower() == 'nan':
                    continue

                # 2. 去除标点符号与特殊符号（仅保留汉字、英文字母、数字）
                val = re.sub(r'[^\w\u4e00-\u9fa5]', '', val)

                if not val:
                    continue

                # 3. 全转小写
                val = val.lower()

                cleaned_set.add(val)

        # 4. 调度底层数据库模块存入 SQLite
        ExcelDatabase.save_company_cache(file_name, list(cleaned_set))
        return len(cleaned_set)