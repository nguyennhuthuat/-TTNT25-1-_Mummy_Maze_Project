
import os
from typing import List, Tuple, Optional
from .map_collection import maps_collection
from .settings import *
import pygame
from dataclasses import dataclass
from .settings import COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_TEXT

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

def get_black_shadow_surface(frame: pygame.Surface) -> pygame.Surface:
    """Convert an original shadow surface to a black silhouette."""
    image = frame.copy()
    image.set_colorkey((0, 0, 0))
    mask = pygame.mask.from_surface(image)
    # setcolor=(0, 0, 0) -> Absolute black
    return mask.to_surface(setcolor=(0, 0, 0), unsetcolor=None)

def load_and_scale_image(TILE_SIZE, filename: str = "", is_shadow: bool = False, use_colorkey: bool = False) -> pygame.Surface:
    """Helper just for loading and scaling, NOT applying shadow logic."""
    scale_factor = TILE_SIZE / 60

    path = os.path.join("assets", "images", filename)
    surface = pygame.image.load(path).convert_alpha()
        
    new_size = (int(surface.get_width() * scale_factor), 
                int(surface.get_height() * scale_factor))
        
    if is_shadow:
        return pygame.transform.scale(surface, new_size)
    else: 
        if use_colorkey:
            surface.set_colorkey((0, 0, 0))

        return pygame.transform.smoothscale(surface, new_size)


