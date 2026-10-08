import os
import shutil
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from src.UI.ui_excel_manager import Ui_ExcelManagerDialog, ColumnInputDialog  # 引入 UI 弹窗类
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.tasks.task_excel import ExcelTask


class ExcelManagerHandler(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ExcelManagerDialog()
        self.ui.setupUi(self)

        self.ui.btn_upload.clicked.connect(self.upload_excel)
        self.load_existing_excel_files()

    def load_existing_excel_files(self):
        """读取目录，并调度 UI 画出行列表并绑定解析事件"""
        self.ui.list_excel.clear()

        target_dir = AppConstants.EXCEL_DIR
        if not os.path.exists(target_dir):
            return

        all_files = os.listdir(target_dir)

        for file_name in all_files:
            if not file_name.startswith("~$") and file_name.endswith(('.xlsx', '.xls')):
                btn_parse = self.ui.draw_excel_item(file_name)
                btn_parse.clicked.connect(lambda checked=False, f=file_name: self.parse_excel(f))

    def parse_excel(self, file_name):
        """
        按钮触发方法：只负责拉起 UI 弹窗，并将获取到的路径与列号交由 Task 层解析
        """
        excel_path = os.path.join(AppConstants.EXCEL_DIR, file_name)

        # 1. 实例化 UI 层定义的列输入弹窗
        dialog = ColumnInputDialog(file_name, self)

        # 2. 如果用户点击了确定
        if dialog.exec() == QDialog.Accepted:
            cols_input = dialog.get_column_input()
            if not cols_input:
                return

            try:
                # 3. 委派给任务层解析清洗并入库
                count = ExcelTask.execute_task(file_name, excel_path, cols_input)

                QMessageBox.information(
                    self,
                    "解析成功",
                    f"成功清洗并导入 {count} 条唯一公司名称至本地数据库！"
                )

            except Exception as e:
                QMessageBox.critical(self, "解析错误", f"解析 Excel 失败: {str(e)}")

    def upload_excel(self):
        target_dir = AppConstants.EXCEL_DIR
        os.makedirs(target_dir, exist_ok=True)

        files, _ = QFileDialog.getOpenFileNames(
            self, "选择要导入的 Excel 文件", target_dir, "Excel Files (*.xlsx *.xls)"
        )

        if not files:
            return

        success_count = 0
        for file_path in files:
            file_name = os.path.basename(file_path)
            target_path = os.path.join(target_dir, file_name)

            try:
                if os.path.normpath(file_path) == os.path.normpath(target_path):
                    continue
                shutil.copy2(file_path, target_path)
                success_count += 1
            except Exception as e:
                print(f"文件 {file_name} 复制失败: {e}")

        if success_count > 0:
            QMessageBox.information(self, "导入成功", f"成功将 {success_count} 个文件导入至本地仓库！")
            self.load_existing_excel_files()