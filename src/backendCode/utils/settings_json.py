from src.backendCode.database.db_excel import ExcelDatabase


def dispatch_json_data(data: dict, app_settings):
    """
    分发验证 JSON 数据：
    - 将 Setting 节点拦截并更新系统配置（屏蔽空值、非法字符及越界数值）
    - 将 add/del 节点剥离（自动过滤默认模板字段）后交给数据库引擎处理
    返回 (added_count, modified_count, deleted_count, is_settings_changed)
    """
    added, modified, deleted = 0, 0, 0
    is_settings_changed = False

    # 1. 处理动态系统配置
    if "Setting" in data and isinstance(data["Setting"], dict):
        settings_node = data["Setting"]

        # 校验提示窗时间
        val_time = settings_node.get("提示窗时间")
        if val_time not in [None, ""]:
            try:
                int_time = int(val_time)
                # 只有数值在合法区间，且确实与当前内存里的值不同，才判定为有效修改
                if 0 <= int_time <= 9999 and app_settings.data.toast_duration_ms != int_time:
                    app_settings.data.toast_duration_ms = int_time
                    is_settings_changed = True
            except ValueError:
                pass

                # 校验赦免长度
        val_len = settings_node.get("赦免长度")
        if val_len not in [None, ""]:
            try:
                int_len = int(val_len)
                if 0 <= int_len <= 9999 and app_settings.data.forgive_length != int_len:
                    app_settings.data.forgive_length = int_len
                    is_settings_changed = True
            except ValueError:
                pass

        if is_settings_changed:
            app_settings.save_on_demand()

    # 2. 剥离并忽略模板默认示例内容
    template_ignore_keys = ["shili1", "shili2", "shili3", "shili4"]
    rules_data = {}

    if "add" in data and isinstance(data["add"], dict):
        add_dict = {k: v for k, v in data["add"].items() if k not in template_ignore_keys}
        if add_dict:
            rules_data["add"] = add_dict

    if "del" in data and isinstance(data["del"], dict):
        del_dict = {k: v for k, v in data["del"].items() if k not in template_ignore_keys}
        if del_dict:
            rules_data["del"] = del_dict

    # 3. 处理业务增删改规则
    if rules_data:
        added, modified, deleted = ExcelDatabase.apply_json_rules(rules_data)

    return added, modified, deleted, is_settings_changed