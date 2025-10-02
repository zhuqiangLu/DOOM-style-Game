import random

W, H = 80, 40
WALL, FLOOR = 1, 0

def carve_room(grid, cx, cy, rw, rh):
    h = len(grid); w = len(grid[0])
    x1, y1 = max(1, cx - rw//2), max(1, cy - rh//2)
    x2, y2 = min(w-2, cx + (rw-1)//2), min(h-2, cy + (rh-1)//2)
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            grid[y][x] = FLOOR

def drunkard_dungeon(w=W, h=H, seed=0, target_floor_ratio=0.35,
                     room_chance=0.04, room_min=3, room_max=7,
                     turn_prob=0.30):
    random.seed(seed)
    g = [[WALL for _ in range(w)] for _ in range(h)]
    x, y = w//2, h//2
    g[y][x] = FLOOR
    carved = 1
    target = int(w*h*target_floor_ratio)
    DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
    dx, dy = random.choice(DIRS)

    max_try = 50

    def step(dx, dy, x, y):
        nx = min(max(1, x+dx), w-2)
        ny = min(max(1, y+dy), h-2)
        return nx, ny

    while carved < target:
        max_try -= 1
        if max_try <= 0:
            break
        # occasional room
        if random.random() < room_chance:
            rw = random.randint(room_min, room_max)
            rh = random.randint(room_min, room_max)
            carve_room(g, x, y, rw, rh)

        # direction persistence
        if random.random() < turn_prob:
            dx, dy = random.choice(DIRS)

        # step & carve (with a 3-cell “fat” carve sometimes)
        x, y = step(dx, dy, x, y)
        if g[y][x] == WALL:
            g[y][x] = FLOOR
            carved += 1
        # fatten occasionally
        if random.random() < 0.2:
            for ox, oy in [(1,0),(-1,0),(0,1),(0,-1)]:
                xx, yy = x+ox, y+oy
                if 1 <= xx < w-1 and 1 <= yy < h-1 and g[yy][xx] == WALL:
                    g[yy][xx] = FLOOR
                    carved += 1

    return g

def print_map(grid):
    chars = {0:'·', 1:'#'}
    for row in grid:
        print(''.join(chars[c] for c in row))

if __name__ == "__main__":
    g = drunkard_dungeon(seed=1337)

    print_map(g)