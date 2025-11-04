import dataclasses
from enum import IntEnum
import os

from PIL import Image, ImageDraw, ImageFont

from . import __path__

# constants

RESOURCES_DIR = os.path.join(__path__[0], "resources")

COLOR_MAP: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),
    1: (0, 0, 170),
    2: (0, 170, 0),
    3: (0, 170, 170),
    4: (170, 0, 0),
    5: (170, 0, 170),
    6: (255, 170, 0),
    7: (170, 170, 170),
    8: (85, 85, 85),
    9: (85, 85, 255),
    10: (85, 255, 85),
    11: (85, 255, 255),
    12: (255, 85, 85),
    13: (255, 85, 255),
    14: (255, 255, 85),
    15: (255, 255, 255),
}


class GraphicMode(IntEnum):
    Bold = 0
    Strike = 1
    Underline = 2
    Italic = 3
    Obfuscated = 4

    @classmethod
    def from_int(cls, value: int) -> 'GraphicMode':
        for v in cls:
            if v.value == value:
                return v
        raise ValueError("value not found")


@dataclasses.dataclass(frozen=True)
class FormattedTextSegment:
    text: str
    color: int | None  # one of the 16 color formats 0-16
    graphic: set[GraphicMode]  # one of the 6 graphic formats

    def is_bold(self):
        return GraphicMode.Bold in self.graphic

    def is_strike(self):
        return GraphicMode.Strike in self.graphic

    def is_underline(self):
        return GraphicMode.Underline in self.graphic

    def is_italic(self):
        return GraphicMode.Italic in self.graphic

    def is_obfuscated(self):
        return GraphicMode.Obfuscated in self.graphic


class MinecraftTextDraw:
    def __init__(self, image: Image.Image):
        self.image = image
        self.draw = ImageDraw.Draw(image)
        self.font = ImageFont.truetype(os.path.join(RESOURCES_DIR, "Minecraft.ttf"), size=16)

        self.color_formats = "0123456789abcdef"
        self.graphic_formats = "lmnok"
        self.reset_format = "r"
        self.all_format_chars = self.color_formats + self.graphic_formats + self.reset_format

    def get_formatted_text_segments(self, text: str, format_selector: str = "§") -> list[FormattedTextSegment]:
        segments: list[FormattedTextSegment] = []
        current_text = ""
        current_color = None
        current_graphic: set[GraphicMode] = set()

        i = 0
        n = len(text)

        while i < n:
            char = text[i]

            # Check for format selector
            if char == format_selector and i + 1 < n:
                format_char = text[i + 1].lower()

                if format_char in self.all_format_chars:
                    # flush accumulated text first
                    if len(current_text) != 0:
                        segments.append(
                            FormattedTextSegment(
                                text=current_text,
                                color=current_color,
                                graphic=set(current_graphic),
                            )
                        )
                        current_text = ""

                    # Apply formatting
                    if format_char in self.color_formats:
                        current_color = self.color_formats.index(format_char)
                        current_graphic = set()
                    elif format_char in self.graphic_formats:
                        current_graphic.add(
                            GraphicMode.from_int(self.graphic_formats.index(format_char))
                        )
                    elif format_char in self.reset_format:
                        current_color = None
                        current_graphic = set()

                    i += 2
                    continue
                else:
                    # invalid format, treat literal `§` and next char
                    current_text += char
                    i += 1
                    continue

            # Normal char
            current_text += char
            i += 1

        # final flush
        if len(current_text) != 0:
            segments.append(
                FormattedTextSegment(
                    text=current_text,
                    color=current_color,
                    graphic=current_graphic,
                )
            )

        return segments


    def text(self, xy: tuple[int, int], text: str, default_color: tuple[int, int, int] = (85, 85, 85)):
        assert isinstance(xy[0], int)
        assert isinstance(xy[1], int)

        x = xy[0]
        y = xy[1]
        for segment in self.get_formatted_text_segments(text):
            for char in segment.text:
                if char == "\n":
                    y += 18 # font height + 1 GUI pixel
                    x = xy[0]
                    continue
                if char == " ":
                    x += 8
                    if segment.is_bold():
                        x += 2
                    continue
                # TODO: Support italic text
                # we could support italic text by rendering each character on a sperate image, then
                # tranform that image and then paste it using self.draw, but that is very messy
                color = COLOR_MAP[segment.color] if segment.color else default_color
                prev_x = x
                obf_char = None
                if segment.is_obfuscated():
                    obf_char = "#"  # TODO: choose a random obfuscated symbol
                self.draw.text(
                    (x, y),
                    obf_char or char,
                    color,
                    font=self.font,
                )
                if segment.is_bold():
                    x += 2
                    self.draw.text(
                        (x, y),
                        obf_char or char,
                        color,
                        font=self.font,
                    )
                x += self.font.getlength(char)
                if segment.is_strike():
                    self.draw.rectangle((prev_x, y+9, x, y+10), fill=color)
                if segment.is_underline():
                    self.draw.rectangle((prev_x, y+18, x, y+19), fill=color)
