# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Windows 桌面翻译工具，使用 PySide6 构建。支持迷你悬浮窗和完整窗口两种模式，集成 Google/百度/有道三种翻译引擎，以及截图 OCR 翻译功能。

## 运行和开发

```bash
# 激活虚拟环境
source venv/Scripts/activate

# 启动应用
python main.py
```

无 requirements.txt。当前 venv 中已安装的关键依赖：

| 包 | 用途 |
|---|---|
| PySide6 | Qt 桌面框架 |
| deep-translator | Google 翻译（免费，无需 API Key） |
| requests | 百度/有道 API 调用 |
| keyboard | 全局热键注册 |
| pillow | 截图图像处理 |

## 架构

### 入口与生命周期

`main.py` → 创建 `QApplication`，实例化 `App`（位于 `app.py`），调用 `app.exec()` 进入事件循环。

`App` 是顶层协调器，持有所有组件引用，建立 Qt 信号连接，管理应用生命周期（包括退出时的热键注销和线程池关闭）。

### 翻译引擎 — 插件模式

`translators/` 目录实现统一的翻译器接口：

- `base.py` — `BaseTranslator` 抽象类，定义 `translate(text, from_lang, to_lang) → str` 和 `is_available() → bool`
- `google.py` — 通过 `deep_translator` 调用 Google 翻译，始终可用，无需配置
- `baidu.py` — 百度翻译 API，需 app_id + secret_key
- `youdao.py` — 有道翻译 API，需 app_key + secret_key
- `manager.py` — `TranslatorManager` 工厂，管理所有翻译器实例和凭证刷新

每种引擎有自己的语言代码映射表（`_BAIDU_LANG_MAP` 等），将统一的短代码（`zh`, `en`）转换为各 API 要求的格式。

### UI 窗口

`windows/` 目录包含所有界面：

- `mini_window.py` — `MiniWindow`：无边框、置顶、420×400 浮动窗口。输入翻译后 500ms 防抖自动触发翻译。支持拖拽移动。
- `main_window.py` — `MainWindow`：标准窗口 900×560，带状态栏。支持交换源/目标语言。
- `settings_window.py` — `SettingsWindow`：非模态对话框，三个标签页（翻译引擎配置、OCR 设置、快捷键录制）。打开时通过 `eventFilter` 拦截翻译窗口操作。
- `screenshot_overlay.py` — `ScreenshotOverlay`：全屏覆盖层，绘制屏幕截图并在用户选区上叠加半透明遮罩，返回选区 PNG 的 bytes。

迷你窗口和大窗口之间可以双向切换，切换时会同步文字和引擎选择。

### OCR

`ocr/baidu_ocr.py` — 百度 OCR API，截图翻译流程：截图选区 → base64 编码图片 → 百度 OCR 识别 → 文字填入迷你窗口并自动触发翻译。access_token 过期时会自动重试一次。

### 信号驱动架构

所有异步操作（翻译、OCR）通过 `ThreadPoolExecutor`（max_workers=3）提交到后台线程，完成后通过 Qt Signal 将结果传回主线程更新 UI。关键信号：

- `mini_window.translate_requested` / `main_window.translate_requested` → `App._on_mini_translate` / `App._on_main_translate`
- `_mini_translation_done` / `_main_translation_done` → 更新对应窗口的结果区域
- `_ocr_done` / `_ocr_failed` → 填入迷你窗口

### 配置管理

`config_manager.py` — JSON 文件持久化到 `%APPDATA%/TranslationTool/config.json`。支持点号路径访问（`get("translators.baidu.app_id")`）。默认引擎为 Google。

### 剪贴板监听

`clipboard_monitor.py` — 每 400ms 轮询剪贴板，检测到新文本时发出 `text_copied` 信号，自动填入迷你窗口的原文区域。

### 热键

`hotkey_manager.py` — 通过 `keyboard` 库注册三个全局热键，默认值：
- `ctrl+shift+q` — 迷你窗口
- `ctrl+shift+w` — 完整窗口
- `ctrl+shift+e` — 截图翻译

### UI 样式

`ui/styles.py` — 集中管理所有 QSS，通过 `APP_STYLE` 字符串变量导出，各窗口在初始化时调用 `self.setStyleSheet(APP_STYLE)`。白色主题，主色 `#1a73e8`。
