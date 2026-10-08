import os
import shutil
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from src.UI.ui_excel_manager import Ui_ExcelManagerDialog
from src.backendCode.database.app_constants import AppConstants


class ExcelManagerHandler(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ExcelManagerDialog()
        self.ui.setupUi(self)

        self.ui.btn_upload.clicked.connect(self.upload_excel)

        # 初始化时读取列表
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
                # 1. 调度 UI 层画出这一行，并接手返回的按钮实例
                btn_parse = self.ui.draw_excel_item(file_name)

                # 2. 在控制层给拿到的按钮通电。使用 lambda 闭包锁定当前的 file_name
                btn_parse.clicked.connect(lambda checked=False, f=file_name: self.parse_excel(f))

    def parse_excel(self, file_name):
        """
        点击解析按钮的具体执行逻辑
        """
        QMessageBox.information(self, "解析测试", f"准备解析文件：\n{file_name}")
        pass

    def upload_excel(self):
        # 拿到绝对路径并确保目录存在
        target_dir = AppConstants.EXCEL_DIR
        os.makedirs(target_dir, exist_ok=True)

        # 唤起系统选择框，默认定位到 target_dir
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择要导入的 Excel 文件",
            target_dir,
            "Excel Files (*.xlsx *.xls)"
        )

        if not files:
            return

        success_count = 0
        for file_path in files:
            file_name = os.path.basename(file_path)
            target_path = os.path.join(target_dir, file_name)

            try:
                # 防止用户在 Repository/Excel 里选了文件又传给它自己
                if os.path.normpath(file_path) == os.path.normpath(target_path):
                    continue

                shutil.copy2(file_path, target_path)
                success_count += 1
            except Exception as e:
                print(f"文件 {file_name} 复制失败: {e}")

        if success_count > 0:
            QMessageBox.information(self, "导入成功", f"成功将 {success_count} 个文件导入至本地仓库！")
            self.load_existing_excel_files()