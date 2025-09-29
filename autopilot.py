import math
import random
from settings import PLAYER_SPEED


class AutoPilot:
    def __init__(self, game, enabled=False):
        self.game = game
        self.enabled = enabled
        self.start = None
        self.goal = None
        self.route = []
        self._pick_points_and_route()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def _free_cells(self):
        free = []
        for y, row in enumerate(self.game.map.mini_map):
            for x, val in enumerate(row):
                if not val:
                    free.append((x, y))
        return free

    def _pick_points_and_route(self):
        free = self._free_cells()
        if len(free) < 2:
            self.start = None
            self.goal = None
            self.route = []
            return
        # try several times to find a reachable pair
        for _ in range(50):
            a = random.choice(free)
            b = random.choice(free)
            if a == b:
                continue
            route = self._build_full_route(a, b)
            if route and route[-1] == b:
                self.start = a
                self.goal = b
                self.route = route
                return
        # fallback to any two different points with at least one step
        self.start = free[0]
        self.goal = free[-1]
        self.route = self._build_full_route(self.start, self.goal)

    def _build_full_route(self, start, goal):
        # PathFinding.get_path returns only the next step toward goal.
        # Build the full path by stepping until we reach the goal or loop.
        path = []
        cur = start
        visited = set()
        for _ in range(10000):
            if cur == goal:
                break
            if cur in visited:
                break
            visited.add(cur)
            try:
                nxt = self.game.pathfinding.get_path(cur, goal)
            except Exception:
                return []
            if not nxt or nxt == cur:
                return []
            path.append(nxt)
            cur = nxt
        if cur != goal:
            return []
        return path

    def reset_with_new_targets(self):
        self._pick_points_and_route()

    def _advance_toward(self, target_cell):
        # Move player toward the center of the target cell with collision checks
        tx, ty = target_cell
        # aim at cell center
        angle = math.atan2((ty + 0.5) - self.game.player.y, (tx + 0.5) - self.game.player.x)
        speed = PLAYER_SPEED * self.game.delta_time
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed
        self.game.player.check_wall_collision(dx, dy)
        # rotate player to face movement direction (optional)
        self.game.player.angle = angle

    def update(self):
        if not self.enabled or not self.route:
            return
        # if player not yet at start cell, move to first waypoint
        target = self.route[0]
        px, py = self.game.player.x, self.game.player.y
        tx, ty = target
        # consider close enough when within a small threshold of cell center
        cx, cy = tx + 0.5, ty + 0.5
        dist_sq = (px - cx) ** 2 + (py - cy) ** 2
        if dist_sq < 0.05 * 0.05:
            self.route.pop(0)
            if not self.route:
                # reached final goal; pick a new pair and continue
                self.reset_with_new_targets()
                return
            target = self.route[0]
        self._advance_toward(target)

