import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalSocket, QLocalServer

from src.UI.ui_main import ExcelDeduper
from src.backendCode.database.settings_app import SettingsManager
from src.backendCode.handlers.main_handlers import MainHandlers

if __name__ == "__main__":
    # ================= 新增：IPC 单例互斥锁防多开 =================
    ipc_server_name = "ExcelDeduper_IPC_Lock"
    socket = QLocalSocket()
    socket.connectToServer(ipc_server_name)

    # 如果能连上，说明已经有进程在运行
    if socket.waitForConnected(500):
        socket.write(b"WAKEUP")
        socket.flush()
        socket.waitForBytesWritten(500)
        socket.close()
        sys.exit(0)  # 发送完唤醒指令后，本进程静默退出
    # ==========================================================

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)

    # 防止主窗口隐藏后程序自动退出
    app.setQuitOnLastWindowClosed(False)

    # 1. 实例化配置管家
    app_settings = SettingsManager()
    app.aboutToQuit.connect(app_settings.save_on_exit)

    # 2. 实例化主界面窗口与事件控制器
    window = ExcelDeduper()
    handler = MainHandlers(window, app_settings)

    # ================= 新增：建立本地服务监听唤醒 =================
    QLocalServer.removeServer(ipc_server_name)  # 防崩溃残留兜底
    server = QLocalServer()
    server.listen(ipc_server_name)


    def on_new_connection():
        client = server.nextPendingConnection()
        if client:
            client.waitForReadyRead(500)
            msg = client.readAll().data().decode('utf-8')
            if msg == "WAKEUP":
                handler.show_main_window()  # 唤醒置顶
            client.disconnectFromServer()


    server.newConnection.connect(on_new_connection)
    # ==========================================================

    window.show()
    sys.exit(app.exec())