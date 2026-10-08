from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QSpacerItem, QSizePolicy, QListWidget,
                               QWidget, QLabel, QListWidgetItem)


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
        """
        新增：只负责“画”出带有【解析】按钮的一行，并将按钮移交控制层绑定
        """
        # 1. 生成一个空的占位 Item
        item = QListWidgetItem(self.list_excel)

        # 2. 画一个水平布局的行容器
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 2, 5, 2)  # 把上下边距缩小一点，让列表紧凑

        # 3. 左侧画：文件名
        lbl_name = QLabel(file_name)
        row_layout.addWidget(lbl_name)

        # 4. 中间画：弹簧（把按钮挤到最右边）
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        row_layout.addItem(spacer)

        # 5. 右侧画：解析按钮
        btn_parse = QPushButton("解析")
        btn_parse.setFixedSize(60, 26)
        row_layout.addWidget(btn_parse)

        # 6. 把画好的行容器镶嵌进列表的空 Item 里
        item.setSizeHint(row_widget.sizeHint())
        self.list_excel.setItemWidget(item, row_widget)

        # 7. 核心：把画好的按钮扔给外部（控制层）去绑定事件
        return btn_parse