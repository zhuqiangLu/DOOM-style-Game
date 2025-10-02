import random

W, H = 60, 30               # width x height
WALL, FLOOR = 1, 0

def make_map(w=W, h=H, seed=42, target_floor_ratio=0.40,
             clamp_edges=True, max_steps=None):
    random.seed(seed)
    grid = [[WALL for _ in range(w)] for _ in range(h)]
    x, y = w // 2, h // 2    # start in the middle (you can randomize)

    # how many floors to carve before stopping
    target_floor = int(w * h * target_floor_ratio)
    carved = 0
    grid[y][x] = FLOOR
    carved += 1

    steps = 0
    if max_steps is None:
        max_steps = w * h * 10  # safety cap

    def step(dx, dy, x, y):
        nx, ny = x + dx, y + dy
        if clamp_edges:
            nx = max(1, min(w - 2, nx))
            ny = max(1, min(h - 2, ny))
            return nx, ny
        else:
            # reject moves that go OOB; stay put instead
            if 0 < nx < w-1 and 0 < ny < h-1:
                return nx, ny
            return x, y

    DIRS = [(1,0), (-1,0), (0,1), (0,-1)]

    while carved < target_floor and steps < max_steps:
        dx, dy = random.choice(DIRS)
        x, y = step(dx, dy, x, y)
        if grid[y][x] == WALL:
            grid[y][x] = FLOOR
            carved += 1
        steps += 1

    return grid

def print_map(grid):
    chars = {0: '·', 1: '#'}
    for row in grid:
        print(''.join(chars[c] for c in row))

if __name__ == "__main__":
    g = make_map(target_floor_ratio=0.1, seed=123)
    print_map(g)