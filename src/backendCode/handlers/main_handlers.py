import os
import shutil
from PySide6.QtWidgets import QInputDialog, QMessageBox, QApplication
from PySide6.QtGui import QCursor
from src.backendCode.database.app_constants import AppConstants
from src.backendCode.handlers.excel_manager_handlers import ExcelManagerHandler
from src.backendCode.handlers.modify_rules_handlers import ModifyRulesHandler  # 引入修改规则 Handler
from src.backendCode.tasks.task_excel import ExcelTask
from src.backendCode.database.db_excel import ExcelDatabase
from src.UI.ui_toast import FloatingToast


class MainHandlers:
    def __init__(self, ui_window, app_settings):
        self.ui = ui_window
        self.app_settings = app_settings

        # 监控状态锁
        self.is_monitoring = False
        self.current_toast = None  # 持有悬浮窗的引用，防止被垃圾回收

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

        # 绑定中间大按钮切换事件
        self.ui.btn_toggle_monitor.clicked.connect(self.toggle_monitor)

        # 绑定剪贴板变化信号
        QApplication.clipboard().dataChanged.connect(self.on_clipboard_changed)

    def toggle_monitor(self):
        """中间大按钮点击：翻转监控状态及UI"""
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

        # === 替换 main_handlers.py 里面的 on_clipboard_changed 方法 ===

    def on_clipboard_changed(self):
        """剪贴板内容变更时的触发动作"""
        if not self.is_monitoring:
            return

        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            return

        clean_text = ExcelTask.clean_company_name(text)

        if not clean_text:
            return

        matches = ExcelDatabase.find_matching_companies(clean_text)
        is_exist = len(matches) > 0

        if is_exist:
            match_str_list = []
            display_clean_text = clean_text  # 用于展示的剪贴板内容

            for m in matches[:10]:
                if clean_text in m:
                    # 库里的词比剪贴板长，把库数据中被剪贴板包含的部分标红
                    h_m = m.replace(clean_text, f"<font color='red'>{clean_text}</font>")
                    # 剪贴板全词命中，剪贴板展示区全红
                    display_clean_text = f"<font color='red'>{clean_text}</font>"
                elif m in clean_text:
                    # 剪贴板的词比库里长，库里的词就是相同部分，全标红
                    h_m = f"<font color='red'>{m}</font>"
                    # 顺便把剪贴板展示文字里相同的部分也标红（防冲突校验）
                    if "<font" not in display_clean_text:
                        display_clean_text = display_clean_text.replace(m, f"<font color='red'>{m}</font>")
                else:
                    h_m = m

                match_str_list.append(f"- {h_m}")

            match_str = "<br>".join(match_str_list)
            if len(matches) > 10:
                match_str += f"<br>...等共计 {len(matches)} 项命中"

            # HTML 模式下必须使用 <br> 替代 \n
            display_text = f"【已开发】<br>您复制: {display_clean_text}<br>命中列表:<br>{match_str}"
        else:
            display_text = f"【未开发】<br>您复制: {clean_text}"

        if self.current_toast:
            self.current_toast.close()

        self.current_toast = FloatingToast(display_text, is_exist=is_exist)

        pos = QCursor.pos()
        self.current_toast.move(pos.x() + 20, pos.y() + 20)
        self.current_toast.show()

    def modify_rules(self):
        """修改规则按钮点击逻辑：唤起修改规则与数据管理弹窗"""
        dialog_handler = ModifyRulesHandler(self.ui)
        dialog_handler.exec()

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
