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
        # optional floor texture
        self.floor_tile = None
        self._floor_surface = None
        if 'FLOOR_TEXTURE_PATH' in globals() and FLOOR_TEXTURE_PATH:
            try:
                self.floor_tile = self.get_texture(FLOOR_TEXTURE_PATH, (TEXTURE_SIZE, TEXTURE_SIZE))
            except Exception:
                self.floor_tile = None

    def draw(self):
        if BIRD_VIEW:
            self.draw_bird_view()
        else:
            self.draw_background()
            self.render_game_objects()
            self.draw_player_health()
            if TOP_DOWN_OVERLAY:
                self.draw_top_down_overlay()

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
        # floor: textured if available, otherwise solid color
        if self.floor_tile:
            # perspective-correct floor sampling (coarse for performance)
            tex_w, tex_h = self.floor_tile.get_size()
            # precompute left/right ray directions
            ang_left = self.game.player.angle - HALF_FOV
            ang_right = self.game.player.angle + HALF_FOV
            dir0x, dir0y = math.cos(ang_left), math.sin(ang_left)
            dir1x, dir1y = math.cos(ang_right), math.sin(ang_right)
            # drawing in coarse steps to keep it fast
            y_step = 2
            x_step = 4
            for y in range(HALF_HEIGHT, HEIGHT, y_step):
                p = y - HALF_HEIGHT
                if p == 0:
                    continue
                row_dist = SCREEN_DIST / p
                # world coordinate at left edge for this row
                floor_x = self.game.player.x + row_dist * dir0x
                floor_y = self.game.player.y + row_dist * dir0y
                # step across the screen
                step_x = row_dist * (dir1x - dir0x) / WIDTH
                step_y = row_dist * (dir1y - dir0y) / WIDTH
                wx, wy = floor_x, floor_y
                for x in range(0, WIDTH, x_step):
                    # texture coordinates from world position
                    u = int((wx % 1.0) * tex_w) % tex_w
                    v = int((wy % 1.0) * tex_h) % tex_h
                    color = self.floor_tile.get_at((u, v))
                    pg.draw.rect(self.screen, color, (x, y, x_step, y_step))
                    wx += step_x * x_step
                    wy += step_y * x_step
        else:
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

    def draw_top_down_overlay(self):
        ow, oh = TOP_DOWN_OVERLAY_SIZE
        overlay = pg.Surface((ow, oh), pg.SRCALPHA)
        rows = self.game.map.rows
        cols = self.game.map.cols
        scale = min(ow / cols, oh / rows)
        off_x = (ow - cols * scale) / 2
        off_y = (oh - rows * scale) / 2

        # background with slight transparency
        overlay.fill((20, 20, 20, 180))

        # walls
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
            pg.draw.rect(overlay, color, (rx, ry, scale, scale))

        # autopilot route (remaining path) as polyline
        if hasattr(self.game, 'autopilot') and self.game.autopilot and self.game.autopilot.enabled:
            route = getattr(self.game.autopilot, 'route', [])
            if route:
                points = []
                # start from player's current position
                px = off_x + self.game.player.x * scale
                py = off_y + self.game.player.y * scale
                points.append((px, py))
                for cx, cy in route:
                    cxp = off_x + (cx + 0.5) * scale
                    cyp = off_y + (cy + 0.5) * scale
                    points.append((cxp, cyp))
                try:
                    pg.draw.lines(overlay, (0, 180, 255), False, points, 2)
                except Exception:
                    pass

        # draw all generated waypoints with their original colors
        if hasattr(self.game, 'autopilot') and self.game.autopilot and self.game.autopilot.enabled:
            all_wps = getattr(self.game.autopilot, 'all_waypoints', [])
            colors = globals().get('WAYPOINT_COLORS', {})
            color_list = list(colors.values()) if colors else []
            for i, (wx, wy) in enumerate(all_wps):
                wxp = off_x + (wx + 0.5) * scale
                wyp = off_y + (wy + 0.5) * scale
                color = (200, 200, 200)
                if i < len(color_list):
                    color = color_list[i]
                pg.draw.circle(overlay, color, (wxp, wyp), max(2, scale * 0.18))

        # player
        px = off_x + self.game.player.x * scale
        py = off_y + self.game.player.y * scale
        pg.draw.circle(overlay, (0, 220, 0), (px, py), max(2, scale * 0.12))

        # optional direction
        if BIRD_VIEW_SHOW_DIRECTION:
            dx = math.cos(self.game.player.angle)
            dy = math.sin(self.game.player.angle)
            pg.draw.line(overlay, (255, 255, 0), (px, py), (px + dx * scale * 0.6, py + dy * scale * 0.6), 2)

        # autopilot start/goal markers if available
        if hasattr(self.game, 'autopilot') and self.game.autopilot and self.game.autopilot.enabled:
            start = getattr(self.game.autopilot, 'start', None)
            goal = getattr(self.game.autopilot, 'goal', None)
            if start:
                sx = off_x + (start[0] + 0.5) * scale
                sy = off_y + (start[1] + 0.5) * scale
                pg.draw.circle(overlay, (0, 180, 255), (sx, sy), max(3, scale * 0.2))
            if goal:
                gx = off_x + (goal[0] + 0.5) * scale
                gy = off_y + (goal[1] + 0.5) * scale
                pg.draw.circle(overlay, (255, 80, 80), (gx, gy), max(3, scale * 0.2))

        # blit to main screen top-right
        self.screen.blit(overlay, (WIDTH - ow, 0))

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



