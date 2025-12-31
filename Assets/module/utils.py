
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
    if not level_data.get("level_score"): 
        print(f"Warning: Level {level_index} has no level_score defined.")
        return (
        level_data["map_length"],
        level_data["stair_position"],
        cleaned_map_data,
        level_data["player_start"].copy(),
        level_data["zombie_starts"].copy(),
        1000,
    )
    else:
        return (
        level_data["map_length"],
        level_data["stair_position"],
        cleaned_map_data,
        level_data["player_start"].copy(),
        level_data["zombie_starts"].copy(),
        level_data["level_score"],
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

# -------------------------------------------------------- #
# --------------------- CLASS HELPER --------------------- #
# -------------------------------------------------------- #
class Button:
    
    def __init__(self, x, y, width, height, text='', image_path=None, hover_image_path=None, color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER):
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
                orig_w, orig_h = img_orig.get_size()
                aspect_ratio = orig_w / orig_h
                # Tính width mới để giữ đúng tỉ lệ ảnh dựa trên height bạn nhập
                new_width = int(height * aspect_ratio)
                
                self.image = pygame.transform.scale(img_orig, (new_width, height))
                # Cập nhật rect khớp với kích thước ảnh thực tế
                self.rect = pygame.Rect(x, y, new_width, height)
                self.mask = pygame.mask.from_surface(self.image)
            except Exception as e:
                print(f"Không tải được hình ảnh {image_path}. Lỗi: {e}")

        self.hover_image = None
        if hover_image_path:
            try:
                h_orig = pygame.image.load(hover_image_path).convert_alpha()
                # Ép ảnh hover theo đúng kích thước rect đã tính
                self.hover_image = pygame.transform.scale(h_orig, (self.rect.width, self.rect.height))
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