def is_linked(map_data: list, direction:  list, facing_direction: str, gate_opened: bool = False, superdata: dict = None) -> bool:
    """
    Check if can move from 'direction' in 'facing_direction' considering walls and gates.
    
    Args:
        map_data: Map data matrix
        direction: Current position [x, y]
        facing_direction: Direction to move (UP/DOWN/LEFT/RIGHT)
        gate_opened: Current state of gate (True = opened, False = closed)
        superdata: Original map data containing gate_pos and key_pos
    
    Returns: 
        bool: True if can move, False otherwise
    """
    x = direction[0]
    y = direction[1]
    
    # Check if gate is blocking the path
    if superdata and superdata.get("gate_pos") and not gate_opened:
        gx, gy = superdata["gate_pos"]
        
        # Check if next position is the gate
        if facing_direction == UP: 
            if (x - 1, y - 2) == (gx - 1, gy - 1):
                return False
        elif facing_direction == DOWN:
            if (x - 1, y - 1) == (gx - 1, gy - 1):
                return False
    
    # Original wall checking logic
    if facing_direction == UP:
        return (y - 1 > 0) and \
               (map_data[y - 1][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and \
               (map_data[y - 2][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])
    
    if facing_direction == DOWN:
        return (y + 1 <= len(map_data[0])) and \
               (map_data[y - 1][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*']) and \
               (map_data[y][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*'])
    
    if facing_direction == LEFT:
        return (x - 1 > 0) and \
               (map_data[y - 1][x - 1] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*']) and \
               (map_data[y - 1][x - 2] not in ['r', 'br', 'tr', 't*', 'l*', 'b*'])
    
    if facing_direction == RIGHT:
        return (x + 1 <= len(map_data[0])) and \
               (map_data[y - 1][x - 1] not in ['r', 'br', 'tr', 't*', 'l*', 'b*']) and \
               (map_data[y - 1][x] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*'])
    
    return True


def get_face_direction(from_pos:  tuple, to_pos: tuple, map_data: list = None, gate_opened: bool = False, superdata: dict = None) -> str:
    """
    Determine the facing direction from one position to another.
    
    Args:
        from_pos:  Starting position (x, y)
        to_pos: Target position (x, y)
        map_data: Map data matrix
        gate_opened:  Current state of gate (True = opened, False = closed)
        superdata: Original map data containing gate_pos and key_pos
    
    Returns:
        str: Direction string (UP/DOWN/LEFT/RIGHT)
    """
    
    #----- STEP 1: EXTRACT COORDINATES -----#
    from_x, from_y = from_pos
    to_x, to_y = to_pos
    
    #----- STEP 2: DETERMINE DIRECTION BASED ON COORDINATE DIFFERENCE -----#
    # Check horizontal difference first
    if to_x < from_x: 
        return LEFT
    elif from_x < to_x:
        return RIGHT
    
    # Check vertical difference
    elif to_y < from_y: 
        return UP
    elif to_y > from_y: 
        return DOWN
    
    #----- STEP 3: IF POSITIONS ARE THE SAME, DEFAULT TO WALL SIDE -----#

    # This handles edge case where from_pos == to_pos
    # Return direction that faces a wall (for standing still animation)
    
    if map_data is not None: 
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        
        for direction in possible_directions: 
            # Check if this direction is blocked (wall or closed gate)
            if not is_linked(map_data, from_pos, direction, gate_opened, superdata):
                return direction
    
    # Fallback:  return DOWN if no map_data provided
    return DOWN


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
    level_data["map_data"] = cleaned_map_data

    return (
        level_data.get("map_length", 6),
        level_data.get("stair_position", (0, 1)),
        level_data,
        level_data.get("player_start", (1, 1)).copy(),
        level_data.get("zombie_starts", []).copy(),
        level_data.get("scorpion_starts", []).copy(),
        level_data.get("level_score", 1000),
    )

# -------------------------------------------------------- #
# --------------------- CLASS HELPER --------------------- #
# -------------------------------------------------------- #

@dataclass
class FrameSet:
    UP: List[pygame.Surface]
    DOWN: List[pygame.Surface]
    LEFT: List[pygame.Surface]
    RIGHT: List[pygame.Surface]

class Button:

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
        image_path=None,
        hover_image_path=None,
        color=COLOR_BUTTON,
        hover_color=COLOR_BUTTON_HOVER,
        keep_aspect_ratio=True,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.mask = None

        # Tải hình ảnh cho nút
        self.image = None
        if image_path:
            try:
                img_orig = pygame.image.load(image_path).convert_alpha()

                if keep_aspect_ratio:
                    orig_w, orig_h = img_orig.get_size()
                    aspect_ratio = orig_w / orig_h
                    # Tính width mới để giữ đúng tỉ lệ ảnh dựa trên height bạn nhập
                    new_width = int(height * aspect_ratio)
                    self.image = pygame.transform.scale(img_orig, (new_width, height))
                    # Cập nhật rect khớp với kích thước ảnh thực tế
                    self.rect = pygame.Rect(x, y, new_width, height)
                else:
                    self.image = pygame.transform.scale(img_orig, (width, height))
                    self.rect = pygame.Rect(x, y, width, height)

                self.mask = pygame.mask.from_surface(self.image)
            except Exception as e:
                print(f"Không tải được hình ảnh {image_path}. Lỗi: {e}")

        self.hover_image = None
        if hover_image_path:
            try:
                h_orig = pygame.image.load(hover_image_path).convert_alpha()
                # Ép ảnh hover theo đúng kích thước rect đã tính
                self.hover_image = pygame.transform.scale(
                    h_orig, (self.rect.width, self.rect.height)
                )
            except Exception as e:
                print(f"Không tải được hình ảnh hover {hover_image_path}. Lỗi: {e}")

    def draw(self, surface):
        # Trường hợp 1: Có hình ảnh
        if self.image:
            surface.blit(self.image, self.rect.topleft)
            # Vẽ đè ảnh hover lên nếu đang hover
            if self.is_hovered and self.hover_image:
                surface.blit(self.hover_image, self.rect.topleft)

        # Trường hợp 2: Không có hình ảnh (hoặc ảnh lỗi), vẽ hình chữ nhật màu
        else:
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)  # Viền trắng

        # Luôn vẽ Text nếu có (để debug hoặc dùng cho nút không ảnh)
        if self.text != "":
            text_surf = main_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """Kiểm tra xem chuột có đang ở trên nút không (theo vùng hình chữ nhật)."""
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def is_clicked(self, event):
        """Kiểm tra xem nút có được nhấp chuột trái không."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
        image_path=None,
        hover_image_path=None,
        color=COLOR_BUTTON,
        hover_color=COLOR_BUTTON_HOVER,
        keep_aspect_ratio=True,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.mask = None

        # Tải hình ảnh cho nút
        self.image = None
        if image_path:
            try:
                img_orig = pygame.image.load(image_path).convert_alpha()

                if keep_aspect_ratio:
                    orig_w, orig_h = img_orig.get_size()
                    aspect_ratio = orig_w / orig_h
                    # Tính width mới để giữ đúng tỉ lệ ảnh dựa trên height bạn nhập
                    new_width = int(height * aspect_ratio)
                    self.image = pygame.transform.scale(img_orig, (new_width, height))
                    # Cập nhật rect khớp với kích thước ảnh thực tế
                    self.rect = pygame.Rect(x, y, new_width, height)
                else:
                    self.image = pygame.transform.scale(img_orig, (width, height))
                    self.rect = pygame.Rect(x, y, width, height)

                self.mask = pygame.mask.from_surface(self.image)
            except Exception as e:
                print(f"Không tải được hình ảnh {image_path}. Lỗi: {e}")

        self.hover_image = None
        if hover_image_path:
            try:
                h_orig = pygame.image.load(hover_image_path).convert_alpha()
                # Ép ảnh hover theo đúng kích thước rect đã tính
                self.hover_image = pygame.transform.scale(
                    h_orig, (self.rect.width, self.rect.height)
                )
            except Exception as e:
                print(f"Không tải được hình ảnh hover {hover_image_path}. Lỗi: {e}")

    def draw(self, surface):
        # Trường hợp 1: Có hình ảnh
        if self.image:
            surface.blit(self.image, self.rect.topleft)
            # Vẽ đè ảnh hover lên nếu đang hover
            if self.is_hovered and self.hover_image:
                surface.blit(self.hover_image, self.rect.topleft)

        # Trường hợp 2: Không có hình ảnh (hoặc ảnh lỗi), vẽ hình chữ nhật màu
        else:
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)  # Viền trắng

        # Luôn vẽ Text nếu có (để debug hoặc dùng cho nút không ảnh)
        if self.text != "":
            text_surf = main_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """Kiểm tra xem chuột có đang ở trên nút không (theo vùng hình chữ nhật)."""
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def is_clicked(self, event):
        """Kiểm tra xem nút có được nhấp chuột trái không."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

    
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
        image_path=None,
        hover_image_path=None,
        color=COLOR_BUTTON,
        hover_color=COLOR_BUTTON_HOVER,
        keep_aspect_ratio=True,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.mask = None

        # Tải hình ảnh cho nút
        self.image = None
        if image_path:
            try:
                img_orig = pygame.image.load(image_path).convert_alpha()

                if keep_aspect_ratio:
                    orig_w, orig_h = img_orig.get_size()
                    aspect_ratio = orig_w / orig_h
                    # Tính width mới để giữ đúng tỉ lệ ảnh dựa trên height bạn nhập
                    new_width = int(height * aspect_ratio)
                    self.image = pygame.transform.scale(img_orig, (new_width, height))
                    # Cập nhật rect khớp với kích thước ảnh thực tế
                    self.rect = pygame.Rect(x, y, new_width, height)
                else:
                    self.image = pygame.transform.scale(img_orig, (width, height))
                    self.rect = pygame.Rect(x, y, width, height)

                self.mask = pygame.mask.from_surface(self.image)

            except Exception as e:
                print(f"Không tải được hình ảnh {image_path}. Lỗi: {e}")   
            self.hover_image = None
            try:
                h_orig = pygame.image.load(hover_image_path).convert_alpha()
                # Ép ảnh hover theo đúng kích thước rect đã tính
                self.hover_image = pygame.transform.scale(
                    h_orig, (self.rect.width, self.rect.height)
                )
            except Exception as e:
                print(f"Không tải được hình ảnh hover {hover_image_path}. Lỗi: {e}")  
                       
    def draw(self, surface):
        # Trường hợp 1: Có hình ảnh
        if self.image:
            surface.blit(self.image, self.rect.topleft)
            # Vẽ đè ảnh hover lên nếu đang hover
            if self.is_hovered and self.hover_image:
                surface.blit(self.hover_image, self.rect.topleft)
        
        # Trường hợp 2: Không có hình ảnh (hoặc ảnh lỗi), vẽ hình chữ nhật màu
        else:
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2) # Viền trắng
        
        # Luôn vẽ Text nếu có (để debug hoặc dùng cho nút không ảnh)
        if self.text != "":
            text_surf = main_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        """Kiểm tra xem chuột có đang ở trên nút không (theo vùng hình chữ nhật)."""
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def is_clicked(self, event):
        """Kiểm tra xem nút có được nhấp chuột trái không."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False