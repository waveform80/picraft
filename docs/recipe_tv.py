#!/usr/bin/env python

from __future__ import division

import io
import time
import picamera
from picraft import World, Vector as V, Block
from picraft.block import _BLOCKS_BY_COLOR
from PIL import Image


class MinecraftTVScreen(object):
    def __init__(self, world, origin, size):
        self.world = world
        self.origin = origin
        self.size = size
        self.jpeg = None
        # Construct a palette for PIL
        self.palette = Image.new('P', (1, 1))
        self.palette_len = len(_BLOCKS_BY_COLOR)
        PALETTE = {data: color for color, (id, data) in _BLOCKS_BY_COLOR.items()}
        PALETTE = [PALETTE[i] for i in range(16)]
        self.palette.putpalette(
            [c for rgb in PALETTE for c in rgb] +
            list(PALETTE[0]) * (256 - len(PALETTE))
            )

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            if self.jpeg:
                self.jpeg.seek(0)
                self.render(self.jpeg)
            self.jpeg = io.BytesIO()
        self.jpeg.write(buf)

    def close(self):
        self.jpeg = None

    def render(self, jpeg):
        o = self.origin
        img = Image.open(jpeg)
        img = img.resize(self.size, Image.BILINEAR)
        img = img.quantize(self.palette_len, palette=self.palette)
        with self.world.connection.batch_start():
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    self.world.blocks[o + V(0, y, x)] = Block.from_id(35, img.getpixel((x, y)))


class MinecraftTV(object):
    def __init__(self, origin=V(), size=(12, 8)):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (64, int(64 / size[0] * size[1]))
        self.camera.framerate = 2
        self.world = World(ignore_errors=True)
        self.origin = origin
        self.size = V(0, size[1], size[0])
        self.button_vec = None
        self.screen = MinecraftTVScreen(
            self.world, origin + V(0, 1, 1), (size[0] - 2, size[1] - 2))

    def main_loop(self):
        self.create_tv()
        try:
            while True:
                for event in self.world.events.poll():
                    if event.pos == self.button_vec:
                        if self.camera.recording:
                            self.switch_off()
                        else:
                            self.switch_on()
                time.sleep(0.1)
        finally:
            if self.camera.recording:
                self.switch_off()
            self.destroy_tv()

    def create_tv(self):
        o = self.origin
        self.world.blocks[o:o + self.size + 1] = Block('#ffffff')
        self.world.blocks[
            o + V(0, 1, 1):o + self.size - V(0, 1, 1) + 1] = Block('#000000')
        self.button_vec = o + V(z=2)
        self.world.blocks[self.button_vec] = Block('#800000')

    def destroy_tv(self):
        o = self.origin
        self.world.blocks[o:o + self.size + 1] = Block('air')

    def switch_on(self):
        self.camera.start_recording(self.screen, format='mjpeg')

    def switch_off(self):
        self.camera.stop_recording()
        o = self.origin
        self.world.blocks[
            o + V(0, 1, 1):o + self.size - V(0, 2, 2) + 1] = Block('#000000')


def main():
    tv = MinecraftTV(origin=V(2, 0, 5), size=(24,16))
    tv.main_loop()


if __name__ == '__main__':
    main()
