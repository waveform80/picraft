from __future__ import division

import io
import time
import picamera
from picraft import World, V, X, Y, Z, Block
from PIL import Image


def track_changes(old_state, new_state, default=Block('#000000')):
    changes = {v: b for v, b in new_state.items() if old_state.get(v) != b}
    changes.update({v: default for v in old_state if not v in new_state})
    return changes


class MinecraftTVScreen(object):
    def __init__(self, world, origin, size):
        self.world = world
        self.origin = origin
        self.size = size
        self.jpeg = None
        self.state = {}
        # Construct a palette for PIL
        self.palette = list(Block.COLORS)
        self.palette_img = Image.new('P', (1, 1))
        self.palette_img.putpalette(
            [c for rgb in self.palette for c in rgb] +
            list(self.palette[0]) * (256 - len(self.palette))
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
        img = img.quantize(len(self.palette), palette=self.palette_img)
        new_state = {
            o + V(0, y, x): Block.from_color(self.palette[img.getpixel((x, y))], exact=True)
            for x in range(img.size[0])
            for y in range(img.size[1])
            }
        with self.world.connection.batch_start():
            for v, b in track_changes(self.state, new_state).items():
                self.world.blocks[v] = b
        self.state = new_state


class MinecraftTV(object):
    def __init__(self, world, origin=V(), size=(12, 8)):
        self.world = world
        self.camera = picamera.PiCamera()
        self.camera.resolution = (64, int(64 / size[0] * size[1]))
        self.camera.framerate = 5
        self.origin = origin
        self.size = V(0, size[1], size[0])
        self.button_pos = None
        self.quit_pos = None
        self.screen = MinecraftTVScreen(
            self.world, origin + V(0, 1, 1), (size[0] - 2, size[1] - 2))

    def main_loop(self):
        try:
            self.create_tv()
            running = True
            while running:
                for event in self.world.events.poll():
                    if event.pos == self.button_pos:
                        if self.camera.recording:
                            self.switch_off()
                        else:
                            self.switch_on()
                    elif event.pos == self.quit_pos:
                        running = False
                time.sleep(0.1)
        finally:
            if self.camera.recording:
                self.switch_off()
            self.destroy_tv()

    def create_tv(self):
        o = self.origin
        self.world.blocks[o:o + self.size + 1] = Block('#ffffff')
        self.world.blocks[
            o + V(0, 1, 1):o + self.size - V(0, 2, 2) + 1] = Block('#000000')
        self.button_pos = o + V(z=3)
        self.quit_pos = o + V(z=1)
        self.world.blocks[self.button_pos] = Block('#0080ff')
        self.world.blocks[self.quit_pos] = Block('#800000')
        self.world.say('Behold the Minecraft TV!')

    def destroy_tv(self):
        o = self.origin
        self.world.blocks[o:o + self.size + 1] = Block('air')

    def switch_on(self):
        self.world.say('Switching TV on')
        self.camera.start_recording(self.screen, format='mjpeg')

    def switch_off(self):
        self.world.say('Switching TV off')
        self.camera.stop_recording()
        o = self.origin
        self.world.blocks[
            o + V(0, 1, 1):o + self.size - V(0, 2, 2) + 1] = Block('#000000')


with World(ignore_errors=True) as world:
    p = world.player.tile_pos
    tv = MinecraftTV(world, origin=p + 8*X + 2*Y, size=(20, 14))
    tv.main_loop()

