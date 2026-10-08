from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QSpacerItem, QSizePolicy, QListWidget,
                               QWidget, QLabel, QListWidgetItem, QDialog, QLineEdit)


class Ui_ExcelManagerDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("ExcelManagerDialog")
        Dialog.resize(600, 450)
        Dialog.setWindowTitle("管理文件 (Excel)")

        self.main_layout = QVBoxLayout(Dialog)

        # 1. 顶部操作区
        self.top_layout = QHBoxLayout()
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.top_layout.addItem(self.spacer)

        self.btn_upload = QPushButton("上传", Dialog)
        self.btn_upload.setMinimumWidth(80)
        self.top_layout.addWidget(self.btn_upload)
        self.main_layout.addLayout(self.top_layout)

        # 2. 下方列表展示区
        self.list_excel = QListWidget(Dialog)
        self.main_layout.addWidget(self.list_excel)

    def draw_excel_item(self, file_name):
        """只负责“画”出带有【解析】按钮的一行，并将按钮移交控制层绑定"""
        item = QListWidgetItem(self.list_excel)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 2, 5, 2)

        lbl_name = QLabel(file_name)
        row_layout.addWidget(lbl_name)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        row_layout.addItem(spacer)

        btn_parse = QPushButton("解析")
        btn_parse.setFixedSize(60, 26)
        row_layout.addWidget(btn_parse)

        item.setSizeHint(row_widget.sizeHint())
        self.list_excel.setItemWidget(item, row_widget)

        return btn_parse


class ColumnInputDialog(QDialog):
    """新增：专门用于输入列号的弹窗 UI 类"""
    def __init__(self, file_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入解析列")
        self.resize(350, 160)

        layout = QVBoxLayout(self)

        self.lbl_tip = QLabel(f"当前文件: {file_name}\n请输入要解析的列字母 (支持多列，用逗号隔开，例如: a,b)：")
        layout.addWidget(self.lbl_tip)

        self.input_cols = QLineEdit(self)
        self.input_cols.setPlaceholderText("例如: a,b")
        layout.addWidget(self.input_cols)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定", self)
        self.btn_cancel = QPushButton("取消", self)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        # 信号槽绑定
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_column_input(self):
        """获取用户输入的列号字符串"""
        return self.input_cols.text().strip()