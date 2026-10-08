import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.UI.ui_main import ExcelDeduper
from src.backendCode.handlers.main_handlers import MainHandlers
from src.backendCode.database.settings_app import SettingsManager

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    # 1. 实例化顶层单例配置管家
    app_settings = SettingsManager()

    # 2. 将管家的兜底保存绑定到程序的退出信号上（关闭保存）
    app.aboutToQuit.connect(app_settings.save_on_exit)

    # 2. 实例化主界面窗口
    window = ExcelDeduper()

    # 3. 实例化主事件控制器，完成依赖注入
    handler = MainHandlers(window, app_settings)

    window.show()
    sys.exit(app.exec())