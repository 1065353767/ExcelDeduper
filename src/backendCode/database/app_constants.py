import os
import sys

class AppConstants:
    """管理全局静态路径和魔法数字的常量类"""

    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_current_dir)))

    REPO_DIR = os.path.join(BASE_DIR, "Repository")
    DATA_DIR = os.path.join(REPO_DIR, "data")
    ASSETS_DIR = os.path.join(REPO_DIR, "Assets")
    EXCEL_DIR = os.path.join(BASE_DIR, "Repository", "Excel")

    APP_SETTINGS_PATH = os.path.join(DATA_DIR, "settings_app.json")
    EXCEL_RULES_PATH = os.path.join(DATA_DIR, "excel_rules.json")

    SYNC_INTERVAL_MS = 60000

    TOAST_OPACITY = 0.6
    TOAST_DURATION_NOT_FOUND_MS = 3000

    # ================= 新增 =================
    # 匹配宽容值：允许的字符串长度最大差值。
    # 设为3时，复制"a"(长度1)，库中的"abcd"(长度4，差值3)会命中，"abcde"(长度5，差值4)会被剔除。
    MATCH_LENGTH_TOLERANCE = 3
    # ========================================

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
            "shili1": "",
            "shili2": "xiugaihoumingcheng"
        },
        "del": {
            "shili3": "",
            "shili4": "批量删除规则"
        }
    }