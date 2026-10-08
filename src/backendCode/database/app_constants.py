import os
import sys


class AppConstants:
    """管理全局静态路径和魔法数字的常量类"""

    # 动态获取项目根目录
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # 当前文件在 src/backendCode/database/ 下，退3级到根目录
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_current_dir)))

    # 核心文件夹
    REPO_DIR = os.path.join(BASE_DIR, "Repository")
    DATA_DIR = os.path.join(REPO_DIR, "data")
    ASSETS_DIR = os.path.join(REPO_DIR, "Assets")
    EXCEL_DIR = os.path.join(BASE_DIR, "Repository", "Excel")

    # 根据你的要求，更名为 settings_app.json
    APP_SETTINGS_PATH = os.path.join(DATA_DIR, "settings_app.json")
    EXCEL_RULES_PATH = os.path.join(DATA_DIR, "excel_rules.json")

    # 定时器巡检间隔时间（毫秒），60000 = 1分钟
    SYNC_INTERVAL_MS = 60000