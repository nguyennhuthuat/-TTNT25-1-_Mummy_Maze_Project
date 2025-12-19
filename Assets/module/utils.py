
from typing import List, Tuple, Optional
from .map_collection import maps_collection
from .settings import *
import pygame
from dataclasses import dataclass

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
# --------------------- LEVEL HELPER--------------------- #
# ------------------------------------------------------- #
def get_winning_position(stair_pos: Tuple[int, int], map_len: int) -> Optional[List[int]]:
    """Determines the grid cell in front of the stair to win."""
    row, col = stair_pos
    if col == 0:  # Stair is at the top edge
        return [row, 1],  UP
    elif col == map_len + 1:  # Stair is at the bottom edge
        return [row, map_len], DOWN
    elif row == 0:  # Stair is at the left edge
        return [1, col], LEFT
    elif row == map_len + 1:  # Stair is at the right edge
        return [map_len, col], RIGHT
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


# --------------------------------------------------- #
# --------------------- TESTING --------------------- #
# --------------------------------------------------- #

@dataclass
class FrameSet:
    UP: List[pygame.Surface]
    DOWN: List[pygame.Surface]
    LEFT: List[pygame.Surface]
    RIGHT: List[pygame.Surface]