import pygame as pg
import sys
import os
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from autopilot import AutoPilot
from settings import SOUND_ENABLED, BIRD_VIEW, RANDOM_SPAWN, RANDOM_ASSET_PATH, RECORD_VIDEO, VIDEO_OUTPUT_DIR, HEADLESS, HEADLESS_FPS


class Game:
    def __init__(self):
        if HEADLESS:
            # Set environment variables for headless rendering BEFORE pygame.init()
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            
        pg.init()
        
        # Initialize video system even in headless mode
        if HEADLESS:
            # Initialize video system with dummy driver
            pg.display.init()
            # Set a dummy display mode for headless rendering
            try:
                pg.display.set_mode((1, 1), pg.NOFRAME)
            except:
                pass
            # Create a virtual screen surface for headless rendering
            self.screen = pg.Surface(RES)
            pg.event.set_grab(False)  # No mouse grabbing in headless mode
        else:
            self.screen = pg.display.set_mode(RES)
            pg.event.set_grab(True)
            
        pg.mouse.set_visible(False)
            
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.video_recorder = None
        self.frame_count = 0
        self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        # random spawn after map is created
        if RANDOM_SPAWN:
            free = self.map.free_cells()
            import random
            if free:
                sx, sy = random.choice(free)
                # center of the cell
                self.player.x = sx + 0.5
                self.player.y = sy + 0.5
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        # attach autopilot controller
        self.autopilot = AutoPilot(self, enabled=AUTOPILOT)
        # spawn assets at all waypoints (including skipped) if configured
        if RANDOM_ASSET_PATH and hasattr(self.autopilot, 'all_waypoints') and self.autopilot.all_waypoints:
            try:
                self.object_handler.spawn_random_assets(RANDOM_ASSET_PATH, len(self.autopilot.all_waypoints))
            except Exception:
                pass
        
        # setup video recording
        if RECORD_VIDEO and hasattr(self.autopilot, 'session_dir'):
            self._setup_video_recording()
            
        if SOUND_ENABLED:
            pg.mixer.music.play(-1)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        
        if not HEADLESS:
            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
        else:
            # In headless mode, use a fixed delta time and FPS
            self.delta_time = self.clock.tick(HEADLESS_FPS)

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        if not BIRD_VIEW:
            self.weapon.draw()
        # self.map.draw()
        # self.player.draw()
        
        # Record frame for video
        if RECORD_VIDEO and self.video_recorder:
            self._record_frame()

    def check_events(self):
        self.global_trigger = False
        
        if HEADLESS:
            # In headless mode, simulate events
            self.global_trigger = True
        else:
            # Normal event handling for GUI mode
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == self.global_event:
                    self.global_trigger = True
                self.player.single_fire_event(event)

    def _setup_video_recording(self):
        """Setup video recording using pygame's image save functionality"""
        if not RECORD_VIDEO or not hasattr(self.autopilot, 'session_dir'):
            return
        os.makedirs(self.autopilot.session_dir, exist_ok=True)
        self.video_recorder = {
            'session_dir': self.autopilot.session_dir,
            'frame_count': 0
        }

    def _record_frame(self):
        """Record current frame as image"""
        if not self.video_recorder:
            return
        frame_path = os.path.join(
            self.video_recorder['session_dir'], 
            f"frame_{self.video_recorder['frame_count']:06d}.png"
        )
        pg.image.save(self.screen, frame_path)
        self.video_recorder['frame_count'] += 1

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
