import math
import random
import sys
import pygame as pg
import os
import json
from datetime import datetime
from settings import PLAYER_SPEED, AUTOPILOT_WAYPOINTS, WAYPOINT_COLORS, AUTOPILOT_TURN_SPEED, WAYPOINT_SKIP_PROB, RECORD_VIDEO, VIDEO_OUTPUT_DIR


class AutoPilot:
    def __init__(self, game, enabled=False):
        self.game = game
        self.enabled = enabled
        self.start = None  # first waypoint (for overlay)
        self.goal = None   # last waypoint (for overlay)
        self.waypoints = []  # full list of chosen waypoints (for overlay)
        self.all_waypoints = []  # all generated waypoints (including skipped)
        self.route = []
        self.visited_waypoints = []  # track visited waypoints in order
        self.session_id = None
        self._setup_recording()
        self._pick_waypoints_and_route()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def _setup_recording(self):
        if not RECORD_VIDEO:
            return
        # Create unique session folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"session_{timestamp}"
        self.session_dir = os.path.join(VIDEO_OUTPUT_DIR, self.session_id)
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Initialize recording data
        self.recording_data = {
            "session_id": self.session_id,
            "timestamp": timestamp,
            "all_colors": list(WAYPOINT_COLORS.items()),
            "visited_waypoints": []
        }

    def _save_recording_data(self):
        if not RECORD_VIDEO or not self.session_id:
            return
        # Save current recording data
        with open(os.path.join(self.session_dir, "recording_data.json"), "w") as f:
            json.dump(self.recording_data, f, indent=2)

    def _free_cells(self):
        free = []
        for y, row in enumerate(self.game.map.mini_map):
            for x, val in enumerate(row):
                if not val:
                    free.append((x, y))
        return free

    def _pick_waypoints_and_route(self):
        free = self._free_cells()
        if len(free) < 1:
            self.start = None
            self.goal = None
            self.route = []
            return
        # build K waypoints reachable in sequence from the current cell
        k = max(1, int(AUTOPILOT_WAYPOINTS))
        # allow more colors than needed; require at least k
        if len(WAYPOINT_COLORS) < k:
            raise ValueError(f"WAYPOINT_COLORS length ({len(WAYPOINT_COLORS)}) must be >= AUTOPILOT_WAYPOINTS ({k})")
        cur_cell = (int(self.game.player.x), int(self.game.player.y))
        waypoints = []
        attempts = 0
        while len(waypoints) < k and attempts < 500:
            attempts += 1
            cand = random.choice(free)
            if waypoints and cand == waypoints[-1]:
                continue
            if cand == cur_cell:
                continue
            seg = self._build_full_route(cur_cell, cand)
            if seg and seg[-1] == cand:
                waypoints.append(cand)
                cur_cell = cand
        if not waypoints:
            self.start = None
            self.goal = None
            self.waypoints = []
            self.all_waypoints = []
            self.route = []
            return
        # store all generated waypoints for overlay display
        self.all_waypoints = waypoints.copy()
        # randomly skip waypoints with configured probability; ensure at least one remains
        if WAYPOINT_SKIP_PROB > 0:
            filtered = [wp for wp in waypoints if random.random() >= WAYPOINT_SKIP_PROB]
            if filtered:
                waypoints = filtered
            else:
                # keep at least one: choose the last generated (furthest in sequence)
                waypoints = [waypoints[-1]]
        self.start = waypoints[0]
        self.goal = waypoints[-1]
        self.waypoints = waypoints
        # stitch segments from player -> w1 -> w2 -> ...
        route = []
        cur_cell = (int(self.game.player.x), int(self.game.player.y))
        for wp in waypoints:
            seg = self._build_full_route(cur_cell, wp)
            if not seg:
                route = []
                break
            route.extend(seg)
            cur_cell = wp
        self.route = route

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
        self._pick_waypoints_and_route()

    def _advance_toward(self, target_cell):
        # Move player toward the center of the target cell with collision checks
        tx, ty = target_cell
        # aim at cell center
        target_angle = math.atan2((ty + 0.5) - self.game.player.y, (tx + 0.5) - self.game.player.x)
        # rotate gradually towards target_angle; do not move until aligned
        pa = self.game.player.angle
        # shortest angular difference in (-pi, pi]
        diff = (target_angle - pa + math.pi) % (2 * math.pi) - math.pi
        max_turn = AUTOPILOT_TURN_SPEED * self.game.delta_time
        moved = False
        if abs(diff) > 0.05:  # require alignment within ~3 degrees before moving
            if diff > 0:
                pa += min(diff, max_turn)
            else:
                pa -= min(-diff, max_turn)
            self.game.player.angle = pa % (2 * math.pi)
        else:
            # aligned enough: set precise angle and move forward
            self.game.player.angle = target_angle
            speed = PLAYER_SPEED * self.game.delta_time
            dx = math.cos(self.game.player.angle) * speed
            dy = math.sin(self.game.player.angle) * speed
            self.game.player.check_wall_collision(dx, dy)
            moved = True

    def update(self):
        if not self.enabled or not self.route:
            return
        # progress along precomputed route of cells
        target = self.route[0]
        px, py = self.game.player.x, self.game.player.y
        tx, ty = target
        # consider close enough when within a small threshold of cell center
        cx, cy = tx + 0.5, ty + 0.5
        dist_sq = (px - cx) ** 2 + (py - cy) ** 2
        # more forgiving arrival radius to avoid edge sticking
        if dist_sq < 0.2 * 0.2:
            # Record visited waypoint
            if target in self.waypoints:
                waypoint_index = self.waypoints.index(target)
                if waypoint_index < len(WAYPOINT_COLORS):
                    color_name = list(WAYPOINT_COLORS.keys())[waypoint_index]
                    color_code = list(WAYPOINT_COLORS.values())[waypoint_index]
                    self.visited_waypoints.append({
                        "waypoint": target,
                        "color_name": color_name,
                        "color_code": color_code,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.recording_data["visited_waypoints"] = self.visited_waypoints
                    self._save_recording_data()
            
            self.route.pop(0)
            if not self.route:
                # reached second (last) waypoint; exit game
                self._save_recording_data()  # Final save
                pg.quit()
                sys.exit(0)
            target = self.route[0]
        else:
            self._advance_toward(target)

