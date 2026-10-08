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

    APP_SETTINGS_PATH = os.path.join(DATA_DIR, "settings_app.json")
    EXCEL_RULES_PATH = os.path.join(DATA_DIR, "excel_rules.json")

    # 定时器巡检间隔时间（毫秒），60000 = 1分钟
    SYNC_INTERVAL_MS = 60000

    # 修改规则的 JSON 模板示例
    DEFAULT_RULES_EXAMPLE = {
        "eg": {
            "说明：": (
                "新增和修改：新增在 add 里前面写无符号全小写公司名，后面置空；"
                "修改前面写要修改的条目，后面写修改后的内容。"
                "删除：在前面写要删除的条目并且后面置空（精确删除）。"
                "后面有值的会忽略前面，然后使用通配规则批量删除（模糊匹配）。"
            )
        },
        "add": {
            # 新增
            "shili1": "",
            # 修改（把 shili2 改为 xiugaihoumingcheng）
            "shili2": "xiugaihoumingcheng"
        },
        "del": {
            # 精确删除
            "shili3": "",
            # 通配规则批量删除（只要公司名包含该字符串即被删除）
            "shili4": "批量删除规则"
        }
    }