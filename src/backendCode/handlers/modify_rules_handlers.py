import json
import os
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QTableWidgetItem
from src.UI.ui_modify_rules import ModifyRulesDialog
from src.backendCode.database.db_excel import ExcelDatabase


class ModifyRulesHandler:
    def __init__(self, parent_ui=None):
        self.dialog = ModifyRulesDialog(parent_ui)

        # 绑定按钮事件
        self.dialog.btn_upload_json.clicked.connect(self.upload_json_rules)
        self.dialog.btn_deduplicate.clicked.connect(self.run_deduplication)

        # 初始化时加载已解析的文件表格
        self.load_parsed_files()

    def load_parsed_files(self):
        """加载数据库中记录的已解析文件和时间到表格中"""
        files_info = ExcelDatabase.get_parsed_files_info()

        table = self.dialog.table_files
        table.setRowCount(len(files_info))

        for row_idx, (file_name, parse_time) in enumerate(files_info):
            item_name = QTableWidgetItem(str(file_name))
            item_time = QTableWidgetItem(str(parse_time))

            table.setItem(row_idx, 0, item_name)
            table.setItem(row_idx, 1, item_time)

    def upload_json_rules(self):
        """上传 JSON 规则文件，支持【增加】与【删除】两部分"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.dialog, "选择规则 JSON 文件", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 兼容读取增加和删除部分
            # 预期 JSON 结构示例: {"add": ["公司A", "公司B"], "del": ["公司C"]}
            add_list = data.get("add", [])
            del_list = data.get("del", [])

            if not add_list and not del_list:
                QMessageBox.warning(self.dialog, "提示", "JSON 文件中未检测到有效的 'add' 或 'del' 数据段！")
                return

            # 调用底层应用规则
            added_count, deleted_count = ExcelDatabase.apply_json_rules(add_list, del_list)

            QMessageBox.information(
                self.dialog,
                "规则应用成功",
                f"JSON 规则执行完毕：\n- 成功增加词条：{added_count} 条\n- 成功删除词条：{deleted_count} 条"
            )

        except Exception as e:
            QMessageBox.critical(self.dialog, "错误", f"解析或应用 JSON 规则失败:\n{str(e)}")

    def run_deduplication(self):
        """一键操作数据库去重"""
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
        """显示弹窗"""
        return self.dialog.exec()