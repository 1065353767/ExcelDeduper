from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout

from src.backendCode.database.app_constants import AppConstants


class FloatingToast(QWidget):
    # ================= 新增 duration_ms 参数 =================
    def __init__(self, text, is_exist=False, duration_ms=3000):
        super().__init__()

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
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_exist:
            bg_color = "#87CEEB"
        else:
            bg_color = "#f44336"

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

        if not is_exist:
            # ================= 使用动态时间 =================
            QTimer.singleShot(duration_ms, self.close)

    def mousePressEvent(self, event):
        self.close()
        super().mousePressEvent(event)