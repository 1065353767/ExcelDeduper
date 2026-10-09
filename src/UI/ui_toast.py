from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout

from src.backendCode.database.app_constants import AppConstants


class FloatingToast(QWidget):
    def __init__(self, text, is_exist=False):
        super().__init__()

        # 无边框 | 置顶 | 工具窗口(不显示在任务栏) | 鼠标穿透（关闭穿透以便接收点击）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(AppConstants.TOAST_OPACITY)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(text, self)

        # =============== 新增/修改：强制开启 HTML 富文本解析 ===============
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 存在给天蓝色，不存在给红色
        if is_exist:
            bg_color = "#87CEEB"  # 天蓝色
        else:
            bg_color = "#f44336"  # 红色

        self.label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }}
        """)

        layout.addWidget(self.label)

        # 如果未命中，设定 3000ms 后自动关闭；命中则不开启定时器，持续显示
        if not is_exist:
            QTimer.singleShot(AppConstants.TOAST_DURATION_NOT_FOUND_MS, self.close)

    def mousePressEvent(self, event):
        """重写鼠标点击事件：用户点击提示框任意位置即可销毁它"""
        self.close()
        super().mousePressEvent(event)
