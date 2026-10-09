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

    # ================= 修改：全球化及货代行业常见公司后缀字典集 =================
    # 严格按照字符串长度降序排列（无符号、全小写格式）
    COMPANY_SUFFIXES = (
        "incorporated",
        "corporation",
        "forwarding",
        "logistics",
        "集团股份有限公司", "集团有限责任公司", "股份有限责任公司", "科技股份有限公司", "services",
        "spolsro", "limited", "company",
        "sadecv", "ptyltd", "集团有限公司", "控股有限公司", "实业有限公司", "商贸有限公司", "贸易有限公司",
        "发展有限公司", "个人独资企业",
        "spzoo", "coltd", "group", "专业合作社",
        "ltda", "gmbh", "corp", "sarl", "合伙企业", "责任公司", "股份公司", "集团公司", "控股公司", "有限公司",
        "sia", "spa", "sas", "doo", "sro", "inc", "llc", "ltd", "plc", "ulc", "llp", "总公司", "分公司", "子公司",
        "大药房", "经营部", "营业部", "服务部", "工作室", "办事处", "代表处", "俱乐部",
        "as", "ag", "sa", "nv", "bv", "co", "集团", "公司", "中心", "商行", "门店", "工厂",
        "厂", "店", "行", "网", "站", "部", "局"
    )
    # ================================================================

    # ================= 修改规则模板 =================
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
    # ================================================================