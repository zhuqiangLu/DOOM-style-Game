from sprite_object import *
from npc import *
from settings import ENEMY_COUNT, TORCHES_ENABLED, RANDOM_ASSET_PATH, RANDOM_ASSET_IS_ANIMATED, RANDOM_ASSET_SCALE, RANDOM_ASSET_SHIFT, RANDOM_ASSET_ANIMATION_TIME
import os
import random
from random import choices, randrange


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        # spawn npc
        self.enemies = ENEMY_COUNT  # npc count
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()

        # random asset placement will be triggered after autopilot initializes (in main)

        # sprite map
        if TORCHES_ENABLED:
            add_sprite(AnimatedSprite(game))
            add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
            add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
            add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
            add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
            add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
            add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
            add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
            add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

        # npc map
        # add_npc(SoldierNPC(game, pos=(11.0, 19.0)))
        # add_npc(SoldierNPC(game, pos=(11.5, 4.5)))
        # add_npc(SoldierNPC(game, pos=(13.5, 6.5)))
        # add_npc(SoldierNPC(game, pos=(2.0, 20.0)))
        # add_npc(SoldierNPC(game, pos=(4.0, 29.0)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 14.5)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 16.5)))
        # add_npc(CyberDemonNPC(game, pos=(14.5, 25.5)))

    def spawn_npc(self):
        for i in range(self.enemies):
                npc = choices(self.npc_types, self.weights)[0]
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                    pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self):
        # Trigger win only if enemies were configured; with 0 enemies, run infinitely
        if self.enemies and not len(self.npc_positions):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)

    def spawn_random_assets(self, asset_path, count):
        # Use all generated waypoints (including skipped ones) if available
        waypoint_cells = []
        if hasattr(self.game, 'autopilot') and self.game.autopilot and getattr(self.game.autopilot, 'all_waypoints', None):
            waypoint_cells = list(self.game.autopilot.all_waypoints)

        # fallback: choose random free cells
        if not waypoint_cells:
            waypoint_cells = self.game.map.free_cells()

        # limit to requested count
        waypoint_cells = waypoint_cells[:max(0, int(count))]

        # avoid spawning on the player cell
        taken = set()
        px, py = int(self.game.player.x), int(self.game.player.y)
        taken.add((px, py))

        # resolve animated path to a frame file if a directory is provided
        resolved_path = asset_path
        if RANDOM_ASSET_IS_ANIMATED and os.path.isdir(asset_path):
            # try common first frame name, else pick first file in directory
            candidate = os.path.join(asset_path, '0.png')
            if os.path.isfile(candidate):
                resolved_path = candidate
            else:
                files = [f for f in os.listdir(asset_path) if os.path.isfile(os.path.join(asset_path, f))]
                if files:
                    resolved_path = os.path.join(asset_path, files[0])

        # get waypoint colors for tinting
        colors = globals().get('WAYPOINT_COLORS', {})
        color_list = list(colors.values()) if colors else []
        for i, cell in enumerate(waypoint_cells):
            if cell in taken or cell in self.game.map.world_map:
                continue
            taken.add(cell)
            cx, cy = cell
            # use corresponding waypoint color for tinting
            color = color_list[i] if i < len(color_list) else None
            if RANDOM_ASSET_IS_ANIMATED:
                self.add_sprite(AnimatedSprite(self.game, path=resolved_path, pos=(cx + 0.5, cy + 0.5), scale=RANDOM_ASSET_SCALE, shift=RANDOM_ASSET_SHIFT, animation_time=RANDOM_ASSET_ANIMATION_TIME, color=color))
            else:
                self.add_sprite(SpriteObject(self.game, path=resolved_path, pos=(cx + 0.5, cy + 0.5), scale=RANDOM_ASSET_SCALE, shift=RANDOM_ASSET_SHIFT, color=color))