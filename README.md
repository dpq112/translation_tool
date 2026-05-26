# 翻译工具 (Translation Tool)

Windows 桌面翻译工具，基于 PySide6 构建。支持迷你悬浮窗和完整窗口两种模式，集成 Google / 百度翻译引擎，支持截图 OCR 翻译、剪贴板监听和历史记录。
如果不想了解代码只想使用该工具，可以直接下载dist目录下面的TranslationTool.exe文件，双击即可在任务栏或者隐藏的图标中看到该工具已经启动。

## 功能亮点

- **迷你悬浮窗** — 无边框置顶窗口，输入即翻，适合边看资料边翻译
- **截图翻译** — 框选屏幕任意区域，OCR 识别后自动翻译
- **多引擎** — Google 翻译（免费、无需配置）+ 百度翻译（需 API Key）
- **剪贴板监听** — 复制即翻译，自动填入迷你窗口
- **历史记录** — 翻译自动存档，支持搜索，超过 3 天自动清理
- **全局快捷键** — 系统级热键，任何界面都可触发

## 安装

```bash
# 克隆仓库
git clone https://github.com/dpq112/translation_tool.git
cd translation_tool

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# 安装依赖
pip install PySide6 deep-translator requests pillow
```

## 使用

```bash
python main.py
```

启动后系统托盘出现「译」图标，右键展开菜单。

### 默认快捷键

| 功能 | 快捷键 | 说明 |
|---|---|---|
| 迷你翻译窗口 | `Ctrl + Shift + Q` | 显示 / 隐藏悬浮窗 |
| 完整翻译窗口 | `Ctrl + Shift + W` | 打开标准窗口 |
| 截图翻译 | `Ctrl + Shift + E` | 框选屏幕区域进行 OCR 翻译 |

### 迷你窗口操作

- **拖拽** — 拖动标题栏移动位置
- **📌** — 切换置顶 / 取消置顶
- **─** — 最小化到任务栏
- **⚙** — 打开设置
- **✕** — 关闭窗口

### 截图翻译流程

1. 按下 `Ctrl + Shift + E`（或托盘菜单选择「截图翻译」）
2. 鼠标拖拽框选需要翻译的区域
3. 松开鼠标 → OCR 识别 → 自动填入迷你窗口并翻译
4. ESC 或右键取消

> 截图翻译需要配置百度 OCR API Key（在 ai.baidu.com 开通「通用文字识别」服务后获取）

### 翻译引擎配置

- **Google 翻译**：免费，无需配置，开箱即用
- **百度翻译**：在 fanyi-api.baidu.com 注册获取 APP ID 和密钥，设置中填入后测试连接

## 快捷键冲突检测

修改快捷键时自动检测与系统其他程序的冲突，冲突时拒绝修改并提示。启动时如有快捷键注册失败，托盘会弹出具体信息。

## 数据存储

- 配置：`%APPDATA%/TranslationTool/config.json`
- 历史：`%APPDATA%/TranslationTool/history.json`（目录可在设置中自定义）

## 依赖

| 包 | 用途 |
|---|---|
| PySide6 | Qt 桌面框架 |
| deep-translator | Google 翻译 |
| requests | 百度 API 调用 |
| pillow | 截图图像处理 |

## 许可

MIT License
