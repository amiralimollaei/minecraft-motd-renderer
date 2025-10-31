import os

from PIL import Image

from .textdraw import MinecraftTextDraw


# constants

RESOURCES_DIR = os.path.join(__path__[0], "resources")

def generate_tiling_background(tile: Image.Image, size: tuple[int, int]) -> Image.Image:
    tile_w, tile_h = tile.size
    background_im = Image.new('RGB', size)
    w, h = background_im.size
    for x in range(0, w, tile_w):
        for y in range(0, h, tile_h):
            background_im.paste(tile, (x, y))
    return background_im


def generate_tiling_dirt_background(size: tuple[int, int]):
    dirt_tile = Image.open(os.path.join(RESOURCES_DIR, "texture_dirt.png")).convert("RGB")
    dirt_tile = Image.eval(dirt_tile, lambda x: x * 0.2)
    dirt_tile = dirt_tile.resize(
        size=tuple(v*4 for v in dirt_tile.size),  # pyright: ignore[reportArgumentType]
        resample=Image.Resampling.NEAREST
    )
    return generate_tiling_background(dirt_tile, size)


def render_motd(
    name: str,
    text: str,
    favicon: Image.Image | None = None
) -> Image.Image:
    render = generate_tiling_dirt_background((642, 96))
    draw = MinecraftTextDraw(render)
    draw.text((88, 16), name, default_color=(255, 255, 255))
    draw.text((88, 40), text, default_color=(170, 170, 170))
    if favicon:
        render.paste(favicon, (16, 16))
    else:
        default_favicon = Image.open(os.path.join(RESOURCES_DIR, "default_favicon.png")).convert("RGB")
        default_favicon = default_favicon.resize((64, 64))
        render.paste(default_favicon, (16, 16))
    return render
