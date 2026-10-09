from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QDialog, QHeaderView, QLabel, QSpacerItem, QSizePolicy)


class Ui_ModifyRulesDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("ModifyRulesDialog")
        Dialog.resize(680, 480)
        Dialog.setWindowTitle("修改规则与数据管理")

        self.main_layout = QVBoxLayout(Dialog)

        # 1. 顶部区域：左侧标题标签，中间弹簧，右侧“一键数据库去重”按钮
        self.top_bar_layout = QHBoxLayout()
        self.lbl_title = QLabel("已解析的 Excel 文件及时间记录：", Dialog)
        self.top_bar_layout.addWidget(self.lbl_title)

        self.spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.top_bar_layout.addItem(self.spacer)

        self.btn_deduplicate = QPushButton("一键数据库去重", Dialog)
        self.top_bar_layout.addWidget(self.btn_deduplicate)

        self.main_layout.addLayout(self.top_bar_layout)

        # 表格展示区
        self.table_files = QTableWidget(Dialog)
        self.table_files.setColumnCount(2)
        self.table_files.setHorizontalHeaderLabels(["Excel 文件名称", "最近解析时间"])
        self.table_files.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_files.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.main_layout.addWidget(self.table_files)

        # 2. 底部操作按钮区：“上传 JSON 规则”与“下载模板”
        self.btn_layout = QHBoxLayout()

        self.btn_upload_json = QPushButton("上传 JSON 规则", Dialog)
        self.btn_download_template = QPushButton("下载模板", Dialog)

        self.btn_layout.addWidget(self.btn_upload_json)
        self.btn_layout.addWidget(self.btn_download_template)

        self.main_layout.addLayout(self.btn_layout)


class ModifyRulesDialog(QDialog, Ui_ModifyRulesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)