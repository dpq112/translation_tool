# -*- coding: utf-8 -*-
"""设置窗口 — API 密钥配置、快捷键编辑"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QTabWidget, QWidget,
    QMessageBox, QGridLayout, QFileDialog, QApplication,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QKeySequence
from ui.utils import shake_widget, show_modal


HOTKEY_DESCRIPTIONS = {
    "mini_window": "显示/隐藏迷你翻译窗口",
    "main_window": "打开完整翻译窗口",
    "screenshot": "截图翻译",
}

HOTKEY_DEFAULTS = {
    "mini_window": "ctrl+shift+q",
    "main_window": "ctrl+shift+w",
    "screenshot": "ctrl+shift+e",
}


class HotkeyCaptureLine(QWidget):
    """可点击捕获快捷键的控件"""
    key_captured = Signal(str)

    def __init__(self, current_key=""):
        super().__init__()
        self.current_key = current_key
        self.capturing = False
        self._pending_key = None
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.key_label = QLabel(self.current_key)
        self.key_label.setObjectName("hotkeyTag")
        self.key_label.setCursor(Qt.PointingHandCursor)
        self.key_label.mousePressEvent = self._start_capture
        layout.addWidget(self.key_label)

        self.capture_btn = QPushButton("修改")
        self.capture_btn.setObjectName("accentBtn")
        self.capture_btn.setFixedWidth(56)
        self.capture_btn.clicked.connect(self._start_capture)
        layout.addWidget(self.capture_btn)

        self.hint_label = QLabel("")
        self.hint_label.setObjectName("hintLabel")
        layout.addWidget(self.hint_label)
        layout.addStretch()

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)

    def _start_capture(self, event=None):
        self.capturing = True
        self._pending_key = None
        self.key_label.setText("按下快捷键...")
        self.key_label.setStyleSheet(
            "background-color: #e8f0fe; color: #1a73e8; "
            "border: 2px dashed #1a73e8; border-radius: 6px; "
            "padding: 5px 12px; font-family: Consolas, monospace; "
            "font-size: 13px; font-weight: bold;"
        )
        self.capture_btn.setEnabled(False)
        self.hint_label.setText("请按下新的快捷键组合，ESC 取消")
        self.setFocus()
        self.grabKeyboard()

    def keyPressEvent(self, event):
        if not self.capturing:
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Escape:
            self._cancel_capture()
            return

        modifiers = event.modifiers()
        key = event.key()

        parts = []
        if modifiers & Qt.ControlModifier:
            parts.append("ctrl")
        if modifiers & Qt.ShiftModifier:
            parts.append("shift")
        if modifiers & Qt.AltModifier:
            parts.append("alt")
        if modifiers & Qt.MetaModifier:
            parts.append("win")

        if key not in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            key_name = QKeySequence(key).toString().lower()
            parts.append(key_name)

        if len(parts) >= 2 and any(k not in ("ctrl", "shift", "alt", "win") for k in parts):
            new_key = "+".join(parts)
            self._pending_key = new_key
            self.key_label.setText(new_key)
            self._end_capture()
            self.key_captured.emit(new_key)
        else:
            self.hint_label.setText("需要组合键，如 Ctrl+Shift+X")

    def accept_key(self):
        """确认热键更改（由父组件在验证通过后调用）"""
        if self._pending_key:
            self.current_key = self._pending_key
        self._pending_key = None

    def reject_key(self):
        """拒绝热键更改，回退到旧值（由父组件在验证失败后调用）"""
        self._pending_key = None
        self.key_label.setText(self.current_key)

    def _cancel_capture(self):
        self.key_label.setText(self.current_key)
        self._pending_key = None
        self._end_capture()

    def _end_capture(self):
        self.capturing = False
        self.capture_btn.setEnabled(True)
        self.hint_label.setText("")
        self.key_label.setStyleSheet("")
        self.releaseKeyboard()
        self.clearFocus()


class SettingsWindow(QDialog):
    settings_saved = Signal()

    def __init__(self, config_manager, translator_manager, ocr_engine, icon=None):
        super().__init__()
        self.config = config_manager
        self.translator_manager = translator_manager
        self.ocr_engine = ocr_engine
        self._modified_hotkeys = {}
        self._init_ui()
        self._load_config()
        self._apply_style()
        if icon:
            self.setWindowIcon(icon)

    def _init_ui(self):
        self.setWindowTitle("翻译工具 - 设置")
        self.resize(650, 600)
        self.setMinimumSize(600, 520)
        self.setWindowFlags(
            (self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            | Qt.WindowMinimizeButtonHint
        )
        self.setObjectName("settingsWindow")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        tabs = QTabWidget()

        # ================================================================
        # 翻译引擎标签页
        # ================================================================
        translate_tab = QWidget()
        translate_layout = QVBoxLayout()
        translate_layout.setSpacing(16)
        translate_layout.setContentsMargins(12, 12, 12, 12)

        # Google
        google_group = QGroupBox("Google 翻译")
        google_layout = QVBoxLayout()
        google_info = QLabel("免费引擎，无需配置，始终可用。")
        google_info.setObjectName("hintLabel")
        google_layout.addWidget(google_info)
        google_group.setLayout(google_layout)
        translate_layout.addWidget(google_group)

        # 百度翻译
        baidu_group = QGroupBox("百度翻译")
        baidu_layout = QVBoxLayout()
        baidu_layout.setSpacing(10)

        baidu_info = QLabel("在百度翻译开放平台 (fanyi-api.baidu.com) 注册获取 APP ID 和密钥。")
        baidu_info.setObjectName("hintLabel")
        baidu_info.setWordWrap(True)
        baidu_layout.addWidget(baidu_info)

        baidu_grid = QGridLayout()
        baidu_grid.setSpacing(8)
        baidu_grid.setColumnStretch(1, 1)

        app_id_label = QLabel("APP ID")
        app_id_label.setMinimumWidth(80)
        self.baidu_app_id = QLineEdit()
        self.baidu_app_id.setPlaceholderText("请输入百度翻译 APP ID")
        baidu_grid.addWidget(app_id_label, 0, 0)
        baidu_grid.addWidget(self.baidu_app_id, 0, 1)

        secret_label = QLabel("密钥")
        self.baidu_secret_key = QLineEdit()
        self.baidu_secret_key.setPlaceholderText("请输入百度翻译密钥 (Secret Key)")
        self.baidu_secret_key.setEchoMode(QLineEdit.Password)
        baidu_grid.addWidget(secret_label, 1, 0)
        baidu_grid.addWidget(self.baidu_secret_key, 1, 1)

        baidu_layout.addLayout(baidu_grid)

        baidu_btn_row = QHBoxLayout()
        self.baidu_test_btn = QPushButton("测试连接")
        self.baidu_test_btn.setObjectName("accentBtn")
        self.baidu_test_btn.clicked.connect(self._test_baidu)
        baidu_btn_row.addWidget(self.baidu_test_btn)
        baidu_btn_row.addStretch()
        baidu_layout.addLayout(baidu_btn_row)
        baidu_group.setLayout(baidu_layout)
        translate_layout.addWidget(baidu_group)

        translate_layout.addStretch()

        translate_tab.setLayout(translate_layout)
        tabs.addTab(translate_tab, "翻译引擎")

        # ================================================================
        # OCR 标签页
        # ================================================================
        ocr_tab = QWidget()
        ocr_layout = QVBoxLayout()
        ocr_layout.setSpacing(16)
        ocr_layout.setContentsMargins(12, 12, 12, 12)

        ocr_group = QGroupBox("百度 OCR（截图翻译文字识别）")
        ocr_layout_inner = QVBoxLayout()
        ocr_layout_inner.setSpacing(10)

        ocr_info = QLabel(
            "在 ai.baidu.com 开通「通用文字识别」服务后，"
            "在百度智能云控制台获取 API Key 和 Secret Key。"
        )
        ocr_info.setObjectName("hintLabel")
        ocr_info.setWordWrap(True)
        ocr_layout_inner.addWidget(ocr_info)

        ocr_grid = QGridLayout()
        ocr_grid.setSpacing(8)
        ocr_grid.setColumnStretch(1, 1)

        ocr_api_label = QLabel("API Key")
        ocr_api_label.setMinimumWidth(80)
        self.ocr_api_key = QLineEdit()
        self.ocr_api_key.setPlaceholderText("请输入百度 OCR API Key")
        ocr_grid.addWidget(ocr_api_label, 0, 0)
        ocr_grid.addWidget(self.ocr_api_key, 0, 1)

        ocr_secret_label = QLabel("Secret Key")
        self.ocr_secret = QLineEdit()
        self.ocr_secret.setPlaceholderText("请输入百度 OCR Secret Key")
        self.ocr_secret.setEchoMode(QLineEdit.Password)
        ocr_grid.addWidget(ocr_secret_label, 1, 0)
        ocr_grid.addWidget(self.ocr_secret, 1, 1)

        ocr_layout_inner.addLayout(ocr_grid)

        ocr_btn_row = QHBoxLayout()
        self.ocr_test_btn = QPushButton("测试连接")
        self.ocr_test_btn.setObjectName("accentBtn")
        self.ocr_test_btn.clicked.connect(self._test_ocr)
        ocr_btn_row.addWidget(self.ocr_test_btn)
        ocr_btn_row.addStretch()
        ocr_layout_inner.addLayout(ocr_btn_row)

        ocr_group.setLayout(ocr_layout_inner)
        ocr_layout.addWidget(ocr_group)
        ocr_layout.addStretch()

        ocr_tab.setLayout(ocr_layout)
        tabs.addTab(ocr_tab, "OCR 设置")

        # ================================================================
        # 快捷键标签页
        # ================================================================
        hotkey_tab = QWidget()
        hotkey_layout = QVBoxLayout()
        hotkey_layout.setSpacing(14)
        hotkey_layout.setContentsMargins(12, 12, 12, 12)

        hotkey_info = QLabel("点击快捷键标签或「修改」按钮来更改快捷键，按 ESC 取消修改。")
        hotkey_info.setObjectName("hintLabel")
        hotkey_layout.addWidget(hotkey_info)

        hotkey_group = QGroupBox("全局快捷键")
        hotkey_group_layout = QVBoxLayout()
        hotkey_group_layout.setSpacing(12)

        self.hotkey_widgets = {}
        for key, desc in HOTKEY_DESCRIPTIONS.items():
            row = QHBoxLayout()
            row.setSpacing(12)

            desc_label = QLabel(desc)
            desc_label.setMinimumWidth(160)
            desc_label.setStyleSheet("color: #d0d0e0; font-size: 13px;")
            row.addWidget(desc_label)

            current = self.config.get(f"hotkeys.{key}") or HOTKEY_DEFAULTS[key]
            capture = HotkeyCaptureLine(current)
            capture.key_captured.connect(lambda new_key, k=key: self._on_hotkey_changed(k, new_key))
            self.hotkey_widgets[key] = capture
            row.addWidget(capture, stretch=1)

            row_widget = QWidget()
            row_widget.setLayout(row)
            hotkey_group_layout.addWidget(row_widget)

        hotkey_group.setLayout(hotkey_group_layout)
        hotkey_layout.addWidget(hotkey_group)
        hotkey_layout.addStretch()

        hotkey_tab.setLayout(hotkey_layout)
        tabs.addTab(hotkey_tab, "快捷键")

        # ================================================================
        # 通用标签页
        # ================================================================
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        general_layout.setSpacing(16)
        general_layout.setContentsMargins(12, 12, 12, 12)

        data_group = QGroupBox("数据存储")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(10)

        data_info = QLabel("翻译历史记录将存储在此目录中，超过 3 天的记录自动清理。")
        data_info.setObjectName("hintLabel")
        data_info.setWordWrap(True)
        data_layout.addWidget(data_info)

        dir_row = QHBoxLayout()
        dir_row.setSpacing(10)
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setPlaceholderText("选择数据存储目录...")
        dir_row.addWidget(self.data_dir_edit, stretch=1)

        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("accentBtn")
        browse_btn.clicked.connect(self._browse_data_dir)
        dir_row.addWidget(browse_btn)
        data_layout.addLayout(dir_row)

        data_group.setLayout(data_layout)
        general_layout.addWidget(data_group)
        general_layout.addStretch()

        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "通用")

        layout.addWidget(tabs)

        # 底部按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QPushButton("保存设置")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._save_and_close)
        btn_row.addWidget(self.save_btn)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _apply_style(self):
        from ui.styles import APP_STYLE
        self.setStyleSheet(APP_STYLE)

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange and not self.isActiveWindow():
            modal = QApplication.activeModalWidget()
            if modal is not None:
                shake_widget(self)
                shake_widget(modal)
            else:
                self.showMinimized()
        super().changeEvent(event)

    def _on_hotkey_changed(self, key, new_value):
        """验证快捷键是否冲突，通过则存储，冲突则回退并提示"""
        if not self._check_hotkey_available(key, new_value):
            self.hotkey_widgets[key].reject_key()
            return
        self.hotkey_widgets[key].accept_key()
        self._modified_hotkeys[key] = new_value

    def _check_hotkey_available(self, changed_key, new_hotkey):
        """检查快捷键是否可用。返回 True 表示可用，False 表示冲突"""
        from hotkey_manager import check_hotkey_available

        # 1. 检查是否与自己已有的其他热键冲突（原始值）
        hotkeys = self.config.get("hotkeys", {})
        for hk_name, hk_value in hotkeys.items():
            if hk_name != changed_key and hk_value.lower() == new_hotkey.lower():
                show_modal(
                    self, QMessageBox.Warning, "快捷键冲突",
                    f"「{new_hotkey}」已用于"
                    f"「{HOTKEY_DESCRIPTIONS.get(hk_name, hk_name)}」，\n"
                    f"请选择其他快捷键。"
                )
                return False

        # 2. 检查是否与本轮已修改的其他热键冲突
        for hk_name, hk_value in self._modified_hotkeys.items():
            if hk_name != changed_key and hk_value.lower() == new_hotkey.lower():
                show_modal(
                    self, QMessageBox.Warning, "快捷键冲突",
                    f"「{new_hotkey}」已在本轮修改中用于"
                    f"「{HOTKEY_DESCRIPTIONS.get(hk_name, hk_name)}」，\n"
                    f"请选择其他快捷键。"
                )
                return False

        # 3. 系统级冲突检测（仅当热键确实改变了时才检测系统占用）
        original = hotkeys.get(changed_key, "")
        if new_hotkey.lower() != original.lower():
            available, msg = check_hotkey_available(new_hotkey)
            if not available:
                show_modal(
                    self, QMessageBox.Warning, "快捷键冲突",
                    f"「{new_hotkey}」与系统其他程序的快捷键冲突，\n"
                    f"请选择其他快捷键组合。\n\n({msg})"
                )
                return False

        return True

    def _load_config(self):
        baidu = self.config.get("translators.baidu", {})
        self.baidu_app_id.setText(baidu.get("app_id", ""))
        self.baidu_secret_key.setText(baidu.get("secret_key", ""))

        ocr = self.config.get("ocr.baidu", {})
        self.ocr_api_key.setText(ocr.get("api_key", ""))
        self.ocr_secret.setText(ocr.get("secret_key", ""))

        self.data_dir_edit.setText(self.config.get("data_dir", ""))

    def _save_and_close(self):
        self.config.set("translators.baidu.app_id", self.baidu_app_id.text().strip())
        self.config.set("translators.baidu.secret_key", self.baidu_secret_key.text().strip())
        self.config.set("ocr.baidu.api_key", self.ocr_api_key.text().strip())
        self.config.set("ocr.baidu.secret_key", self.ocr_secret.text().strip())
        self.config.set("data_dir", self.data_dir_edit.text().strip())

        for key, value in self._modified_hotkeys.items():
            self.config.set(f"hotkeys.{key}", value)

        self.translator_manager.refresh_credentials()
        self.ocr_engine.api_key = self.ocr_api_key.text().strip()
        self.ocr_engine.secret_key = self.ocr_secret.text().strip()

        show_modal(self, QMessageBox.Information, "提示", "设置已保存！")
        self.settings_saved.emit()
        self.accept()

    def _browse_data_dir(self):
        current = self.data_dir_edit.text().strip()
        if not current:
            import os
            from pathlib import Path
            current = str(Path(os.environ["APPDATA"]) / "TranslationTool")
        directory = QFileDialog.getExistingDirectory(self, "选择数据存储目录", current)
        if directory:
            self.data_dir_edit.setText(directory)

    def _test_baidu(self):
        from translators.baidu import BaiduTranslate
        t = BaiduTranslate(self.baidu_app_id.text().strip(), self.baidu_secret_key.text().strip())
        if not t.is_available():
            show_modal(self, QMessageBox.Warning, "提示", "请先填入百度翻译 APP ID 和密钥")
            return
        result = t.translate("hello", "en", "zh")
        if result.startswith("[翻译失败]"):
            show_modal(self, QMessageBox.Warning, "测试失败", result)
        else:
            show_modal(self, QMessageBox.Information, "测试成功", f"翻译结果: hello → {result}")

    def _test_ocr(self):
        show_modal(
            self, QMessageBox.Information, "提示",
            "OCR 功能需要上传真实图片测试。\n请在截图翻译中实际使用以验证配置。"
        )
