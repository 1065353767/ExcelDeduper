import os
import json
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from src.UI.ui_modify_rules import ModifyRulesDialog
from src.backendCode.database.db_excel import ExcelDatabase
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.utils.util_json import dict2json, json2dict  # 引入现有的 utils 方法


class ModifyRulesHandler:
    def __init__(self, parent_ui=None):
        self.dialog = ModifyRulesDialog(parent_ui)

        # 绑定按钮事件
        self.dialog.btn_upload_json.clicked.connect(self.upload_json_rules)
        self.dialog.btn_deduplicate.clicked.connect(self.run_deduplication)
        self.dialog.btn_download_template.clicked.connect(self.download_template)  # 绑定下载模板

        self.load_parsed_files()

    def load_parsed_files(self):
        files_info = ExcelDatabase.get_parsed_files_info()
        table = self.dialog.table_files
        table.setRowCount(len(files_info))

        for row_idx, (file_name, parse_time) in enumerate(files_info):
            item_name = QTableWidgetItem(str(file_name))
            item_time = QTableWidgetItem(str(parse_time))
            table.setItem(row_idx, 0, item_name)
            table.setItem(row_idx, 1, item_time)

    def upload_json_rules(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.dialog, "选择规则 JSON 文件", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            # 使用工具层的 json2dict 解析上传的规则文件
            data = json2dict(file_path)

            if not isinstance(data, dict):
                QMessageBox.warning(self.dialog, "提示", "JSON 文件格式错误，根节点必须是一个字典对象！")
                return

            added, modified, deleted = ExcelDatabase.apply_json_rules(data)

            QMessageBox.information(
                self.dialog,
                "规则应用成功",
                f"高级 JSON 规则执行完毕：\n"
                f"- 成功新增条数：{added}\n"
                f"- 成功修改条数：{modified}\n"
                f"- 成功删除条数：{deleted}"
            )

            self.load_parsed_files()

        except Exception as e:
            QMessageBox.critical(self.dialog, "错误", f"解析或应用 JSON 规则失败:\n{str(e)}")

    def download_template(self):
        """调用工具层的 dict2json，将固定规则模板保存到 Win10 桌面"""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~")

            file_path = os.path.join(desktop_path, "excel_rules_template.json")

            # 使用现有的 dict2json 方法落盘
            dict2json(AppConstants.DEFAULT_RULES_EXAMPLE, file_path)

            QMessageBox.information(
                self.dialog,
                "下载成功",
                f"规则模板已成功导出至您的 Win10 桌面：\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self.dialog, "错误", f"下载模板失败:\n{str(e)}")

    def run_deduplication(self):
        try:
            deleted_count = ExcelDatabase.deduplicate_database()
            QMessageBox.information(
                self.dialog,
                "去重完成",
                f"数据库去重清理完毕！共清理并移除了 {deleted_count} 条重复冗余数据。"
            )
        except Exception as e:
            QMessageBox.critical(self.dialog, "错误", f"去重操作失败:\n{str(e)}")

    def exec(self):
        return self.dialog.exec()