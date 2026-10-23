import pyautogui

from .CoordinateConverter import CoordinateConverter

class MouseController:
    """Mouse actions inside the selected window's client area, using relative (0..1) coordinates.

    (0, 0) is the client area's top-left corner and (1, 1) its bottom-right corner.
    The window is chosen with WindowController.selectWindow().
    """

    @staticmethod
    def click(
        x: float,
        y: float,
        button: str = "left",
        clicks: int = 1,
    ) -> None:
        screenX, screenY = CoordinateConverter.convert(x, y)
        pyautogui.click(screenX, screenY, clicks=clicks, button=button)

    @staticmethod
    def scroll(
        x: float,
        y: float,
        amount: int,
    ) -> None:
        """Scroll at (x, y) by amount wheel notches; a positive amount scrolls up, negative down."""
        screenX, screenY = CoordinateConverter.convert(x, y)
        # pyautogui ignores x/y for scrolling on Windows, and the wheel event goes to the window under the cursor
        pyautogui.moveTo(screenX, screenY)
        # On Windows pyautogui sends amount as a raw wheel delta, and one notch is 120 (WHEEL_DELTA).
        # The delta reaches the window as a signed 16-bit value, so large amounts are sent in chunks
        maxNotchesPerEvent = 32767 // 120
        remaining = amount
        while remaining != 0:
            notches = max(-maxNotchesPerEvent, min(maxNotchesPerEvent, remaining))
            pyautogui.scroll(notches * 120)
            remaining -= notches

    @staticmethod
    def mouseMove(
        x: float,
        y: float,
        duration: float = 0.0,
    ) -> None:
        screenX, screenY = CoordinateConverter.convert(x, y)
        pyautogui.moveTo(screenX, screenY, duration=duration)

    @staticmethod
    def dragAndDrop(
        startX: float,
        startY: float,
        endX: float,
        endY: float,
        button: str = "left",
        duration: float = 0.5,
    ) -> None:
        """Press the button at (startX, startY), move to (endX, endY) and release it there."""
        startScreenX, startScreenY = CoordinateConverter.convert(startX, startY)
        endScreenX, endScreenY = CoordinateConverter.convert(endX, endY)

        pyautogui.moveTo(startScreenX, startScreenY)
        pyautogui.mouseDown(button=button)
        try:
            # A gradual move (duration > 0) lets the application notice the drag
            pyautogui.moveTo(endScreenX, endScreenY, duration=duration)
        finally:
            # Always release the button, even if the move fails
            pyautogui.mouseUp(button=button)
