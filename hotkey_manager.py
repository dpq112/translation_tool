# -*- coding: utf-8 -*-
"""全局热键管理器 — 使用 Windows RegisterHotKey API"""
import ctypes
from ctypes import wintypes

from PySide6.QtCore import QObject, Signal, QAbstractNativeEventFilter, Qt
from PySide6.QtWidgets import QApplication, QWidget

user32 = ctypes.WinDLL("user32", use_last_error=True)

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

_MOD_NAME_MAP = {
    "ctrl": MOD_CONTROL, "control": MOD_CONTROL,
    "shift": MOD_SHIFT,
    "alt": MOD_ALT, "menu": MOD_ALT,
    "win": MOD_WIN, "windows": MOD_WIN, "meta": MOD_WIN, "cmd": MOD_WIN,
}

_KEY_NAME_TO_VK = {
    "space": 0x20, "tab": 0x09, "enter": 0x0D, "return": 0x0D,
    "esc": 0x1B, "escape": 0x1B,
    "backspace": 0x08, "delete": 0x2E, "del": 0x2E,
    "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "insert": 0x2D, "ins": 0x2D,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "printscreen": 0x2C, "scrolllock": 0x91, "pause": 0x13,
    "num0": 0x60, "num1": 0x61, "num2": 0x62, "num3": 0x63,
    "num4": 0x64, "num5": 0x65, "num6": 0x66, "num7": 0x67,
    "num8": 0x68, "num9": 0x69,
}


def check_hotkey_available(hotkey_str):
    """通过临时 RegisterHotKey 测试热键是否被系统其他程序占用。
    返回 (True, None) 或 (False, error_message)"""
    mods, vk = _parse_hotkey(hotkey_str)
    if mods is None or vk is None:
        return False, f"无效的热键格式: {hotkey_str}"

    # 用临时窗口测试注册
    dummy = QWidget()
    dummy.setAttribute(Qt.WA_ShowWithoutActivating)
    dummy.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
    dummy.resize(1, 1)
    dummy.winId()
    hwnd = int(dummy.winId())

    test_id = 0xFFFE
    ok = user32.RegisterHotKey(hwnd, test_id, mods, vk)
    if ok:
        user32.UnregisterHotKey(hwnd, test_id)
        return True, None
    else:
        err = ctypes.get_last_error()
        return False, f"快捷键已被占用 (系统错误码: {err})"


def _parse_hotkey(hotkey_str):
    """解析热键字符串 'ctrl+shift+e' → (modifiers, vk_code)"""
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    mods = 0
    key = None
    for p in parts:
        if p in _MOD_NAME_MAP:
            mods |= _MOD_NAME_MAP[p]
        else:
            key = p

    if key is None:
        return None, None

    if key in _KEY_NAME_TO_VK:
        vk = _KEY_NAME_TO_VK[key]
    elif len(key) == 1:
        vk = user32.VkKeyScanW(ord(key))
        if vk == -1 or vk == 0xFFFF:
            return None, None
        vk = vk & 0xFF
    else:
        return None, None

    return mods, vk


class _HotkeyNativeFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, event_type, message):
        msg = ctypes.cast(
            ctypes.c_void_p(int(message)), ctypes.POINTER(wintypes.MSG)
        ).contents
        if msg.message == WM_HOTKEY:
            self._callback(msg.wParam)
            return True, 0
        return False, 0


class HotkeyManager(QObject):
    mini_window_triggered = Signal()
    main_window_triggered = Signal()
    screenshot_triggered = Signal()

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self._registered = {}  # hotkey_id → (name,)
        self._next_id = 1
        self._hwnd = None
        self._filter = None
        self._filter_installed = False

        # 创建隐藏窗口用于接收 WM_HOTKEY
        self._dummy = QWidget()
        self._dummy.setAttribute(Qt.WA_ShowWithoutActivating)
        self._dummy.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self._dummy.resize(1, 1)
        self._dummy.winId()  # 强制创建原生窗口句柄
        self._hwnd = int(self._dummy.winId())

        self._filter = _HotkeyNativeFilter(self._on_hotkey_event)

    def _on_hotkey_event(self, hotkey_id):
        entry = self._registered.get(hotkey_id)
        if entry is None:
            return
        name = entry[0]
        if name == "mini_window":
            self.mini_window_triggered.emit()
        elif name == "main_window":
            self.main_window_triggered.emit()
        elif name == "screenshot":
            self.screenshot_triggered.emit()

    def register_all(self):
        self.unregister_all()

        self._last_failures = []

        if not self._filter_installed:
            QApplication.instance().installNativeEventFilter(self._filter)
            self._filter_installed = True

        hotkeys = self.config.get("hotkeys", {})

        mappings = [
            ("mini_window", hotkeys.get("mini_window", "ctrl+shift+q")),
            ("main_window", hotkeys.get("main_window", "ctrl+shift+w")),
            ("screenshot", hotkeys.get("screenshot", "ctrl+shift+e")),
        ]

        for name, hotkey_str in mappings:
            mods, vk = _parse_hotkey(hotkey_str)
            if mods is None:
                self._last_failures.append((name, hotkey_str, "无效的热键格式"))
                continue

            hid = self._next_id
            self._next_id += 1

            ok = user32.RegisterHotKey(self._hwnd, hid, mods, vk)
            if not ok:
                err = ctypes.get_last_error()
                print(f"[Hotkey] RegisterHotKey 失败: {name} ({hotkey_str}), 错误码={err}")
                self._last_failures.append((name, hotkey_str, f"系统错误码: {err}"))
                continue

            self._registered[hid] = (name,)

        return len(self._registered) > 0

    def get_failed_hotkeys(self):
        """返回注册失败的热键列表 [(name, hotkey_str, reason), ...]"""
        return getattr(self, '_last_failures', [])

    def unregister_all(self):
        if self._hwnd:
            for hid in list(self._registered):
                user32.UnregisterHotKey(self._hwnd, hid)
            self._registered.clear()

        if self._filter_installed:
            try:
                QApplication.instance().removeNativeEventFilter(self._filter)
            except Exception:
                pass
            self._filter_installed = False
