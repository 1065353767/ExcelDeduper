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
    def clean_company_name(cls, raw_name):
        """
        公共清洗方法：去除前后空格、回车换行，仅保留汉字、大小写英文字母、数字，最后转全小写
        供 Excel导入 与 剪贴板实时监控 共同调用
        """
        if pd.isna(raw_name) or not raw_name:
            return ""

        val = str(raw_name).strip()
        if not val or val.lower() == 'nan':
            return ""

        # 核心修改：正则匹配，过滤掉除了(大小写字母、数字、汉字)以外的所有字符
        val = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', val)

        if not val:
            return ""

        return val.lower()

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
                continue

            col_data = df.iloc[:, col_idx].dropna().astype(str)

            for item in col_data:
                cleaned_val = cls.clean_company_name(item)
                if cleaned_val:
                    cleaned_set.add(cleaned_val)

        ExcelDatabase.save_company_cache(file_name, list(cleaned_set))
        return len(cleaned_set)