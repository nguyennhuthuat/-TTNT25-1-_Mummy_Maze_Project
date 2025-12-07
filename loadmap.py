import os
import time
from typing import List, Optional, Tuple

import pygame

from maps import maps_collection  # Import a collection of maps

# Direction constants
RIGHT = "RIGHT"
LEFT = "LEFT"
UP = "UP"
DOWN = "DOWN"

# Layout constants (kept module-level so classes can use them)
TILE_SIZE = 48  # Size of each tile in the grid !!!!!!!! CHANGE WHEN LOADING DIFFERENT MAP SIZES !!!!!!!!!
BACKDROP_WIDTH = 657 #575
BACKDROP_HEIGHT = 638 #558
GAME_FLOOR_WIDTH = 480
GAME_FLOOR_HEIGHT = 480
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 670
MARGIN_LEFT = 88 + (SCREEN_WIDTH - BACKDROP_WIDTH) // 2
MARGIN_TOP = 106 + (SCREEN_HEIGHT - BACKDROP_HEIGHT) // 2

# --------------------------------------------------- #
# --------------------- HELPERS --------------------- #
# --------------------------------------------------- #
def clean_map_data(map_data: List[List[str]]) -> List[List[str]]:
    """Return a cleaned copy of map_data with whitespace stripped from each tile id."""
    return [[(cell or "").strip() for cell in col] for col in map_data]


def extract_sprite_frames(sheet: pygame.Surface, frame_width: int, frame_height: int) -> List[pygame.Surface]:
    """Extract frames from a sprite sheet given each frame's width and height."""
    sheet_width, sheet_height = sheet.get_size()
    frames: List[pygame.Surface] = []
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frames.append(sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height)))
    return frames

def double_list(input_list: List[pygame.Surface]) -> List[pygame.Surface]:
    """Duplicate each element in the list (used to expand animation frames)."""
    return [item for item in input_list for _ in range(2)]


