import io
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

COURSE_IMAGES = abspath(join(dirname(__file__), "../course/images/"))


class ExtremeAspectCropTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.QUALITY = "keep"
        cfg.SVG_DPI = 200

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_very_wide_short_size_returns_visible_strip(self):
        response = await self.async_fetch("/unsafe/800x20/rainbow.png")
        assert response.code == 200
        image = Image.open(io.BytesIO(response.body)).convert("RGBA")
        assert image.size == (800, 20)
        assert image.getchannel("A").getextrema()[1] > 0

    @gen_test
    async def test_fit_in_1x1_returns_1x1_image(self):
        response = await self.async_fetch("/unsafe/fit-in/1x1/940x2.png")
        assert response.code == 200
        image = Image.open(io.BytesIO(response.body))
        assert image.size == (1, 1)

    @gen_test
    async def test_fit_in_width_only_returns_100x1_image(self):
        response = await self.async_fetch("/unsafe/fit-in/100x0/940x2.png")
        assert response.code == 200
        image = Image.open(io.BytesIO(response.body))
        assert image.size == (100, 1)
