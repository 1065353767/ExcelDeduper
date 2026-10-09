import os
from dataclasses import dataclass, asdict

from PySide6.QtCore import QTimer, QObject

from src.backendCode.database.app_constants import AppConstants
from src.backendCode.utils.util_json import json2dict, dict2json


# 1. 纯粹的数据结构 Bean，仅管理字段
@dataclass
class AppSettingsData:
    current_bg_name: str = "月色海滨"
    window_width: int = 1280
    window_height: int = 958

    # ================= 新增：接管原 Constants 中的动态业务参数 =================
    toast_duration_ms: int = 3000  # 提示窗时间
    forgive_length: int = 3  # 赦免长度
    # =========================================================================


# 2. 全局状态管家
class SettingsManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = AppSettingsData()
        self._last_saved_dict = {}

        self._load_init()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timer_check)
        self.timer.start(AppConstants.SYNC_INTERVAL_MS)

    def _load_init(self):
        if not os.path.exists(AppConstants.DATA_DIR):
            os.makedirs(AppConstants.DATA_DIR)

        try:
            loaded_dict = json2dict(AppConstants.APP_SETTINGS_PATH)
            for key, value in loaded_dict.items():
                if hasattr(self.data, key):
                    setattr(self.data, key, value)
        except Exception:
            pass

        self.save_on_demand()

    def save_on_demand(self):
        current_dict = asdict(self.data)
        dict2json(current_dict, AppConstants.APP_SETTINGS_PATH)
        self._last_saved_dict = current_dict

    def save_on_exit(self):
        self.save_on_demand()

    def _timer_check(self):
        current_dict = asdict(self.data)
        if current_dict != self._last_saved_dict:
            self.save_on_demand()