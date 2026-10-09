from src.backendCode.database.db_excel import ExcelDatabase

def dispatch_json_data(data: dict, app_settings):
    """
    分发验证 JSON 数据：
    - 将 Setting 节点拦截并更新系统配置（屏蔽空值、非法字符及越界数值）
    - 将 add/del 节点剥离后交给数据库引擎处理
    返回 (added_count, modified_count, deleted_count)
    """
    added, modified, deleted = 0, 0, 0

    # 1. 处理动态系统配置
    if "Setting" in data and isinstance(data["Setting"], dict):
        settings_node = data["Setting"]
        is_settings_changed = False

        # 校验提示窗时间：剔除 None 和 空字符串，并限制范围 0-9999
        val_time = settings_node.get("提示窗时间")
        if val_time not in [None, ""]:
            try:
                int_time = int(val_time)
                if 0 <= int_time <= 9999:
                    app_settings.data.toast_duration_ms = int_time
                    is_settings_changed = True
            except ValueError:
                pass  # 忽略乱码或非法字符串

        # 校验赦免长度：剔除 None 和 空字符串，并限制范围 0-9999
        val_len = settings_node.get("赦免长度")
        if val_len not in [None, ""]:
            try:
                int_len = int(val_len)
                if 0 <= int_len <= 9999:
                    app_settings.data.forgive_length = int_len
                    is_settings_changed = True
            except ValueError:
                pass

        if is_settings_changed:
            app_settings.save_on_demand()

    # 2. 处理业务增删改规则
    rules_data = {}
    if "add" in data:
        rules_data["add"] = data["add"]
    if "del" in data:
        rules_data["del"] = data["del"]

    if rules_data:
        added, modified, deleted = ExcelDatabase.apply_json_rules(rules_data)

    return added, modified, deleted