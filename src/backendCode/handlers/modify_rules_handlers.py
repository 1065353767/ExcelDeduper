import os
import copy

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem

from src.UI.ui_modify_rules import ModifyRulesDialog
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.database.db_excel import ExcelDatabase
from src.backendCode.utils.util_json import dict2json, json2dict
from src.backendCode.utils.settings_json import dispatch_json_data


class ModifyRulesHandler:
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

            # 接收 4 个返回值，包含配置是否变更的布尔值
            added, modified, deleted, is_settings_changed = dispatch_json_data(data, self.app_settings)

            # ================= 新增：动态拼接提示信息 =================
            if added == 0 and modified == 0 and deleted == 0 and not is_settings_changed:
                QMessageBox.information(
                    self.dialog,
                    "提示",
                    "未检测到任何有效的数据修改或配置变更\n（已自动忽略默认模板示例内容）。"
                )
            else:
                msg_lines = ["高级 JSON 规则已执行完毕！\n"]
                if added > 0:
                    msg_lines.append(f"- 成功新增条数：{added}")
                if modified > 0:
                    msg_lines.append(f"- 成功修改条数：{modified}")
                if deleted > 0:
                    msg_lines.append(f"- 成功删除条数：{deleted}")

                if is_settings_changed:
                    msg_lines.append("\n*(检测到 Setting 节点，相关配置已更新并生效)*")

                QMessageBox.information(
                    self.dialog,
                    "应用成功",
                    "\n".join(msg_lines)
                )
            # ==========================================================

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

            # 深拷贝并注入最新的设置值
            dynamic_template = copy.deepcopy(AppConstants.DEFAULT_RULES_EXAMPLE)
            dynamic_template["Setting"]["提示窗时间"] = self.app_settings.data.toast_duration_ms
            dynamic_template["Setting"]["赦免长度"] = self.app_settings.data.forgive_length

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