import os
import sys
from PySide6.QtWidgets import QMainWindow, QPushButton
from PySide6.QtCore import Qt, Signal


class ExcelDeduper(QMainWindow):
    # ================= 新增：自定义信号，用于向上层传递尺寸变化 =================
    window_resized_signal = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Excel提示重复工具skyg Jackson.wuhan 出品，请勿传播")

        # 移除原有的 self.resize(1280, 958)，改为统一由 Handler 从配置文件中读取赋值
        self.setMinimumSize(630, 430)

        # 实例化“修改规则”按钮
        self.btn_modify_rules = QPushButton("修改规则", self)
        self.btn_modify_rules.setFixedSize(100, 35)

        # 实例化“管理文件”按钮
        self.btn_manage_files = QPushButton("管理文件", self)
        self.btn_manage_files.setFixedSize(100, 35)

        # 实例化“更换背景”按钮
        self.btn_change_bg = QPushButton("更换背景", self)
        self.btn_change_bg.setFixedSize(100, 35)

        # 实例化中心的大按钮（默认处于暂停状态）
        self.btn_toggle_monitor = QPushButton("已暂停", self)
        self.btn_toggle_monitor.setStyleSheet("""
            QPushButton {
                border: 3px solid red; 
                font-size: 60px; 
                font-weight: bold; 
                background-color: rgba(255, 255, 255, 180);
                border-radius: 15px;
            }
        """)

        # 首次启动加载背景
        self.load_background()

    def load_background(self, target_name="default_bg.jpg"):
        """加载背景图"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(os.path.dirname(current_dir))

        img_path = os.path.join(base_path, "Repository", "Assets", target_name).replace('\\', '/')
        if not os.path.exists(img_path):
            img_path = os.path.join(base_path, "Repository", "Assets", "default_bg_1.jpg").replace('\\', '/')

        self.setStyleSheet(f"""
            #MainWindow {{
                border-image: url({img_path});
            }}
        """)

    def resizeEvent(self, event):
        """重写窗口拉伸事件：强制保持按钮在右上角绝对位置及中央按钮尺寸居中"""
        self.btn_modify_rules.move(self.width() - 340, 20)
        self.btn_manage_files.move(self.width() - 230, 20)
        self.btn_change_bg.move(self.width() - 120, 20)

        btn_w = int(self.width() * 0.5)
        btn_h = int(self.height() * 0.33)
        self.btn_toggle_monitor.setFixedSize(btn_w, btn_h)

        self.btn_toggle_monitor.move(
            int((self.width() - btn_w) / 2),
            int((self.height() - btn_h) / 2)
        )

        # ================= 新增：向外发送最新长宽数据 =================
        self.window_resized_signal.emit(self.width(), self.height())

        super().resizeEvent(event)