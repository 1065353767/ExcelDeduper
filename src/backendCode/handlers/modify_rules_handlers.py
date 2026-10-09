import os

import copy
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem

from src.UI.ui_modify_rules import ModifyRulesDialog
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.database.db_excel import ExcelDatabase
from src.backendCode.utils.util_json import dict2json, json2dict
from src.backendCode.utils.settings_json import dispatch_json_data  # 引入新的分发工具


class ModifyRulesHandler:
    # 接收 main_handlers 传来的 app_settings
    def __init__(self, parent_ui=None, app_settings=None):
        self.dialog = ModifyRulesDialog(parent_ui)
        self.app_settings = app_settings

        self.dialog.btn_upload_json.clicked.connect(self.upload_json_rules)
        self.dialog.btn_deduplicate.clicked.connect(self.run_deduplication)
        self.dialog.btn_download_template.clicked.connect(self.download_template)

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
            data = json2dict(file_path)

            if not isinstance(data, dict):
                QMessageBox.warning(self.dialog, "提示", "JSON 文件格式错误，根节点必须是一个字典对象！")
                return

            # 调用外部的分发工具，同时处理设置修改和数据库增删
            added, modified, deleted = dispatch_json_data(data, self.app_settings)

            QMessageBox.information(
                self.dialog,
                "应用成功",
                f"高级 JSON 规则已执行完毕！\n"
                f"- 成功新增条数：{added}\n"
                f"- 成功修改条数：{modified}\n"
                f"- 成功删除条数：{deleted}\n"
                f"*(如果包含 Setting 节点，相关配置已生效)*"
            )

            self.load_parsed_files()

        except Exception as e:
            QMessageBox.critical(self.dialog, "错误", f"解析或应用 JSON 失败:\n{str(e)}")

    def download_template(self):
        try:
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            default_save_path = os.path.join(desktop_path, "excel_rules_template.json")

            file_path, _ = QFileDialog.getSaveFileName(
                self.dialog,
                "导出规则 JSON 模板",
                default_save_path,
                "JSON Files (*.json)"
            )

            if not file_path:
                return

            # ================= 新增：动态同步当前设置 =================
            # 使用深拷贝保证不污染原始常量，同时维持原有字典的排序（eg在最上）
            dynamic_template = copy.deepcopy(AppConstants.DEFAULT_RULES_EXAMPLE)
            dynamic_template["Setting"]["提示窗时间"] = self.app_settings.data.toast_duration_ms
            dynamic_template["Setting"]["赦免长度"] = self.app_settings.data.forgive_length
            # ==========================================================

            # 落盘时使用动态注入后的模板
            dict2json(dynamic_template, file_path)

            QMessageBox.information(
                self.dialog,
                "导出成功",
                f"规则模板已成功导出至：\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self.dialog, "错误", f"导出模板失败:\n{str(e)}")

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