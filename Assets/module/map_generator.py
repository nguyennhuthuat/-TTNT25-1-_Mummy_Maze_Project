import random
import sys
import io
import os
from collections import deque

# Add the parent directory to sys.path to allow imports if run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

try:
    from .game_algorithms import Shortest_Path
except ImportError:
    # Fallback for running as script
    from Assets.module.game_algorithms import Shortest_Path


class MapGenerator:
    def __init__(self, size=6):
        self.size = size
        self.map_data = []
        self.player_start = (1, 1)
        self.stair_pos = (size, size)
        self.zombies = []
        self.scorpions = []
        self.traps = []
        self.key_pos = ()
        self.gate_pos = ()

        # Internal wall representation
        # walls_v: (r, c) -> Wall between (r, c) and (r, c+1)
        # walls_h: (r, c) -> Wall between (r, c) and (r+1, c)
        self.walls_v = set()
        self.walls_h = set()

    def generate_maze(self):
        """Generates a random maze using DFS (Recursive Backtracking)."""
        # Start with all walls present
        for r in range(self.size):
            for c in range(self.size):
                if c < self.size - 1:
                    self.walls_v.add((r, c))
                if r < self.size - 1:
                    self.walls_h.add((r, c))

        # DFS to remove walls
        visited = set()
        stack = [(0, 0)]
        visited.add((0, 0))

        while stack:
            current = stack[-1]
            r, c = current
            neighbors = []

            # Check neighbors (Up, Down, Left, Right)
            # Up
            if r > 0 and (r - 1, c) not in visited:
                neighbors.append(("U", (r - 1, c)))
            # Down
            if r < self.size - 1 and (r + 1, c) not in visited:
                neighbors.append(("D", (r + 1, c)))
            # Left
            if c > 0 and (r, c - 1) not in visited:
                neighbors.append(("L", (r, c - 1)))
            # Right
            if c < self.size - 1 and (r, c + 1) not in visited:
                neighbors.append(("R", (r, c + 1)))

            if neighbors:
                direction, next_cell = random.choice(neighbors)
                nr, nc = next_cell

                # Remove wall
                if direction == "U":
                    self.walls_h.remove((nr, nc))  # Wall between (r-1, c) and (r, c)
                elif direction == "D":
                    self.walls_h.remove((r, c))  # Wall between (r, c) and (r+1, c)
                elif direction == "L":
                    self.walls_v.remove((nr, nc))  # Wall between (r, c-1) and (r, c)
                elif direction == "R":
                    self.walls_v.remove((r, c))  # Wall between (r, c) and (r, c+1)

                visited.add(next_cell)
                stack.append(next_cell)
            else:
                stack.pop()

        # Randomly remove a few more walls to create loops (make it less perfect/harder)
        remove_count = self.size // 2
        for _ in range(remove_count):
            if self.walls_v:
                w = random.choice(list(self.walls_v))
                self.walls_v.remove(w)
            if self.walls_h:
                w = random.choice(list(self.walls_h))
                self.walls_h.remove(w)

    def convert_to_map_data(self):
        """Converts internal wall representation to game's map_data format."""
        # Initialize grid with empty sets of walls
        grid_walls = [[set() for _ in range(self.size)] for _ in range(self.size)]

        # Populate basic walls based on edges
        # (Boundary walls removed as per request)

        # Add internal walls
        for r, c in self.walls_v:
            # Wall between (r, c) and (r, c+1)
            # Prefer adding 'l' to (r, c+1)
            grid_walls[r][c + 1].add("l")

        for r, c in self.walls_h:
            # Wall between (r, c) and (r+1, c)
            # Prefer adding 't' to (r+1, c)
            grid_walls[r + 1][c].add("t")

        # Resolve conflicts (unsupported combinations)
        # Supported: t, b, l, r, tl, tr, bl, br, t*, b*, l*, r*
        # Unsupported: tb, lr, + (and combinations involving them)

        # Simple fix: If unsupported, remove one wall to make it supported.
        # This opens up the maze (removes walls), which is safe.

        for r in range(self.size):
            for c in range(self.size):
                walls = grid_walls[r][c]

                # Check for 'tb' (Top + Bottom)
                if "t" in walls and "b" in walls:
                    # Remove 'b' (Open Bottom)
                    walls.remove("b")

                # Check for 'lr' (Left + Right)
                if "l" in walls and "r" in walls:
                    # Remove 'r' (Open Right)
                    walls.remove("r")

                # Check for '+' (All 4) - unlikely but possible
                if len(walls) == 4:
                    # Remove 'b' and 'r'
                    if "b" in walls:
                        walls.remove("b")
                    if "r" in walls:
                        walls.remove("r")

        # Final conversion to strings
        self.map_data = [["" for _ in range(self.size)] for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                walls = grid_walls[r][c]
                s = ""
                if "t" in walls and "l" in walls and "r" in walls:
                    s = "b*"  # Bottom missing
                elif "b" in walls and "l" in walls and "r" in walls:
                    s = "t*"  # Top missing
                elif "t" in walls and "b" in walls and "r" in walls:
                    s = "l*"  # Left missing
                elif "t" in walls and "b" in walls and "l" in walls:
                    s = "r*"  # Right missing
                elif "t" in walls and "l" in walls:
                    s = "tl"
                elif "t" in walls and "r" in walls:
                    s = "tr"
                elif "b" in walls and "l" in walls:
                    s = "bl"
                elif "b" in walls and "r" in walls:
                    s = "br"
                elif "t" in walls:
                    s = "t"
                elif "b" in walls:
                    s = "b"
                elif "l" in walls:
                    s = "l"
                elif "r" in walls:
                    s = "r"

                self.map_data[r][c] = s

    def place_entities(self):
        """Places player, stair, and enemies."""

        # 1. Stair (Exit) - Random Edge
        # Stair must be OUTSIDE the grid.
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            self.stair_pos = (random.randint(1, self.size), 0)
        elif edge == "bottom":
            self.stair_pos = (random.randint(1, self.size), self.size + 1)
        elif edge == "left":
            self.stair_pos = (0, random.randint(1, self.size))
        elif edge == "right":
            self.stair_pos = (self.size + 1, random.randint(1, self.size))

        # Clear wall for stair
        self.open_wall_for_stair()

        # 2. Player Start - Furthest from Stair
        # Find the entrance cell inside the grid
        sx, sy = self.stair_pos
        start_node = None
        if sy == 0:  # Top
            start_node = (0, sx - 1)
        elif sy == self.size + 1:  # Bottom
            start_node = (self.size - 1, sx - 1)
        elif sx == 0:  # Left
            start_node = (sy - 1, 0)
        elif sx == self.size + 1:  # Right
            start_node = (sy - 1, self.size - 1)

        # BFS to find furthest cell
        queue = deque([(start_node, 0)])
        visited = {start_node}
        max_dist = -1
        furthest_cell = start_node

        while queue:
            (r, c), dist = queue.popleft()

            if dist > max_dist:
                max_dist = dist
                furthest_cell = (r, c)

            # Check neighbors
            # Up
            if r > 0 and (r - 1, c) not in visited:
                # Check if wall blocks UP
                curr_cell = self.map_data[r][c]
                if curr_cell not in ["t", "tl", "tr", "b*", "l*", "r*"]:
                    # Check if wall blocks DOWN from above (should match if map is consistent)
                    queue.append(((r - 1, c), dist + 1))
                    visited.add((r - 1, c))

            # Down
            if r < self.size - 1 and (r + 1, c) not in visited:
                # Check if wall blocks DOWN
                curr_cell = self.map_data[r][c]
                if curr_cell not in ["b", "bl", "br", "t*", "l*", "r*"]:
                    queue.append(((r + 1, c), dist + 1))
                    visited.add((r + 1, c))

            # Left
            if c > 0 and (r, c - 1) not in visited:
                # Check if wall blocks LEFT
                curr_cell = self.map_data[r][c]
                if curr_cell not in ["l", "tl", "bl", "t*", "b*", "r*"]:
                    queue.append(((r, c - 1), dist + 1))
                    visited.add((r, c - 1))

            # Right
            if c < self.size - 1 and (r, c + 1) not in visited:
                # Check if wall blocks RIGHT
                curr_cell = self.map_data[r][c]
                if curr_cell not in ["r", "tr", "br", "t*", "b*", "l*"]:
                    queue.append(((r, c + 1), dist + 1))
                    visited.add((r, c + 1))

        self.player_start = [
            furthest_cell[1] + 1,
            furthest_cell[0] + 1,
        ]  # 1-based [col, row]

        # 3. Enemies
        # Number of enemies based on size
        num_zombies = random.randint(1, self.size // 3)
        num_scorpions = random.randint(0, self.size // 4)

        self.zombies = []
        for _ in range(num_zombies):
            tries = 0
            while tries < 100:
                zr = random.randint(0, self.size - 1)
                zc = random.randint(0, self.size - 1)
                pos = [zc + 1, zr + 1]
                if pos != self.player_start:
                    z_type = random.randint(0, 3)
                    self.zombies.append((pos[0], pos[1], z_type))
                    break
                tries += 1

        self.scorpions = []
        for _ in range(num_scorpions):
            tries = 0
            while tries < 100:
                sr = random.randint(0, self.size - 1)
                sc = random.randint(0, self.size - 1)
                pos = [sc + 1, sr + 1]
                if pos != self.player_start and pos not in [
                    [z[0], z[1]] for z in self.zombies
                ]:
                    s_type = random.randint(0, 3)
                    self.scorpions.append((pos[0], pos[1], s_type))
                    break
                tries += 1

    def open_wall_for_stair(self):
        sx, sy = self.stair_pos
        # sx is col (1-based), sy is row (1-based)

        r, c = -1, -1
        wall_to_remove = ""

        if sy == 0:  # Top
            r, c = 0, sx - 1
            wall_to_remove = "t"
        elif sy == self.size + 1:  # Bottom
            r, c = self.size - 1, sx - 1
            wall_to_remove = "b"
        elif sx == 0:  # Left
            r, c = sy - 1, 0
            wall_to_remove = "l"
        elif sx == self.size + 1:  # Right
            r, c = sy - 1, self.size - 1
            wall_to_remove = "r"

        if r != -1:
            current = self.map_data[r][c]
            # Remove the wall char from the type
            # This is tricky because types are strings like 'tl', 'b*'
            # We need to decompose, remove, and recompose.
            walls = set()
            if "t" in current:
                walls.add("t")
            if "b" in current:
                walls.add("b")
            if "l" in current:
                walls.add("l")
            if "r" in current:
                walls.add("r")
            if current == "tl":
                walls = {"t", "l"}
            elif current == "tr":
                walls = {"t", "r"}
            elif current == "bl":
                walls = {"b", "l"}
            elif current == "br":
                walls = {"b", "r"}
            elif current == "b*":
                walls = {"t", "l", "r"}  # Wait, b* is Bottom Missing -> T, L, R
            elif current == "t*":
                walls = {"b", "l", "r"}
            elif current == "l*":
                walls = {"t", "b", "r"}
            elif current == "r*":
                walls = {"t", "b", "l"}

            if wall_to_remove in walls:
                walls.remove(wall_to_remove)

            # Recompose
            s = ""
            if "t" in walls and "l" in walls and "r" in walls:
                s = "b*"
            elif "b" in walls and "l" in walls and "r" in walls:
                s = "t*"
            elif "t" in walls and "b" in walls and "r" in walls:
                s = "l*"
            elif "t" in walls and "b" in walls and "l" in walls:
                s = "r*"
            elif "t" in walls and "l" in walls:
                s = "tl"
            elif "t" in walls and "r" in walls:
                s = "tr"
            elif "b" in walls and "l" in walls:
                s = "bl"
            elif "b" in walls and "r" in walls:
                s = "br"
            elif "t" in walls:
                s = "t"
            elif "b" in walls:
                s = "b"
            elif "l" in walls:
                s = "l"
            elif "r" in walls:
                s = "r"

            # If empty, s is ''
            self.map_data[r][c] = s

    def validate(self):
        """Checks if the map is winnable."""
        superdata = {
            "map_data": self.map_data,
            "trap_pos": self.traps,
            "key_pos": self.key_pos,
            "gate_pos": self.gate_pos,
        }

        sx, sy = self.stair_pos
        goal_cell = None
        # Stair is outside, so goal is the cell adjacent to it inside the grid
        if sy == 0:
            goal_cell = (sx, 1)
        elif sy == self.size + 1:
            goal_cell = (sx, self.size)
        elif sx == 0:
            goal_cell = (1, sy)
        elif sx == self.size + 1:
            goal_cell = (self.size, sy)

        if not goal_cell:
            return False

        # Redirect stdout to suppress print from Shortest_Path
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Run Shortest Path
        try:
            # Ensure start is a tuple
            start_pos = tuple(self.player_start)
            path = Shortest_Path(
                superdata, start_pos, goal_cell, self.zombies, self.scorpions
            )
        except Exception as e:
            sys.stdout = old_stdout
            print(f"Validation Error: {e}")
            path = []

        sys.stdout = old_stdout

        return len(path) > 0

    def create_map(self):
        """Main loop to generate a valid map."""
        attempts = 0
        while attempts < 10:
            print(f"Attempt {attempts}")
            self.walls_v.clear()
            self.walls_h.clear()
            print("Generating maze...")
            self.generate_maze()
            print("Converting...")
            self.convert_to_map_data()
            print("Placing entities...")
            self.place_entities()
            print("Validating...")

            if self.validate():
                print("Map Valid!")
                return self.get_map_dict()
            print("Map Invalid.")
            attempts += 1

        print("Failed to generate valid map after 10 attempts.")
        return None

    def get_map_dict(self):
        return {
            "name": f"Generated Map {self.size}x{self.size}",
            "map_length": self.size,
            "map_data": self.map_data,
            "player_start": self.player_start,
            "stair_position": self.stair_pos,
            "zombie_starts": self.zombies,
            "scorpion_starts": self.scorpions,
            "trap_pos": self.traps,
            "key_pos": list(self.key_pos) if self.key_pos else [],
            "gate_pos": list(self.gate_pos) if self.gate_pos else [],
            "level_score": 1000,
        }


if __name__ == "__main__":
    # Test
    gen = MapGenerator(16)
    map_dict = gen.create_map()
    if map_dict:
        print("Successfully generated map:")
        for row in map_dict["map_data"]:
            print(row)
        print("Player:", map_dict["player_start"])
        print("Stair:", map_dict["stair_position"])
        print("Zombies:", map_dict["zombie_starts"])
    else:
        print("Failed.")
