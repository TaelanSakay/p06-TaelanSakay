# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase

BLOCK = 50


class RoundCornerTransparentTestCase(FilterTestCase):
    @gen_test
    async def test_round_corner_transparent_edge_is_not_darkened(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
            mode="RGBA",
        )
        source = self.get_fixture("source.jpg", mode="RGBA")

        partly_transparent = 0
        for x in range(BLOCK):
            for y in range(BLOCK):
                r, g, b, a = image.getpixel((x, y))
                if 0 < a < 255:
                    partly_transparent += 1
                if a == 255:
                    src_r, src_g, src_b, _ = source.getpixel((x, y))
                    assert (r, g, b) == (src_r, src_g, src_b), (
                        f"pixel {(x, y)} darkened: "
                        f"{(r, g, b)} vs source {(src_r, src_g, src_b)}"
                    )

        assert partly_transparent > 0