# ------------------------------------------------------- #
# --------------------- MAP MANAGER --------------------- #
# ------------------------------------------------------- #
class MummyMazeMapManager:
    """Handles tile/stair drawing and tile graphics loading."""

    def __init__(self, length: int, stair_position: Tuple[int, int], map_data: List[List[str]]):
        self.length = length # size of square map (length x length)
        # Map from tile id to a bound drawing method (set up using bound methods)
        # Will be populated after methods are available (we can set here using bound methods)
        self.map_data = map_data
        self.stair_positions = stair_position

        # padding to center walls/stairs based on map size
        self.padding_left = SCREEN_WIDTH//(10*self.length) // 4
        self.padding_top = SCREEN_HEIGHT//(10*self.length) * 2 + 1

        # Load background and floor images (pygame must be initialized before calling)
        self.backdrop = pygame.image.load(os.path.join("assets", "image", "backdrop.png")).convert()
        self.backdrop = pygame.transform.scale(self.backdrop, (BACKDROP_WIDTH, BACKDROP_HEIGHT))
        self.game_floor = pygame.image.load(os.path.join("assets", "image", "floor" + str(self.length) + ".png")).convert_alpha()
        self.game_floor = pygame.transform.scale(self.game_floor, (GAME_FLOOR_WIDTH, GAME_FLOOR_HEIGHT))

        # Prepare tile images
        self.load_tiles()

        # Populate the database mapping tile ids to bound functions
        self.database = {
            't': self.draw_top_wall_tile,
            'b': self.draw_bottom_wall_tile,
            'l': self.draw_left_wall_tile,
            'r': self.draw_right_wall_tile,
            'tr': self.draw_top_right_wall_tile,
            'tl': self.draw_top_left_wall_tile,
            'br': self.draw_bottom_right_wall_tile,
            'bl': self.draw_bottom_left_wall_tile,
            'l*': self.draw_left_t_wall_tile,
            'r*': self.draw_right_t_wall_tile,
            't*': self.draw_top_t_wall_tile,
            'b*': self.draw_bottom_t_wall_tile,
        }

    def load_tiles(self) -> None:
        """Cut and scale wall/stair images from spritesheets according to map size."""
        area_surface = pygame.image.load(os.path.join("assets", "image", "walls6.png")).convert_alpha()

        area_to_cut = pygame.Rect(0, 0, 12, 78)
        self.down_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (12*TILE_SIZE//60, 78*TILE_SIZE//60))

        area_to_cut = pygame.Rect(12, 0, 72, 18)
        self.lying_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (72*TILE_SIZE//60, 18*TILE_SIZE//60))

        area_to_cut = pygame.Rect(84, 0, 12, 78)
        self.up_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (12*TILE_SIZE//60, 78*TILE_SIZE//60))

        area_stair_surface = pygame.image.load(os.path.join("assets", "image", "stairs6.png")).convert_alpha()

        area_to_cut = pygame.Rect(2, 0, 54, 66)
        self.top_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*TILE_SIZE//60, 66*TILE_SIZE//60))

        area_to_cut = pygame.Rect(60, 0, 54, 66)
        self.right_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*TILE_SIZE//60, 66*TILE_SIZE//60))

        area_to_cut = pygame.Rect(114, 0, 54, 34)
        self.bottom_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*TILE_SIZE//60, 34*TILE_SIZE//60))

        area_to_cut = pygame.Rect(170, 0, 54, 66)
        self.left_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*TILE_SIZE//60, 66*TILE_SIZE//60))

    # Tile drawing methods (x and y are 1-based grid coordinates)
    def draw_top_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))

    def draw_bottom_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y + TILE_SIZE - self.padding_top))

    def draw_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))

    def draw_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x + TILE_SIZE - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))

    def draw_bottom_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y + TILE_SIZE - self.padding_top))

    def draw_top_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))

    def draw_bottom_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + TILE_SIZE * x + TILE_SIZE - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y + TILE_SIZE - self.padding_top))

    def draw_top_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x + TILE_SIZE - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))

    def draw_left_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + TILE_SIZE * x + TILE_SIZE - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y + TILE_SIZE - self.padding_top))

    def draw_right_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y + TILE_SIZE - self.padding_top))

    def draw_top_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + TILE_SIZE * x + TILE_SIZE - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y + TILE_SIZE - self.padding_top))

    def draw_bottom_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + TILE_SIZE * x + TILE_SIZE - self.padding_left, MARGIN_TOP + TILE_SIZE * y - self.padding_top))

    def draw_stair(self, screen: pygame.Surface) -> None:
        """Draw the stair graphic according to stair_positions."""
        row, col = self.stair_positions

        def draw_bottom_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + TILE_SIZE * (col_i - 1) - 2
            screen_inner.blit(self.bottom_stair, (x, y))

        def draw_top_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + TILE_SIZE * (row_i - 1) - self.top_stair.get_width() - 3
            y = MARGIN_TOP + TILE_SIZE * (col_i - 1) - self.top_stair.get_height() + TILE_SIZE
            screen_inner.blit(self.top_stair, (x, y))

        def draw_left_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + TILE_SIZE * (col_i - 1) - 5
            screen_inner.blit(self.left_stair, (x, y))

        def draw_right_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + TILE_SIZE * (col_i - 1) - 5
            screen_inner.blit(self.right_stair, (x, y))

        # Check position and draw corresponding stair
        if col == len(self.map_data[0]) + 1:
            draw_bottom_stair(screen, row, col)
        elif col == 0:
            draw_top_stair(screen, row, col)
        elif row == 0:
            draw_left_stair(screen, row, col)
        elif row == len(self.map_data[0]) + 1:
            draw_right_stair(screen, row, col)
        else:
            print(f"Warning: stair position {self.stair_positions} is invalid. No stair drawn.")
            print("length of map_data:", len(self.map_data[0]))
    def draw_map(self, screen: pygame.Surface) -> None:
        screen.blit(self.backdrop, ((SCREEN_WIDTH - BACKDROP_WIDTH) // 2, (SCREEN_HEIGHT - BACKDROP_HEIGHT) // 2))
        screen.blit(self.game_floor, (MARGIN_LEFT, MARGIN_TOP))
        self.draw_stair(screen)

    def draw_walls(self, screen: pygame.Surface) -> None:
        """Draw all walls according to map_data."""
        for col_index, col in enumerate(self.map_data):
            for row_index, tile_id in enumerate(col):
                tid = (tile_id or "").strip()
                if tid and (tid in self.database):
                    # Call the bound drawing function
                    self.database[tid](screen, row_index + 1, col_index + 1)
                elif tid:
                    # If tile id is unknown, warn and skip
                    print(f"Warning: tile_id '{tid}' at ({col_index}, {row_index}) not found in database. Skipping drawing.")


# ---------------------------------------------------------- #
# --------------------- PLAYER MANAGER --------------------- #
# ---------------------------------------------------------- #
class MummyMazePlayerManager:
    """Player handling: loading frames, movement, and rendering."""

    class MummyMazeFramesManager:
        def __init__(self, UP, DOWN, LEFT, RIGHT):
            self.UP = UP
            self.DOWN = DOWN
            self.LEFT = LEFT
            self.RIGHT = RIGHT

    def __init__(self, length: int, grid_position: List[int], map_data: List[List[str]]):
        self.length = length
        self.player_frames = self.load_player_images()
        self.map_data = map_data

        self.grid_position = grid_position  # [row, column] position of the player in the grid

        self.movement_list: List[str] = []
        self.movement_frame_index = 0
        self.facing_direction = DOWN
        self.total_frames = 10
        self.current_frame = getattr(self.player_frames, self.facing_direction)[self.total_frames - 1]
        self.Speed = TILE_SIZE

    def get_player_position(self, grid_position: List[int]) -> List[int]:
        """Return pixel (x, y) for the given grid_position (helper)."""
        return [MARGIN_LEFT + TILE_SIZE * (grid_position[0] - 1) + 4, MARGIN_TOP + TILE_SIZE * (grid_position[1] - 1) + 4]

    def load_player_images(self) -> 'MummyMazePlayerManager.MummyMazeFramesManager':
        """Load player sprite sheet and split into directional frames."""
        player_surface = pygame.image.load(os.path.join("assets", "image", "explorer6.png")).convert_alpha()
        player_surface = pygame.transform.scale(player_surface, (player_surface.get_width() *TILE_SIZE//60, player_surface.get_height() *TILE_SIZE//60))

        player_frame = extract_sprite_frames(player_surface, player_surface.get_width() // 5, player_surface.get_height() // 4)
        player_go_up_frames = player_frame[1:5] + [player_frame[0]]
        player_go_right_frames = player_frame[6:10] + [player_frame[5]]
        player_go_down_frames = player_frame[11:15] + [player_frame[10]]
        player_go_left_frames = player_frame[16:20] + [player_frame[15]]

        return self.MummyMazeFramesManager(
            double_list(player_go_up_frames),
            double_list(player_go_down_frames),
            double_list(player_go_left_frames),
            double_list(player_go_right_frames),
        )

    def player_can_move(self, direction: List[int], facing_direction: str) -> bool:
        """Check if player can move in facing_direction considering wall tiles."""
        x = direction[0]
        y = direction[1]
        if facing_direction == UP:
            return (y - 1 > 0) and (self.map_data[y - 1][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and (
                self.map_data[y - 2][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])
        if facing_direction == DOWN:
            return (y + 1 <= len(self.map_data[0])) and (self.map_data[y - 1][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*']) and (
                self.map_data[y][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*'])
        if facing_direction == LEFT:
            return (x - 1 > 0) and (self.map_data[y - 1][x - 1] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*']) and (
                self.map_data[y - 1][x - 2] not in ['r', 'br', 'tr', 't*', 'l*', 'b*'])
        if facing_direction == RIGHT:
            return (x + 1 <= len(self.map_data[0])) and (self.map_data[y - 1][x - 1] not in ['r', 'br', 'tr', 't*', 'l*', 'b*']) and (
                self.map_data[y - 1][x] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*'])
        return True

    def update_player(self, screen: pygame.Surface) -> bool:
        """
        Update player animation and position.
        Returns True when a movement step completes.
        """
        move_completed = False
        move_distance_x = 0
        move_distance_y = 0
        grid_x = 0
        grid_y = 0

        if self.movement_list:
            self.facing_direction = self.movement_list[0]
            self.current_frame = getattr(self.player_frames, str(self.facing_direction))[self.movement_frame_index]

            if self.player_can_move(self.grid_position, self.facing_direction):
                if self.facing_direction == UP:
                    move_distance_y = - (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_y = -1
                elif self.facing_direction == DOWN:
                    move_distance_y = (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_y = 1
                elif self.facing_direction == LEFT:
                    move_distance_x = - (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_x = -1
                elif self.facing_direction == RIGHT:
                    move_distance_x = (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_x = 1

            screen.blit(self.current_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1) + move_distance_x,
                                             MARGIN_TOP + 4 + TILE_SIZE * (self.grid_position[1] - 1) + move_distance_y))

            self.movement_frame_index += 1
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                self.movement_list.pop(0)
                self.grid_position[0] += grid_x
                self.grid_position[1] += grid_y
                move_completed = True
        else:
            screen.blit(self.current_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1),
                                             MARGIN_TOP + 4 + TILE_SIZE * (self.grid_position[1] - 1)))

        return move_completed


# ---------------------------------------------------------- #
# --------------------- ZOMBIE MANAGER --------------------- #
# ---------------------------------------------------------- #
class MummyMazeZombieManager:
    """Zombie handling: loading frames, simple chasing movement, and rendering."""

    class MummyMazeFramesManager:
        def __init__(self, UP, DOWN, LEFT, RIGHT):
            self.UP = UP
            self.DOWN = DOWN
            self.LEFT = LEFT
            self.RIGHT = RIGHT

    def __init__(self, length: int, grid_position: List[int], map_data: List[List[str]]):
        self.length = length
        self.zombie_frames = self.load_zombie_images()
        self.map_data = map_data

        self.grid_position = grid_position

        self.movement_list: List[str] = []
        self.movement_frame_index = 0
        self.facing_direction = DOWN
        self.total_frames = 10
        self.current_frame = getattr(self.zombie_frames, self.facing_direction)[self.total_frames - 1]
        self.Speed = TILE_SIZE

    def get_zombie_position(self, grid_position: List[int]) -> List[int]:
        return [MARGIN_LEFT + TILE_SIZE * (grid_position[0] - 1) + 4, MARGIN_TOP + TILE_SIZE * (grid_position[1] - 1) + 4]

    def load_zombie_images(self) -> 'MummyMazeZombieManager.MummyMazeFramesManager':
        zombie_surface = pygame.image.load(os.path.join("assets", "image", "mummy_white6.png")).convert_alpha()
        zombie_surface = pygame.transform.scale(zombie_surface, (zombie_surface.get_width() *TILE_SIZE//60, zombie_surface.get_height() *TILE_SIZE//60))

        zombie_frame = extract_sprite_frames(zombie_surface, zombie_surface.get_width() // 5, zombie_surface.get_height() // 4)

        zombie_go_up_frames = zombie_frame[1:5] + [zombie_frame[0]]
        zombie_go_right_frames = zombie_frame[6:10] + [zombie_frame[5]]
        zombie_go_down_frames = zombie_frame[11:15] + [zombie_frame[10]]
        zombie_go_left_frames = zombie_frame[16:20] + [zombie_frame[15]]

        return self.MummyMazeFramesManager(
            double_list(zombie_go_up_frames),
            double_list(zombie_go_down_frames),
            double_list(zombie_go_left_frames),
            double_list(zombie_go_right_frames),
        )

    def zombie_can_move(self, direction: List[int], facing_direction: str) -> bool:
        """Check if zombie can move in facing_direction considering wall tiles."""
        x = direction[0]
        y = direction[1]
        if facing_direction == UP:
            return (y - 1 > 0) and (self.map_data[y - 1][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and (
                self.map_data[y - 2][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])
        if facing_direction == DOWN:
            return (y + 1 <= len(self.map_data[0])) and (self.map_data[y - 1][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*']) and (
                self.map_data[y][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*'])
        if facing_direction == LEFT:
            return (x - 1 > 0) and (self.map_data[y - 1][x - 1] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*']) and (
                self.map_data[y - 1][x - 2] not in ['r', 'br', 'tr', 't*', 'l*', 'b*'])
        if facing_direction == RIGHT:
            return (x + 1 <= len(self.map_data[0])) and (self.map_data[y - 1][x - 1] not in ['r', 'br', 'tr', 't*', 'l*', 'b*']) and (
                self.map_data[y - 1][x] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*'])
        return True

    def zombie_movement(self, player_position: List[int]) -> bool:
        """Determine next movement(s) for the zombie to approach the player (up to 2 steps)."""
        if self.movement_list:
            return False

        next_zombie_position = self.grid_position[:]
        for _ in range(2):
            if next_zombie_position == player_position:
                break

            moved_this_step = False

            # Prefer horizontal movement
            if player_position[0] > next_zombie_position[0] and self.zombie_can_move(next_zombie_position, RIGHT):
                self.movement_list.append(RIGHT)
                next_zombie_position[0] += 1
                moved_this_step = True
            elif player_position[0] > next_zombie_position[0] and not self.zombie_can_move(next_zombie_position, RIGHT):
                self.facing_direction = RIGHT
                continue
            elif player_position[0] < next_zombie_position[0] and self.zombie_can_move(next_zombie_position, LEFT):
                self.movement_list.append(LEFT)
                next_zombie_position[0] -= 1
                moved_this_step = True
            elif player_position[0] < next_zombie_position[0] and not self.zombie_can_move(next_zombie_position, LEFT):
                self.facing_direction = LEFT
                continue
            else:
                if player_position[1] > next_zombie_position[1] and self.zombie_can_move(next_zombie_position, DOWN):
                    self.movement_list.append(DOWN)
                    next_zombie_position[1] += 1
                    moved_this_step = True
                elif player_position[1] < next_zombie_position[1] and self.zombie_can_move(next_zombie_position, UP):
                    self.movement_list.append(UP)
                    next_zombie_position[1] -= 1
                    moved_this_step = True

            if not moved_this_step:
                # Set facing direction toward player
                if player_position[0] > next_zombie_position[0]:
                    self.facing_direction = RIGHT
                elif player_position[0] < next_zombie_position[0]:
                    self.facing_direction = LEFT
                else:
                    if player_position[1] > next_zombie_position[1]:
                        self.facing_direction = DOWN
                    elif player_position[1] < next_zombie_position[1]:
                        self.facing_direction = UP
                break

        return len(self.movement_list) > 0

    def update_zombie(self, screen: pygame.Surface) -> None:
        """Render and animate the zombie according to its movement list."""
        move_distance_x = 0
        move_distance_y = 0
        grid_x = 0
        grid_y = 0

        if self.movement_list:
            self.facing_direction = self.movement_list[0]
            self.current_frame = getattr(self.zombie_frames, str(self.facing_direction))[self.movement_frame_index]

            if self.zombie_can_move(self.grid_position, self.facing_direction):
                if self.facing_direction == UP:
                    move_distance_y = - (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_y = -1
                elif self.facing_direction == DOWN:
                    move_distance_y = (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_y = 1
                elif self.facing_direction == LEFT:
                    move_distance_x = - (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_x = -1
                elif self.facing_direction == RIGHT:
                    move_distance_x = (self.movement_frame_index + 1) * (self.Speed // self.total_frames)
                    grid_x = 1

            screen.blit(self.current_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1) + move_distance_x,
                                             MARGIN_TOP + 4 + TILE_SIZE * (self.grid_position[1] - 1) + move_distance_y))

            self.movement_frame_index += 1
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                self.movement_list.pop(0)
                self.grid_position[0] += grid_x
                self.grid_position[1] += grid_y
        else:
            # Idle frame based on facing direction
            self.current_frame = getattr(self.zombie_frames, self.facing_direction)[self.total_frames - 1]
            screen.blit(self.current_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1),
                                             MARGIN_TOP + 4 + TILE_SIZE * (self.grid_position[1] - 1)))


# ------------------------------------------------------- #
# --------------------- LEVEL HELPER--------------------- #
# ------------------------------------------------------- #
def get_winning_position(stair_pos: Tuple[int, int], map_len: int) -> Optional[List[int]]:
    """Determines the grid cell in front of the stair to win."""
    row, col = stair_pos
    if col == 0:  # Stair is at the top edge
        return [row, 1]
    elif col == map_len + 1:  # Stair is at the bottom edge
        return [row, map_len]
    elif row == 0:  # Stair is at the left edge
        return [1, col]
    elif row == map_len + 1:  # Stair is at the right edge
        return [map_len, col]
    return None

def load_level(level_index: int):
    """Load a level from maps_collection and return its components (cleaned)."""
    if level_index < 0 or level_index >= len(maps_collection):
        print(f"Error: Level {level_index} is out of range.")
        return None, None, None, None, None

    level_data = maps_collection[level_index]
    cleaned_map_data = clean_map_data(level_data["map_data"])
    return (
        level_data["map_length"],
        level_data["stair_position"],
        cleaned_map_data,
        level_data["player_start"],
        level_data["zombie_starts"],
    )

# ----------------------------------------------------- #
# --------------------- MAIN LOOP --------------------- #
# ----------------------------------------------------- #
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Load Map Example")
    clock = pygame.time.Clock()

    current_level_index = 9
    map_length, stair_position, map_data, player_start, zombie_starts = load_level(current_level_index)
    winning_position = get_winning_position(stair_position, map_length)

    MummyMazeMap = MummyMazeMapManager(map_length, stair_position, map_data)
    MummyExplorer = MummyMazePlayerManager(map_length, player_start, map_data)
    MummyZombies = [MummyMazeZombieManager(map_length, pos, map_data) for pos in zombie_starts]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not MummyExplorer.movement_list:
                        MummyExplorer.movement_list.append(UP)
                        MummyExplorer.facing_direction = UP
                elif event.key == pygame.K_DOWN:
                    if not MummyExplorer.movement_list:
                        MummyExplorer.movement_list.append(DOWN)
                        MummyExplorer.facing_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    if not MummyExplorer.movement_list:
                        MummyExplorer.movement_list.append(LEFT)
                        MummyExplorer.facing_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    if not MummyExplorer.movement_list:
                        MummyExplorer.movement_list.append(RIGHT)
                        MummyExplorer.facing_direction = RIGHT

        MummyMazeMap.draw_map(screen)
        player_turn_completed = MummyExplorer.update_player(screen)
        for zombie in MummyZombies:
            zombie.update_zombie(screen)
        MummyMazeMap.draw_walls(screen)

        if player_turn_completed:
            for zombie in MummyZombies:
                zombie.zombie_movement(MummyExplorer.grid_position)

        # Check for win condition
        if winning_position and MummyExplorer.grid_position == winning_position:
            print("You Won! Loading next level...")
            current_level_index += 1
            if current_level_index < len(maps_collection):
                map_length, stair_position, map_data, player_start, zombie_starts = load_level(current_level_index)
                winning_position = get_winning_position(stair_position, map_length)

                MummyMazeMap = MummyMazeMapManager(map_length, stair_position, map_data)
                MummyExplorer = MummyMazePlayerManager(map_length, player_start, map_data)
                MummyZombies = [MummyMazeZombieManager(map_length, pos, map_data) for pos in zombie_starts]
            else:
                print("Congratulations! You have completed all levels!")
                running = False

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.03)

    pygame.quit()


if __name__ == "__main__":
    main()