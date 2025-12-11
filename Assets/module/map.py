import os
from typing import List, Tuple
import pygame

from .settings import *

class MummyMazeMapManager:
    """Handles tile/stair drawing and tile graphics loading."""

    def __init__(self, length: int = 6, stair_position: Tuple[int, int] = (1,7), map_data: List[List[str]] = None, tile_size: int = TILE_SIZE) -> None:
        self.length = length # size of square map (length x length)
        # Map from tile id to a bound drawing method (set up using bound methods)
        # Will be populated after methods are available (we can set here using bound methods)
        self.map_data = map_data
        self.stair_positions = stair_position

        self.TILE_SIZE = tile_size

        # padding to center walls/stairs based on map size
        self.padding_left = SCREEN_WIDTH//(10*self.length) // 4
        self.padding_top = SCREEN_HEIGHT//(10*self.length) * 2 + 1

        # Load background and floor images (pygame must be initialized before calling)
        self.backdrop = pygame.image.load(os.path.join("assets", "images", "backdrop.png")).convert()
        self.backdrop = pygame.transform.scale(self.backdrop, (BACKDROP_WIDTH, BACKDROP_HEIGHT))
        self.game_floor = pygame.image.load(os.path.join("assets", "images", "floor" + str(self.length) + ".png")).convert_alpha()
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
        area_surface = pygame.image.load(os.path.join("assets", "images", "walls6.png")).convert_alpha()

        area_to_cut = pygame.Rect(0, 0, 12, 78)
        self.down_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (12*self.TILE_SIZE//60, 78*self.TILE_SIZE//60))

        area_to_cut = pygame.Rect(12, 0, 72, 18)
        self.lying_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (72*self.TILE_SIZE//60, 18*self.TILE_SIZE//60))

        area_to_cut = pygame.Rect(84, 0, 12, 78)
        self.up_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (12*self.TILE_SIZE//60, 78*self.TILE_SIZE//60))

        area_stair_surface = pygame.image.load(os.path.join("assets", "images", "stairs6.png")).convert_alpha()

        area_to_cut = pygame.Rect(2, 0, 54, 66)
        self.top_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*self.TILE_SIZE//60, 66*self.TILE_SIZE//60))

        area_to_cut = pygame.Rect(60, 0, 54, 66)
        self.right_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*self.TILE_SIZE//60, 66*self.TILE_SIZE//60))

        area_to_cut = pygame.Rect(114, 0, 54, 34)
        self.bottom_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*self.TILE_SIZE//60, 34*self.TILE_SIZE//60))

        area_to_cut = pygame.Rect(170, 0, 54, 66)
        self.left_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (54*self.TILE_SIZE//60, 66*self.TILE_SIZE//60))

    # Tile drawing methods (x and y are 1-based grid coordinates)
    def draw_top_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))

    def draw_bottom_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top))

    def draw_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))

    def draw_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))

    def draw_bottom_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top))

    def draw_top_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))

    def draw_bottom_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top))

    def draw_top_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))

    def draw_left_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top))

    def draw_right_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top))

    def draw_top_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.up_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top))

    def draw_bottom_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))
        screen.blit(self.down_standing_wall, (MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left, MARGIN_TOP + self.TILE_SIZE * y - self.padding_top))

    def draw_stair(self, screen: pygame.Surface) -> None:
        """Draw the stair graphic according to stair_positions."""
        row, col = self.stair_positions

        def draw_bottom_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + self.TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - 2
            screen_inner.blit(self.bottom_stair, (x, y))

        def draw_top_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + self.TILE_SIZE * (row_i - 1) - self.top_stair.get_width() - 3
            y = MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - self.top_stair.get_height() + self.TILE_SIZE
            screen_inner.blit(self.top_stair, (x, y))

        def draw_left_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + self.TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - 5
            screen_inner.blit(self.left_stair, (x, y))

        def draw_right_stair(screen_inner: pygame.Surface, row_i: int, col_i: int) -> None:
            x = MARGIN_LEFT + self.TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - 5
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

pygame.quit()