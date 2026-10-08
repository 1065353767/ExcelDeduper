import os
import sys
from PySide6.QtWidgets import QMainWindow, QPushButton

class ExcelDeduper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Excel提示重复工具 - skyg Jackson.wuhan出品，请勿传播")

        self.resize(1280, 958)
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

        # 首次启动加载背景
        self.load_background()

    def load_background(self, target_name="default_bg.jpg"):
        """加载背景图，默认寻找被覆盖生成的 default_bg.jpg"""
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
        """重写窗口拉伸事件：强制保持按钮在右上角绝对位置"""
        self.btn_modify_rules.move(self.width() - 340, 20)
        self.btn_manage_files.move(self.width() - 230, 20)
        self.btn_change_bg.move(self.width() - 120, 20)

        super().resizeEvent(event)