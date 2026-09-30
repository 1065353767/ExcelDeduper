### 打包命令

为了确保配置文件与资源的物理隔离，我们采用“代码纯净打包 + 资源外挂拷贝”的二段组合命令。请根据你使用的终端选择对应指令：

#### Git Bash 终端（推荐）

```bash
pyinstaller -y -w -n "Excel去重工具" main.py && cp -r Repository "dist/Excel去重工具/"
```

#### PowerShell 终端

```powershell
pyinstaller -y -w -n "Excel去重工具" main.py ; Copy-Item -Path "Repository" -Destination "dist\Excel去重工具\Repository" -Recurse -Force
```

#### 命令与参数详解：

- `-y`（或 `--noconfirm`）：自动静默覆盖之前生成的打包缓存文件，不再弹窗询问。
- `-w`（或 `--windowed`）：无控制台模式。启动软件时隐藏背后的黑底 CMD 命令行窗口，提供纯净的桌面端体验。
- `-n`（或 `--name`）：指定最终生成的执行程序名称及父文件夹名称（本例中指定为 `"Excel去重工具"`）。
- `-D`（或 `--onedir`，PyInstaller 默认模式）：打包为目录模式。生成包含 `.exe` 启动器和 `_internal` 底层依赖库的文件夹。强烈推荐此架构，它避免了单文件模式（`-F`）每次运行都需要在系统临时目录解压所带来的性能损耗和本地数据丢失风险。
- 后半段复制指令（`cp` / `Copy-Item`）：打包完成后，将项目外层的 `Repository`（包含配置与资产）按原有层级完整复制到生成的 `dist/Excel去重工具/` 目录下，实现代码环境与用户数据的完美隔离。

---

### 项目树生成命令

用于快速导出项目的纯净目录结构（排除虚拟环境、缓存与编译器配置文件）：

```bash
tree -I ".venv|.idea|__pycache__|dist|build" > tree.txt
```

---

### 项目架构

#### 文件夹结构

- **UI**：仅用于存放纯页面渲染和控件布局代码（表现层）。
- **backendCode**：用于存放底层核心业务、文件读写、架构管家与算法代码（逻辑层与数据层）。

#### 命名规范

- **UI 层**：统一以 `ui_` 作为文件前缀。例如主窗口界面：`ui_main.py`。
- **Backend 层**：
    - **控制与桥接**：与特定 UI 强绑定的事件监听和状态流转逻辑，以 `_handlers` 为后缀。例如：`main_handlers.py`。
    - **纯功能与基建**：按实际功能域命名。例如：`util_json.py`（JSON 读写工具）、`app_constants.py`（全局路径魔法常量）、`core_excel.py`（Excel 处理核心算法）。