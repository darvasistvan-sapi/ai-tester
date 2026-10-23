from .WindowController import WindowController

class CoordinateConverter:
    """Converts relative (0..1) client-area coordinates to absolute screen pixels.

    Only the selected window's client area is used: the title bar, menu frame
    and borders are excluded. The client area is read on every conversion,
    so the result stays correct even if the window is moved or resized.
    """

    @staticmethod
    def convert(x: float, y: float) -> tuple[int, int]:
        CoordinateConverter._validate(x, "x")
        CoordinateConverter._validate(y, "y")

        left, top, width, height = WindowController.clientRect()

        # (size - 1) keeps x = 1 / y = 1 on the last pixel inside the client area
        screenX = left + round(x * (width - 1))
        screenY = top + round(y * (height - 1))

        return screenX, screenY

    @staticmethod
    def _validate(value: float, name: str) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{name} must be between 0 and 1, got {value}"
            )
