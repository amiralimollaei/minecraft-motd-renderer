from PIL import Image

from minecraft_motd_renderer import render_motd

if __name__ == "__main__":
    render = render_motd(
        name="Hypixel",
        text="§r                §aHypixel Network §c[1.8/1.21]§r\n           §d§lSB 0.23.5 §7- §6§lHALLOWEEN EVENT",
        favicon=Image.open("hypixel.png")
    )
    render = render.resize(
        size=tuple(v*4 for v in render.size),  # pyright: ignore[reportArgumentType]
        resample=Image.Resampling.NEAREST
    )
    render.save("motd.png")
