### 1. 项目树生成命令

用于快速导出项目的纯净物理目录结构（自动排除虚拟环境、打包缓存及 IDE 配置文件）：

```bash
tree -I ".venv|.idea|__pycache__|dist|build" > tree.txt
```

---

### 2. 打包命令

为解决 `src` 目录作为源目录时的相对导包报错问题，已在命令中加入 `-p src` 寻址参数。同时采用“代码纯净打包 +
资源外挂拷贝”模式。请根据终端环境选择对应指令：

**Git Bash 终端（推荐）**

```bash
pyinstaller -y -w -i "Repository/Assets/skyico.ico" -n "Excel提示重复工具_v1.0" main.py && cp -r Repository "dist/Excel提示重复工具_v1.0/"
```

**PowerShell 终端**

```powershell
pyinstaller -y -w -i "Repository/Assets/skyico.ico" -n "Excel提示重复工具_v1.0" main.py ; Copy-Item -Path "Repository" -Destination "dist\Excel提示重复工具_v1.0\Repository" -Recurse -Force
```

**核心参数说明：**

- `-y`：静默覆盖历史打包缓存。
- `-w`：无控制台模式（隐藏背后的 CMD 黑框）。
- `-p src`：将 `src` 目录加入检索路径，解决 `backendCode` 等模块找不到的导包异常。
- `-i`：指定打包后的静态可执行文件（`.exe`）图标路径。
- `-n`：指定生成的执行程序及输出文件夹名称。
- `cp / Copy-Item`：打包完成后，将静态资源池完整复制到 `dist` 输出目录中。

---

### 3. 项目架构与规范

项目采用严格的 MVC 分层设计，核心业务（Backend）、表现层（UI）与外部资源（Repository）完全解耦。

#### 文件夹功能说明

- **Repository**：静态资源池。存放不参与代码编译的外部挂载文件，如背景图、ICO 图标（`Assets`）、Excel 源文件（`Excel`
  ）以及持久化配置与规则（`data`）。
- **src/UI**：表现层。仅存放纯页面渲染、控件布局代码及自绘组件（如 Toast 悬浮窗）。
- **src/backendCode**：逻辑与数据层。存放底层核心业务、架构管家与算法代码。
    - `database`：负责 SQLite 数据读写、JSON 配置文件加载以及全局常量定义。
    - `handlers`：控制器。负责接收 UI 层传递的事件，进行业务调度与状态流转。
    - `tasks`：任务层。封装具体的业务处理算法（如公司名称的正则清洗与比对）。
    - `utils`：工具层。存放不带业务状态的纯底层通用方法。

#### 命名规范

- **UI 层**：统一以 `ui_` 作为文件前缀（例：`ui_main.py`）。
- **控制器**：与特定 UI 强绑定的事件逻辑，以 `_handlers` 为后缀（例：`main_handlers.py`）。
- **通用功能**：按实际职责前缀命名，不掺杂多余修饰（例：`util_json.py`、`task_excel.py`、`db_excel.py`）。