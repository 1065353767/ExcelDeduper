import os
import shutil
from PySide6.QtWidgets import QInputDialog, QMessageBox
from src.backendCode.database.app_constants import AppConstants  # 新增：导入常量Bean

class MainHandlers:
    def __init__(self, ui_window, app_settings): # 接收注入的单例
        self.ui = ui_window
        self.app_settings = app_settings # 挂载到实例上供全局方法调用

        # 建立字典映射（展示给用户看的中文名 -> 实际文件名）
        self.bg_dict = {
            "月色海滨": "default_bg_1.jpg",
            "米色麻布": "default_bg_2.jpg",
            "科技白纸": "default_bg_3.jpg"
        }

        # 完全对齐 UI 中的变量名
        self.ui.btn_modify_rules.clicked.connect(self.modify_rules)
        self.ui.btn_manage_files.clicked.connect(self.manage_files)
        self.ui.btn_change_bg.clicked.connect(self.change_background)

    def modify_rules(self):
        """
        修改规则
        """
        pass

    def manage_files(self):
        """
        管理文件
        """
        pass

    def change_background(self):
        """
        更换背景
        """
        # 1. 提取字典所有的中文名作为下拉列表
        items = list(self.bg_dict.keys())

        # 2. 从管家内存中读取当前背景名，换算成给插件的序号(index)
        current_name = self.app_settings.data.current_bg_name
        current_index = items.index(current_name) if current_name in items else 0

        # 3. 呼出自带的下拉选择弹窗，传入 current_index 保证默认选中项正确
        selected_name, ok = QInputDialog.getItem(
            self.ui, "更换背景", "请选择你喜欢的背景：", items, current_index, False
        )

        # 4. 用户点击了确认，且选择了有效项
        if ok and selected_name:
            # ---- 核心新增：持久化状态更新 ----
            self.app_settings.data.current_bg_name = selected_name
            self.app_settings.save_on_demand() # 即时落盘
            # --------------------------------

            source_filename = self.bg_dict[selected_name]

            # 【已优化】彻底干掉原来一长串计算 sys.frozen 的代码，直接调用常量 Bean
            assets_dir = AppConstants.ASSETS_DIR
            source_path = os.path.join(assets_dir, source_filename)

            # 提取原图后缀（比如 .jpg），并拼装新的目标文件名
            _, ext = os.path.splitext(source_filename)
            target_filename = f"default_bg{ext}"
            target_path = os.path.join(assets_dir, target_filename)

            # 5. 执行复制并覆盖，然后通知 UI 刷新
            if os.path.exists(source_path):
                try:
                    # copy2 会连同文件的元数据一起复制过去，强制覆盖同名文件
                    shutil.copy2(source_path, target_path)

                    # 重新加载背景图，让新背景立刻生效
                    self.ui.load_background(target_filename)
                except Exception as e:
                    QMessageBox.warning(self.ui, "错误", f"背景替换失败: {e}")
            else:
                QMessageBox.warning(self.ui, "错误", "在 Assets 文件夹中找不到该图片源文件！")