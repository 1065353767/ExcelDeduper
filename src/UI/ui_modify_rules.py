from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QDialog, QHeaderView, QLabel)


class Ui_ModifyRulesDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("ModifyRulesDialog")
        Dialog.resize(650, 480)
        Dialog.setWindowTitle("修改规则与数据管理")

        self.main_layout = QVBoxLayout(Dialog)

        # 1. 顶部提示与表格区
        self.lbl_title = QLabel("已解析的 Excel 文件及时间记录：", Dialog)
        self.main_layout.addWidget(self.lbl_title)

        self.table_files = QTableWidget(Dialog)
        self.table_files.setColumnCount(2)
        self.table_files.setHorizontalHeaderLabels(["Excel 文件名称", "最近解析时间"])
        self.table_files.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_files.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.main_layout.addWidget(self.table_files)

        # 2. 底部操作按钮区
        self.btn_layout = QHBoxLayout()

        self.btn_upload_json = QPushButton("上传 JSON 规则", Dialog)
        self.btn_deduplicate = QPushButton("一键数据库去重", Dialog)

        self.btn_layout.addWidget(self.btn_upload_json)
        self.btn_layout.addWidget(self.btn_deduplicate)

        self.main_layout.addLayout(self.btn_layout)


class ModifyRulesDialog(QDialog, Ui_ModifyRulesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)