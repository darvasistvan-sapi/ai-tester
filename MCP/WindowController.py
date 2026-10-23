import ctypes
import time
from ctypes import wintypes
from Environment import WINDOW_TITLE

import pygetwindow
from PIL import Image, ImageGrab

# Work in physical pixels, the same way pyautogui does, so window
# coordinates and mouse coordinates match on scaled (e.g. 150%) displays
ctypes.windll.user32.SetProcessDPIAware()

class WindowController:
    """Stores the target window and handles every window lookup."""

    window = None

    @staticmethod
    def saveScreenshot(savePath: str) -> None:
        """Capture the client area of the window and save it to savePath."""
        image = WindowController.getScreenshot()
        image.save(savePath)

    @staticmethod
    def getScreenshot() -> Image.Image:
        """Capture the client area of the window.

        The image covers exactly the area the relative (0..1) coordinates refer to.
        """
        left, top, width, height = WindowController.clientRect()

        # all_screens=True so windows on a secondary monitor are captured too
        return ImageGrab.grab(
            bbox=(left, top, left + width, top + height),
            all_screens=True,
        )

    @staticmethod
    def clientRect() -> tuple[int, int, int, int]:
        """Return the client area as (left, top, width, height) in screen pixels."""
        hwnd = WindowController.getWindow()._hWnd
        user32 = ctypes.windll.user32

        rect = wintypes.RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            raise ctypes.WinError()

        # GetClientRect is relative to the client area itself (top-left is 0, 0).
        # ClientToScreen only converts the point (0, 0) to absolute screen
        # coordinates; it does not move the window.
        topLeft = wintypes.POINT(0, 0)
        if not user32.ClientToScreen(hwnd, ctypes.byref(topLeft)):
            raise ctypes.WinError()

        return topLeft.x, topLeft.y, rect.right, rect.bottom

    @staticmethod
    def getWindow():
        if WindowController.window is None:
            WindowController.selectWindow(WINDOW_TITLE)
            if WindowController.window is None:
                raise ValueError(f"No window found with title: {WINDOW_TITLE!r}")
        WindowController.activate()

        return WindowController.window

    @staticmethod
    def selectWindow(windowTitle: str) -> None:
        windows = pygetwindow.getWindowsWithTitle(windowTitle)
        if not windows:
            raise ValueError(f"No window found with title: {windowTitle!r}")

        WindowController.window = windows[0]

    @staticmethod
    def activate() -> None:
        # Bring the window to the front so the click lands in it,
        # not in another window that covers it
        if WindowController.window is None:
            WindowController.window = WindowController.getWindow()

        if WindowController.window.isMinimized:
            WindowController.window.restore()

        if not WindowController.window.isActive:
            try:
                WindowController.window.activate()
            except pygetwindow.PyGetWindowException:
                # pygetwindow sometimes raises even when activation succeeded
                # ("The operation completed successfully"), the check below decides
                pass

        # Restoring and activating happen asynchronously in Windows,
        # so wait a little until the window really is in the foreground
        deadline = time.monotonic() + 1.0
        while WindowController.window.isMinimized or not WindowController.window.isActive:
            if time.monotonic() > deadline:
                raise RuntimeError(f"Failed to activate window: {WindowController.window.title!r}")
            time.sleep(0.05)
