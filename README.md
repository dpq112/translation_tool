# 翻译工具 (Translation Tool)

Windows 桌面翻译工具，基于 PySide6 构建。支持迷你悬浮窗和完整窗口两种模式，集成 Google / 百度翻译引擎，Windows 系统 OCR 截图翻译、剪贴板监听和历史记录。

如果不想了解代码只想使用该工具，可以直接下载 dist 目录下的 TranslationTool.exe 文件，双击即可在任务栏或隐藏图标中看到该工具已启动。

## 功能亮点

- **迷你悬浮窗** — 无边框置顶窗口，输入即翻，适合边看资料边翻译
- **截图翻译** — 框选屏幕任意区域，Windows 系统 OCR 识别后自动翻译，免费无需配置
- **多引擎** — Google 翻译（免费）+ 百度翻译（需 API Key）
- **剪贴板监听** — 复制即翻译，自动填入迷你窗口
- **历史记录** — 翻译自动存档，支持搜索，超过 3 天自动清理
- **全局快捷键** — Windows 原生热键，任何界面都可触发，支持自定义和冲突检测

迷你悬浮窗具体样式：

<img width="420" height="400" alt="image" src="https://github.com/user-attachments/assets/5a4aabc6-6dbd-428e-9cc0-a3a861c51d5e" />

当你启动该工具并且将窗口浮现时，直接ctrl+c复制文字，可以实时自动注入到翻译工具中翻译，不需要进行粘贴

<img width="635" height="443" alt="image" src="https://github.com/user-attachments/assets/96cb4651-5849-4b6b-9994-a8ca632fca79" />


## 安装

### 方式一：直接运行 exe

从 [Releases](https://github.com/dpq112/translation_tool/releases) 下载 `TranslationTool.exe`，双击运行。

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/dpq112/translation_tool.git
cd translation_tool

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install PySide6 deep-translator requests pillow winrt-Windows.Media.Ocr winrt-Windows.Graphics.Imaging winrt-Windows.Storage.Streams winrt-Windows.Storage winrt-Windows.Globalization winrt-Windows.Foundation winrt-Windows.Foundation.Collections

# 启动
python main.py
```

## 使用

启动后系统托盘出现「译」图标，右键展开菜单。

### 默认快捷键

| 功能 | 快捷键 | 说明 |
|---|---|---|
| 迷你翻译窗口 | `Ctrl + Shift + Q` | 显示 / 隐藏悬浮窗 |
| 完整翻译窗口 | `Ctrl + Shift + W` | 显示 / 隐藏（切换） |
| 截图翻译 | `Ctrl + Shift + E` | 框选屏幕区域进行 OCR 翻译 |

### 迷你窗口操作

- **拖拽标题栏** — 移动位置
- **📌** — 切换置顶 / 取消置顶
- **⚙** — 打开设置
- **✕** — 关闭窗口

### 截图翻译流程

1. 按下 `Ctrl + Shift + E`（或托盘菜单选择「截图翻译」）
2. 鼠标拖拽框选需要翻译的区域
3. 松开鼠标 → Windows OCR 自动识别 → 填入迷你窗口并翻译
4. ESC 或右键取消

> 截图翻译使用 Windows 系统 OCR，免费无需配置。确保系统已安装中文语言包即可正常识别中英文。

### 翻译引擎配置

- **Google 翻译**：免费，无需配置，开箱即用
- **百度翻译**：在 fanyi-api.baidu.com 注册获取 APP ID 和密钥，设置中填入后测试连接

## 快捷键管理

- 修改快捷键时自动检测内部冲突和系统冲突，冲突时拒绝并提示
- 保存设置后立即生效，无需重启

## 数据存储

- 配置：`%APPDATA%/TranslationTool/config.json`
- 历史：`%APPDATA%/TranslationTool/history.json`（目录可在设置中自定义，超过 3 天自动清理）

## 依赖

| 包 | 用途 |
|---|---|
| PySide6 | Qt 桌面框架 |
| deep-translator | Google 翻译 |
| requests | 百度翻译 API 调用 |
| pillow | 截图图像处理 |
| winrt | Windows 系统 OCR |

## 许可

MIT License
