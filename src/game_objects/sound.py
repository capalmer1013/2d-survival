import pyxel


class Sound:
    def __init__(self):
        self.sound_on = True

    def damage_sound(self):
        if self.sound_on:
            pyxel.play(0, 8)
