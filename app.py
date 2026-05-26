# -*- coding: utf-8 -*-
"""应用主类 — 管理所有组件、信号连接和生命周期"""
import sys
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QIcon

from config_manager import ConfigManager
from translators.manager import TranslatorManager
from ocr import OCRManager
from clipboard_monitor import ClipboardMonitor
from hotkey_manager import HotkeyManager
from history_manager import HistoryManager
from windows import MiniWindow, MainWindow, SettingsWindow, ScreenshotOverlay, HistoryWindow
from ui.utils import show_modal


class App(QObject):
    def __init__(self, app_icon):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=3)

        # 初始化组件
        self.config = ConfigManager()
        self.translator_manager = TranslatorManager(self.config)
        self.ocr_manager = OCRManager(self.config)
        self.history_manager = HistoryManager(self.config.get("data_dir"))

        # 图标（从 main.py 传入，已设置为全局应用图标）
        self.app_icon = app_icon

        # 托盘
        self.tray_icon = QSystemTrayIcon(self.app_icon)
        self._setup_tray()

        # 创建窗口
        engines = self.translator_manager.get_available_engines()
        self.mini_window = MiniWindow(self.config, engines, self.app_icon)
        self.main_window = MainWindow(self.config, self.app_icon)
        self.settings_window = None
        self.history_window = None
        self.main_window.update_engines(engines)

        # 剪贴板监听
        self.clipboard_monitor = ClipboardMonitor()
        self.clipboard_monitor.text_copied.connect(self._on_text_copied)

        # 热键管理
        self.hotkey_manager = HotkeyManager(self.config)
        self._setup_hotkeys()

        # 连接信号
        self._connect_signals()

        # 翻译状态跟踪
        self._last_engine = "google"
        self.mini_window.set_engine_name("Google 翻译")

        # 显示托盘
        self.tray_icon.show()

    # ================================================================
    # 信号连接
    # ================================================================
    def _connect_signals(self):
        # 迷你窗口翻译请求 text, from_lang, to_lang, engine
        self.mini_window.translate_requested.connect(self._on_mini_translate)
        # 迷你窗口引擎切换
        self.mini_window.engine_changed.connect(self._on_engine_changed)
        # 迷你窗口设置按钮
        self.mini_window.settings_clicked.connect(self._open_settings)
        # 迷你窗口切换到大窗口
        self.mini_window.show_main_window.connect(self._switch_to_main)

        # 完整窗口翻译请求
        self.main_window.translate_requested.connect(self._on_main_translate)
        # 完整窗口引擎切换
        self.main_window.engine_changed.connect(self._on_engine_changed)
        # 完整窗口切换到小窗口
        self.main_window.switch_to_mini.connect(self._switch_to_mini_from_main)

        # 历史记录按钮
        self.mini_window.history_clicked.connect(self._show_history)
        self.main_window.history_clicked.connect(self._show_history)

        # 翻译结果信号 → UI 更新
        self._mini_translation_done.connect(self._update_mini_result)
        self._main_translation_done.connect(self._update_main_result)

        # OCR 结果信号
        self._ocr_done.connect(self._on_ocr_done)
        self._ocr_failed.connect(self._on_ocr_failed)

    # ================================================================
    # 系统托盘
    # ================================================================
    def _setup_tray(self):
        menu = QMenu()

        mini_action = menu.addAction("显示迷你翻译窗口")
        mini_action.triggered.connect(self._toggle_mini_window)

        main_action = menu.addAction("打开翻译窗口")
        main_action.triggered.connect(self._show_main_window)

        menu.addSeparator()

        ss_action = menu.addAction("截图翻译")
        ss_action.triggered.connect(self._start_screenshot)

        menu.addSeparator()

        history_action = menu.addAction("翻译历史")
        history_action.triggered.connect(self._show_history)

        menu.addSeparator()

        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self._open_settings)

        menu.addSeparator()

        exit_action = menu.addAction("退出")
        exit_action.triggered.connect(self._quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("翻译工具")
        self.tray_icon.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_mini_window()

    # ================================================================
    # 热键设置
    # ================================================================
    def _setup_hotkeys(self):
        ok = self.hotkey_manager.register_all()
        if not ok:
            failures = self.hotkey_manager.get_failed_hotkeys()
            if failures:
                detail = "\n".join(
                    f"· {name}: {hotkey}" for name, hotkey, _reason in failures
                )
                msg = f"以下快捷键注册失败（可能被其他程序占用）:\n{detail}\n请前往设置修改。"
            else:
                msg = "全局热键注册失败，请检查是否有其他程序占用。\n可通过系统托盘菜单手动操作。"
            QTimer.singleShot(500, lambda m=msg: self.tray_icon.showMessage(
                "翻译工具", m,
                QSystemTrayIcon.MessageIcon.Warning,
                5000,
            ))

        self.hotkey_manager.mini_window_triggered.connect(self._toggle_mini_window)
        self.hotkey_manager.main_window_triggered.connect(self._show_main_window)
        self.hotkey_manager.screenshot_triggered.connect(self._start_screenshot)

    # ================================================================
    # 窗口开关
    # ================================================================
    def _toggle_mini_window(self):
        if self.mini_window.isVisible():
            self.mini_window.hide()
        else:
            # 放置在屏幕右下角
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.right() - self.mini_window.width() - 20
            y = screen.bottom() - self.mini_window.height() - 40
            self.mini_window.move(x, y)
            self.mini_window.show()
            self.mini_window.raise_()
            self.mini_window.activateWindow()

    def _show_main_window(self):
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()

    def _show_history(self):
        if self.history_window is None:
            self.history_window = HistoryWindow(self.history_manager, icon=self.app_icon)
            self.history_window.setWindowFlags(
                self.history_window.windowFlags() | Qt.WindowStaysOnTopHint
            )
        if self.history_window.isMinimized():
            self.history_window.showNormal()
        self.history_window.show()
        self.history_window.raise_()
        self.history_window.activateWindow()

    def _switch_to_main(self):
        text, src, tgt, engine = self.mini_window.get_translate_params()
        self.main_window.set_source_text(text)
        # 同步引擎和大窗口的语言设置
        idx = self.main_window.engine_combo.findData(engine)
        if idx >= 0:
            self.main_window.engine_combo.setCurrentIndex(idx)
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        # 迷你窗口已在 show_main_window 触发后自行 hide

    def _switch_to_mini_from_main(self):
        """从大窗口切到小窗口，传递文字并切换显示"""
        text = self.main_window.input_area.toPlainText().strip()
        if text:
            self.mini_window.set_source_text(text)
        # 确保小窗口显示
        if not self.mini_window.isVisible():
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.right() - self.mini_window.width() - 20
            y = screen.bottom() - self.mini_window.height() - 40
            self.mini_window.move(x, y)
            self.mini_window.show()
        self.mini_window.raise_()
        self.mini_window.activateWindow()
        # 关闭大窗口
        self.main_window.hide()

    def _open_settings(self):
        if self.settings_window is not None:
            if self.settings_window.isMinimized():
                self.settings_window.showNormal()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            return

        self.settings_window = SettingsWindow(
            self.config,
            self.translator_manager,
            self.ocr_manager,
            icon=self.app_icon,
        )
        self.settings_window.setModal(False)  # 非模态，不阻塞其他窗口
        self.settings_window.setWindowFlags(
            self.settings_window.windowFlags() | Qt.WindowStaysOnTopHint
        )
        self.settings_window.settings_saved.connect(self._on_settings_saved)
        self.settings_window.finished.connect(self._on_settings_closed)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _on_settings_closed(self):
        self.settings_window = None

    def _on_settings_saved(self):
        # 同步数据目录
        data_dir = self.config.get("data_dir")
        self.history_manager.set_data_dir(data_dir)
        engines = self.translator_manager.get_available_engines()
        self.main_window.update_engines(engines)
        self.mini_window.update_engines(engines)
        engine = self.config.get("default_engine", "google")
        translator = self.translator_manager.get_translator(engine)
        self.mini_window.set_engine_name(translator.name)
        # 重新注册快捷键，使修改后的快捷键生效
        self.hotkey_manager.unregister_all()
        ok = self.hotkey_manager.register_all()
        if not ok:
            failures = self.hotkey_manager.get_failed_hotkeys()
            if failures:
                detail = "\n".join(
                    f"· {name}: {hotkey}" for name, hotkey, _reason in failures
                )
                msg = f"以下快捷键注册失败（可能被其他程序占用）:\n{detail}\n请检查冲突后重新设置。"
            else:
                msg = "快捷键重新注册失败，请重启应用。"
            self.tray_icon.showMessage(
                "翻译工具", msg,
                QSystemTrayIcon.MessageIcon.Warning,
                5000,
            )

    # ================================================================
    # 翻译处理
    # ================================================================
    _mini_translation_done = Signal(str)

    def _on_mini_translate(self, text, from_lang, to_lang, engine="google"):
        if not text:
            self.mini_window.set_result_text("")
            return

        translator = self.translator_manager.get_translator(engine)
        self.mini_window.set_status("翻译中...")
        self._last_engine = engine

        def work():
            try:
                result = translator.translate(text, from_lang, to_lang)
            except Exception as e:
                result = f"[翻译失败] {str(e)}"
            self._mini_translation_done.emit(result)

        self.executor.submit(work)

    def _update_mini_result(self, result):
        self.mini_window.set_result_text(result)
        self.mini_window.set_status("翻译完成")
        if not result.startswith("[翻译失败]"):
            src = self.mini_window.source_text.toPlainText().strip()
            if src:
                engine = self.mini_window.engine_combo.currentData() or "google"
                t = self.translator_manager.get_translator(engine)
                self.history_manager.add(
                    src, result, t.name,
                    source_lang=self.mini_window.source_lang.currentData(),
                    target_lang=self.mini_window.to_lang.currentData(),
                )

    def _on_main_translate(self, text, from_lang, to_lang, engine):
        if not text:
            self.main_window.set_result_text("")
            return

        translator = self.translator_manager.get_translator(engine)
        self.main_window.set_status(f"翻译中... 使用 {translator.name}")

        def work():
            try:
                result = translator.translate(text, from_lang, to_lang)
            except Exception as e:
                result = f"[翻译失败] {str(e)}"
            self._main_translation_done.emit(result)

        self.executor.submit(work)

    _main_translation_done = Signal(str)

    def _update_main_result(self, result):
        self.main_window.set_result_text(result)
        self.main_window.set_status("翻译完成")
        if not result.startswith("[翻译失败]"):
            src = self.main_window.input_area.toPlainText().strip()
            if src:
                engine = self.main_window.engine_combo.currentData() or "google"
                t = self.translator_manager.get_translator(engine)
                self.history_manager.add(
                    src, result, t.name,
                    source_lang=self.main_window.source_lang.currentData(),
                    target_lang=self.main_window.to_lang.currentData(),
                )

    def _on_engine_changed(self, engine):
        self.config.set("default_engine", engine)
        translator = self.translator_manager.get_translator(engine)

        # 同步两个窗口的引擎选择
        if self.sender() == self.mini_window:
            # 迷你窗口触发的，同步到大窗口
            self.main_window.update_engines(
                self.translator_manager.get_available_engines()
            )
            idx = self.main_window.engine_combo.findData(engine)
            if idx >= 0:
                self.main_window.engine_combo.setCurrentIndex(idx)
        elif self.sender() == self.main_window:
            # 大窗口触发的，同步到迷你窗口
            self.mini_window.set_engine_name(translator.name)

        # 如果迷你窗口有文字，重新翻译
        text = self.mini_window.source_text.toPlainText().strip()
        if text:
            self.mini_window.force_translate()

    # ================================================================
    # 剪贴板处理
    # ================================================================
    def _on_text_copied(self, text):
        if self.mini_window.isVisible() and text:
            self.mini_window.set_source_text(text)

    # ================================================================
    # 截图翻译
    # ================================================================
    def _start_screenshot(self):
        # 记录窗口可见状态，以便取消时恢复
        self._pre_screenshot_mini_visible = self.mini_window.isVisible()
        self._pre_screenshot_main_visible = self.main_window.isVisible()
        self.mini_window.hide()
        self.main_window.hide()
        QApplication.processEvents()

        # 短暂延迟确保窗口已完全隐藏
        QTimer.singleShot(200, self._show_overlay)

    def _show_overlay(self):
        self.overlay = ScreenshotOverlay()
        self.overlay.screenshot_taken.connect(self._on_screenshot_taken)
        self.overlay.cancelled.connect(self._on_screenshot_cancelled)

    def _restore_windows_after_screenshot(self):
        """恢复截屏前可见的窗口"""
        if getattr(self, '_pre_screenshot_main_visible', False):
            self._show_main_window()
        if getattr(self, '_pre_screenshot_mini_visible', False):
            self._toggle_mini_window()

    def _on_screenshot_cancelled(self):
        self._restore_windows_after_screenshot()

    def _on_screenshot_taken(self, image_bytes):
        engine = self.ocr_manager.get_engine()
        if not engine.is_available():
            show_modal(
                None, QMessageBox.Warning,
                "OCR 未配置",
                "请先在设置中配置百度 OCR API Key 后再使用截图翻译功能。",
            )
            self.tray_icon.showMessage(
                "翻译工具",
                "请在设置中配置百度 OCR API Key（与百度翻译使用不同服务）",
                QSystemTrayIcon.MessageIcon.Warning,
                3000,
            )
            self._restore_windows_after_screenshot()
            return

        self.mini_window.show()
        self.mini_window.raise_()
        self.mini_window.activateWindow()
        self.mini_window.set_source_text("[正在识别图片文字...]")
        self.mini_window.set_status("OCR 识别中...")

        def work():
            ok, result = engine.recognize(image_bytes)
            if ok and result:
                self._ocr_done.emit(result)
            else:
                self._ocr_failed.emit(result)

        self.executor.submit(work)

    _ocr_done = Signal(str)
    _ocr_failed = Signal(str)

    def _on_ocr_done(self, text):
        self.mini_window.set_source_text(text)
        self.mini_window.set_status("OCR 识别完成，正在翻译...")
        self.mini_window.force_translate()

    def _on_ocr_failed(self, error_msg):
        self.mini_window.set_source_text("")
        self.mini_window.set_result_text(error_msg)
        self.mini_window.set_status("OCR 失败")

    # ================================================================
    # 辅助方法
    # ================================================================
    def _quit(self):
        self.hotkey_manager.unregister_all()
        self.executor.shutdown(wait=False)
        self.mini_window.close()
        self.main_window.close()
        if self.history_window:
            self.history_window.close()
        QApplication.quit()
