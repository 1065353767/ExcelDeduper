import os
import shutil
from PySide6.QtWidgets import QInputDialog, QMessageBox
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.handlers.excel_manager_handlers import ExcelManagerHandler


class MainHandlers:
    def __init__(self, ui_window, app_settings):
        self.ui = ui_window
        self.app_settings = app_settings

        # 背景字典映射
        self.bg_dict = {
            "月色海滨": "default_bg_1.jpg",
            "米色麻布": "default_bg_2.jpg",
            "科技白纸": "default_bg_3.jpg",
            "梦幻小船": "default_bg_4.jpg"
        }

        # 集中绑定所有主界面按钮事件
        self.ui.btn_modify_rules.clicked.connect(self.modify_rules)
        self.ui.btn_manage_files.clicked.connect(self.manage_files)
        self.ui.btn_change_bg.clicked.connect(self.change_background)

    def modify_rules(self):
        """修改规则按钮点击逻辑"""
        QMessageBox.information(self.ui, "提示", "修改规则功能正在接入中...")

    def manage_files(self):
        """管理文件按钮点击逻辑：唤起 Excel 管理弹窗"""
        dialog = ExcelManagerHandler(self.ui)
        dialog.exec()

    def change_background(self):
        """更换背景并即时持久化落盘"""
        items = list(self.bg_dict.keys())

        # 读取当前配置中的背景名
        current_name = self.app_settings.data.current_bg_name
        current_index = items.index(current_name) if current_name in items else 0

        selected_name, ok = QInputDialog.getItem(
            self.ui, "更换背景", "请选择你喜欢的背景：", items, current_index, False
        )

        if ok and selected_name:
            # 持久化更新
            self.app_settings.data.current_bg_name = selected_name
            self.app_settings.save_on_demand()

            source_filename = self.bg_dict[selected_name]
            assets_dir = AppConstants.ASSETS_DIR
            source_path = os.path.join(assets_dir, source_filename)

            _, ext = os.path.splitext(source_filename)
            target_filename = f"default_bg{ext}"
            target_path = os.path.join(assets_dir, target_filename)

            if os.path.exists(source_path):
                try:
                    shutil.copy2(source_path, target_path)
                    self.ui.load_background(target_filename)
                except Exception as e:
                    QMessageBox.warning(self.ui, "错误", f"背景替换失败: {e}")
            else:
                QMessageBox.warning(self.ui, "错误", "在 Assets 文件夹中找不到该图片源文件！")