import os
from dataclasses import dataclass, asdict
from PySide6.QtCore import QTimer, QObject

# 导入底层工具和刚才建好的常量
from src.backendCode.utils.util_json import json2dict, dict2json
from src.backendCode.database.app_constants import AppConstants


# 1. 纯粹的数据结构 Bean，仅管理字段
@dataclass
class AppSettingsData:
    current_bg_name: str = "月色海滨"
    # 以后你想加什么全写在这，比如: window_width: int = 1280


# 2. 全局状态管家（继承 QObject 是为了能挂载 QTimer）
class SettingsManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 内存中的核心数据实体，全局唯一的单例状态源
        self.data = AppSettingsData()

        # 内部快照：记录最后一次与硬盘对齐的状态
        self._last_saved_dict = {}

        # 第一步：启动时读取硬盘，把 JSON 拉进内存
        self._load_init()

        # 第二步：启动 1 分钟一次的定时巡检
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timer_check)
        self.timer.start(AppConstants.SYNC_INTERVAL_MS)

    def _load_init(self):
        """初始化：读取本地 JSON，没有则创建默认"""
        if not os.path.exists(AppConstants.DATA_DIR):
            os.makedirs(AppConstants.DATA_DIR)

        try:
            # 调用底层纯净工具类
            loaded_dict = json2dict(AppConstants.APP_SETTINGS_PATH)

            # 将读取到的字典值，动态映射给 dataclass
            for key, value in loaded_dict.items():
                if hasattr(self.data, key):
                    setattr(self.data, key, value)
        except Exception:
            # 如果文件不存在或损坏没关系，忽略即可，最后的 demand 会去创建
            pass

        # 记录刚刚对齐的快照，并立刻全量落盘一次，确保 JSON 实体文件存在
        self.save_on_demand()

    def save_on_demand(self):
        """供其他函数即时调用的保存（入参保存动作）"""
        # @dataclass 提供的 asdict 可以一键把 Bean 转成字典
        current_dict = asdict(self.data)
        dict2json(current_dict, AppConstants.APP_SETTINGS_PATH)

        # 更新快照
        self._last_saved_dict = current_dict

    def save_on_exit(self):
        """关闭程序时调用的兜底保存"""
        self.save_on_demand()

    def _timer_check(self):
        """定时器触发：检测内存 dataclass 是否和上次保存时的快照一致"""
        current_dict = asdict(self.data)
        # 如果内存发生了我们没有及时手动调用的隐性变动，立刻落盘补救
        if current_dict != self._last_saved_dict:
            self.save_on_demand()