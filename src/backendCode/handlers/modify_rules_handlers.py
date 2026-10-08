import json
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
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

            if not isinstance(data, dict):
                QMessageBox.warning(self.dialog, "提示", "JSON 文件格式错误，根节点必须是一个字典对象！")
                return

            # 直接传入完整的规则字典
            added, modified, deleted = ExcelDatabase.apply_json_rules(data)

            QMessageBox.information(
                self.dialog,
                "规则应用成功",
                f"高级 JSON 规则执行完毕：\n"
                f"- 成功新增条数：{added}\n"
                f"- 成功修改条数：{modified}\n"
                f"- 成功删除条数：{deleted}"
            )

            # 刷新表格
            self.load_parsed_files()

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