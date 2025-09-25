import pygame as pg
from settings import *


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 90
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)
        # bird view precomputed scale/offset
        self._bird_scale = None
        self._bird_offset = (0, 0)

    def draw(self):
        if BIRD_VIEW:
            self.draw_bird_view()
        else:
            self.draw_background()
            self.render_game_objects()
            self.draw_player_health()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    def draw_bird_view(self):
        # compute scale and offset once per new map size
        rows = self.game.map.rows
        cols = self.game.map.cols
        cell_w = WIDTH / cols
        cell_h = HEIGHT / rows
        scale = min(cell_w, cell_h)
        off_x = (WIDTH - cols * scale) / 2
        off_y = (HEIGHT - rows * scale) / 2
        self._bird_scale = scale
        self._bird_offset = (off_x, off_y)

        # clear background
        self.screen.fill((20, 20, 20))

        # draw grid walls
        for (x, y), tex_id in self.game.map.world_map.items():
            rx = off_x + x * scale
            ry = off_y + y * scale
            color = (80, 80, 80)
            if tex_id == 2:
                color = (100, 100, 120)
            elif tex_id == 3:
                color = (120, 100, 100)
            elif tex_id == 4:
                color = (100, 120, 100)
            elif tex_id == 5:
                color = (120, 120, 80)
            pg.draw.rect(self.screen, color, (rx, ry, scale, scale))

        # draw player
        px = off_x + self.game.player.x * scale
        py = off_y + self.game.player.y * scale
        pg.draw.circle(self.screen, (0, 200, 0), (px, py), max(3, scale * 0.15))
        # draw facing direction (optional)
        if BIRD_VIEW_SHOW_DIRECTION:
            dx = math.cos(self.game.player.angle)
            dy = math.sin(self.game.player.angle)
            pg.draw.line(self.screen, (255, 255, 0), (px, py), (px + dx * scale * 0.75, py + dy * scale * 0.75), 2)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }