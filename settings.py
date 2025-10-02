import math
import random

# game settings
RES = WIDTH, HEIGHT = 1600, 900
# RES = WIDTH, HEIGHT = 1920, 1080
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 24

PLAYER_POS = 1.5, 5  # mini_map
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
AUTOPILOT_TURN_SPEED = 0.0012  # radians per ms, slower than instant snap
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100
RANDOM_SPAWN = True  # spawn player at a random free cell center
ENEMY_COUNT = 0
TORCHES_ENABLED = False
SOUND_ENABLED = False
BIRD_VIEW = False
BIRD_VIEW_SHOW_DIRECTION = True

# headless and automation
HEADLESS = True  # if True, run without opening a window and skip flips
AUTOPILOT = True  # if True, player is controlled by auto-routing instead of keyboard
RECORD_VIDEO = True  # if True, record gameplay video with color tracking
VIDEO_OUTPUT_DIR = "recordings"  # directory to save video recordings
HEADLESS_FPS = 24  # FPS for headless rendering
WAYPOINT_COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'magenta': (255, 0, 255),
    'cyan': (0, 255, 255),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'lime': (0, 255, 0)
}
AUTOPILOT_WAYPOINTS = random.randint(1, len(WAYPOINT_COLORS))  # number of random points to visit before exit

# Shuffle the dictionary by converting to items, shuffling, then back to dict
import random
items = list(WAYPOINT_COLORS.items())
random.shuffle(items)
WAYPOINT_COLORS = dict(items)
WAYPOINT_SKIP_PROB = random.uniform(0, 1)  # probability [0,1] to skip a waypoint (optional)

# map generation
USE_PROCEDURAL_MAP = True
MAP_ROWS = 32
MAP_COLS = 32
TARGET_FLOOR_RATIO_MIN = 0.1
TARGET_FLOOR_RATIO_MAX = 0.3
ROOM_CHANCE_MIN = 0.01
ROOM_CHANCE_MAX = 0.1
ROOM_MIN = 5
ROOM_MAX = 10
TURN_PROB_MIN = 0.5
TURN_PROB_MAX = 0.9

# top-down overlay settings
TOP_DOWN_OVERLAY = True  # if True, render a mini bird's-eye overlay
TOP_DOWN_OVERLAY_SIZE = (480, 320)  # width, height in pixels

# random asset placement
RANDOM_ASSET_PATH = 'resources/sprites/animated_sprites/green_light/'  # e.g., 'resources/sprites/static_sprites/candlebra.png'
RANDOM_ASSET_IS_ANIMATED = True  # if True, use AnimatedSprite and treat path as a frame file
RANDOM_ASSET_SCALE = 0.8
RANDOM_ASSET_SHIFT = 0.16
RANDOM_ASSET_ANIMATION_TIME = 120  # ms per frame

MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

FLOOR_COLOR = (30, 30, 30)
# If set, use this texture for the floor instead of solid color
FLOOR_TEXTURE_PATH = 'resources/textures/floor.png'

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2