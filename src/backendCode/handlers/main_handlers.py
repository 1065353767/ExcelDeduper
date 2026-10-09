import os
import shutil

from PySide6.QtGui import QCursor, QAction, QIcon
from PySide6.QtWidgets import QInputDialog, QMessageBox, QApplication, QSystemTrayIcon, QMenu, QStyle

from src.UI.ui_toast import FloatingToast
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.database.db_excel import ExcelDatabase
from src.backendCode.handlers.excel_manager_handlers import ExcelManagerHandler
from src.backendCode.handlers.modify_rules_handlers import ModifyRulesHandler
from src.backendCode.tasks.task_excel import ExcelTask


class MainHandlers:
    def __init__(self, ui_window, app_settings):
        self.ui = ui_window
        self.app_settings = app_settings

        self.ui.resize(self.app_settings.data.window_width, self.app_settings.data.window_height)

        self.is_monitoring = False
        self.current_toast = None

        self.bg_dict = {
            "月色海滨": "default_bg_1.jpg",
            "米色麻布": "default_bg_2.jpg",
            "科技白纸": "default_bg_3.jpg",
            "梦幻小船": "default_bg_4.jpg"
        }

        self.ui.btn_modify_rules.clicked.connect(self.modify_rules)
        self.ui.btn_manage_files.clicked.connect(self.manage_files)
        self.ui.btn_change_bg.clicked.connect(self.change_background)
        self.ui.btn_toggle_monitor.clicked.connect(self.toggle_monitor)

        QApplication.clipboard().dataChanged.connect(self.on_clipboard_changed)
        self.ui.window_resized_signal.connect(self.on_window_resized)

        self.setup_tray_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self.ui)
        icon_path = os.path.join(AppConstants.ASSETS_DIR, "skypng.png")

        if os.path.exists(icon_path):
            custom_icon = QIcon(icon_path)
            self.tray_icon.setIcon(custom_icon)
            self.ui.setWindowIcon(custom_icon)
        else:
            fallback_icon = self.ui.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(fallback_icon)
            self.ui.setWindowIcon(fallback_icon)

        self.tray_icon.setToolTip(f"Excel去重工具 {AppConstants.APP_VERSION}")

        tray_menu = QMenu()
        show_action = QAction("显示主界面", self.ui)
        quit_action = QAction("完全退出", self.ui)

        show_action.triggered.connect(self.show_main_window)
        quit_action.triggered.connect(self.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def show_main_window(self):
        self.ui.show()
        # 将窗口强制推到前台，应对 IPC 唤醒
        self.ui.setWindowState(self.ui.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.ui.activateWindow()

    def quit_app(self):
        self.ui.real_quit = True
        QApplication.quit()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()

    def on_window_resized(self, w, h):
        self.app_settings.data.window_width = w
        self.app_settings.data.window_height = h

    def toggle_monitor(self):
        self.is_monitoring = not self.is_monitoring

        if self.is_monitoring:
            self.ui.btn_toggle_monitor.setText("已开启")
            self.ui.btn_toggle_monitor.setStyleSheet("""
                QPushButton {
                    border: 3px solid green; 
                    color: green;
                    font-size: 60px; 
                    font-weight: bold; 
                    background-color: rgba(255, 255, 255, 180);
                    border-radius: 15px;
                }
            """)
        else:
            self.ui.btn_toggle_monitor.setText("已暂停")
            self.ui.btn_toggle_monitor.setStyleSheet("""
                QPushButton {
                    border: 3px solid red; 
                    color: red;
                    font-size: 60px; 
                    font-weight: bold; 
                    background-color: rgba(255, 255, 255, 180);
                    border-radius: 15px;
                }
            """)

    def on_clipboard_changed(self):
        if not self.is_monitoring:
            return

        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            return

        clean_text = ExcelTask.clean_company_name(text)
        if not clean_text:
            return

        matches = ExcelDatabase.find_matching_companies(
            clean_text,
            tolerance=self.app_settings.data.forgive_length  # 动态注入赦免长度
        )
        is_exist = len(matches) > 0

        if is_exist:
            match_str_list = []
            display_clean_text = clean_text

            for m in matches[:10]:
                if clean_text in m:
                    h_m = m.replace(clean_text, f"<font color='red'>{clean_text}</font>")
                    display_clean_text = f"<font color='red'>{clean_text}</font>"
                elif m in clean_text:
                    h_m = f"<font color='red'>{m}</font>"
                    if "<font" not in display_clean_text:
                        display_clean_text = display_clean_text.replace(m, f"<font color='red'>{m}</font>")
                else:
                    h_m = m

                match_str_list.append(f"- {h_m}")

            match_str = "<br>".join(match_str_list)
            if len(matches) > 10:
                match_str += f"<br>...等共计 {len(matches)} 项命中"

            display_text = f"【已开发】<br>您复制: {display_clean_text}<br>命中列表:<br>{match_str}"
        else:
            display_text = f"【未开发】<br>您复制: {clean_text}"

        if self.current_toast:
            self.current_toast.close()

        self.current_toast = FloatingToast(
            display_text,
            is_exist=is_exist,
            duration_ms=self.app_settings.data.toast_duration_ms  # 动态注入提示窗时间
        )
        pos = QCursor.pos()
        self.current_toast.move(pos.x() + 20, pos.y() + 20)
        self.current_toast.show()

    def modify_rules(self):
        # 传递 app_settings 给规则管理模块
        dialog_handler = ModifyRulesHandler(self.ui, self.app_settings)
        dialog_handler.exec()

    def manage_files(self):
        dialog = ExcelManagerHandler(self.ui)
        dialog.exec()

    def change_background(self):
        items = list(self.bg_dict.keys())
        current_name = self.app_settings.data.current_bg_name
        current_index = items.index(current_name) if current_name in items else 0

        selected_name, ok = QInputDialog.getItem(
            self.ui, "更换背景", "请选择你喜欢的背景：", items, current_index, False
        )

        if ok and selected_name:
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