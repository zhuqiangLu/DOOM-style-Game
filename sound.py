import pygame as pg
from settings import SOUND_ENABLED


class Sound:
    def __init__(self, game):
        self.game = game
        self.path = 'resources/sound/'
        if SOUND_ENABLED:
            pg.mixer.init()
            self.shotgun = pg.mixer.Sound(self.path + 'shotgun.wav')
            self.npc_pain = pg.mixer.Sound(self.path + 'npc_pain.wav')
            self.npc_death = pg.mixer.Sound(self.path + 'npc_death.wav')
            self.npc_shot = pg.mixer.Sound(self.path + 'npc_attack.wav')
            self.npc_shot.set_volume(0.2)
            self.player_pain = pg.mixer.Sound(self.path + 'player_pain.wav')
            self.theme = pg.mixer.music.load(self.path + 'theme.mp3')
            pg.mixer.music.set_volume(0.3)
        else:
            # Provide no-op stand-ins so calls don't fail when sound is disabled
            class _Null:
                def play(self, *args, **kwargs):
                    pass
                def set_volume(self, *args, **kwargs):
                    pass
            self.shotgun = _Null()
            self.npc_pain = _Null()
            self.npc_death = _Null()
            self.npc_shot = _Null()
            self.player_pain = _Null()