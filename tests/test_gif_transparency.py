from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_palette_gif():
    img = Image.new("P", (40, 40), 0)
    img.putpalette([255, 0, 0, 0, 0, 0] + [0, 0, 0] * 254)
    for x in range(20, 40):
        for y in range(40):
            img.putpixel((x, y), 1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=1)
    return buffer.getvalue()


def make_opaque_palette_gif():
    img = Image.new("P", (40, 40), 0)
    img.putpalette([255, 0, 0, 0, 0, 0] + [0, 0, 0] * 254)
    buffer = BytesIO()
    img.save(buffer, "GIF")
    return buffer.getvalue()


def resize_and_read(data):
    config = Config(PILLOW_PRESERVE_INDEXED_MODE=True)
    engine = Engine(Context(config=config))
    engine.load(data, ".gif")
    engine.resize(20, 20)
    return engine.read(".gif")


def test_resized_palette_gif_keeps_transparent_and_opaque_regions():
    out = Image.open(BytesIO(resize_and_read(make_palette_gif())))
    assert "transparency" in out.info
    rgba = out.convert("RGBA")
    assert rgba.getpixel((15, 10))[3] == 0
    assert rgba.getpixel((18, 5))[3] == 0
    assert rgba.getpixel((3, 10))[3] == 255
    assert rgba.getpixel((5, 15))[3] == 255


def test_opaque_palette_gif_stays_opaque():
    out = Image.open(BytesIO(resize_and_read(make_opaque_palette_gif())))
    assert "transparency" not in out.info
    rgba = out.convert("RGBA")
    assert rgba.getchannel("A").getextrema() == (255, 255)
