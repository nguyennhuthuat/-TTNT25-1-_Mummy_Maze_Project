import os
import time
from typing import List
import pygame
import random
from .utils import extract_sprite_frames, double_list
from .settings import TILE_SIZE, MARGIN_LEFT, MARGIN_TOP, UP, DOWN, LEFT, RIGHT

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
        
        # 1. Load both zombie frames and shadow frames
        self.zombie_frames, self.shadow_zombie_frames = self.load_zombie_frames()
        self.listen_frames, self.shadow_listen_frames = self.load_zombie_listening_frames()
        
        self.map_data = map_data
        self.grid_position = grid_position

        self.movement_list: List[str] = []
        self.is_standing = True # if not moving

        self.movement_frame_index = 0
        self.listening_frame_index = 0

        self.facing_direction = DOWN
        self.total_frames = 10
        
        # Current zombie frame
        self.current_frame = getattr(self.zombie_frames, self.facing_direction)[self.total_frames - 1]
        self.current_shadow_frame = getattr(self.shadow_zombie_frames, str(self.facing_direction))[self.total_frames - 1]
        
        # 2. Current shadow frame (similar to Player logic)
        self.current_shadow_frame = getattr(self.shadow_zombie_frames, str(self.facing_direction))[self.total_frames - 1]

        self.Speed = TILE_SIZE

        #----- timing variable ----- #
        self.idle_time_threshold = random.randint(3,8) # time threshold (in seconds) to trigger idle listening animation
        self.start_moving = time.time()
        self.end_moving = time.time()

        self.start_standing = time.time()
        self.end_standing = time.time()

    def get_black_shadow_surface(self, frame: pygame.Surface) -> pygame.Surface:
        """Convert a origin shadow surface to black shadow surface version."""
        image = frame.copy()
        image.set_colorkey((0,0,0))
        mask = pygame.mask.from_surface(image)
    
        # 2. Đổ lại thành hình ảnh
        # setcolor=(0, 0, 0) -> Màu đen tuyệt đối
        # unsetcolor=None    -> Vùng nền giữ nguyên trong suốt
        black_silhouette = mask.to_surface(setcolor=(0, 0, 0), unsetcolor=None)
        return black_silhouette
    
    def load_zombie_frames(self) -> ('MummyMazeZombieManager.MummyMazeFramesManager', 'MummyMazeZombieManager.MummyMazeFramesManager'): # type: ignore
        

        """Load zombie sprite sheet and split into directional frames."""

        shadow_frames_dict = self.MummyMazeFramesManager([], [], [], [])
        zombie_frames_dict = self.MummyMazeFramesManager([], [], [], [])

        # --- Load and scale zombie sprite sheet ---
        zombie_surface = pygame.image.load(os.path.join("assets", "images", "whitemummy.gif")).convert_alpha()
        zombie_surface.set_colorkey((0,0,0))
        zombie_surface = pygame.transform.scale(zombie_surface, (zombie_surface.get_width() * TILE_SIZE // 60, zombie_surface.get_height() * TILE_SIZE // 60))


        #load and scale shadow sprite sheet
        shadow_surface = pygame.image.load(os.path.join("assets", "images", "_whitemummy.gif"))
        shadow_surface = pygame.transform.scale(shadow_surface, (shadow_surface.get_width() *TILE_SIZE//60, shadow_surface.get_height() *TILE_SIZE//60))
        shadow_surface = self.get_black_shadow_surface(shadow_surface)

        # --- Extract frames ---
        zombie_frames_list = extract_sprite_frames(zombie_surface, zombie_surface.get_width() // 5, zombie_surface.get_height() // 4)
        shadow_frames_list = extract_sprite_frames(shadow_surface, shadow_surface.get_width() // 5, shadow_surface.get_height() // 4)

        # --- Assign frames for Zombie ---
        zombie_frames_dict.UP = double_list(zombie_frames_list[1:5] + [zombie_frames_list[0]])
        zombie_frames_dict.RIGHT = double_list(zombie_frames_list[6:10] + [zombie_frames_list[5]])
        zombie_frames_dict.DOWN = double_list(zombie_frames_list[11:15] + [zombie_frames_list[10]])
        zombie_frames_dict.LEFT = double_list(zombie_frames_list[16:20] + [zombie_frames_list[15]])

        # --- Assign frames for Shadow ---
        shadow_frames_dict.UP = double_list(shadow_frames_list[1:5] + [shadow_frames_list[0]])
        shadow_frames_dict.RIGHT = double_list(shadow_frames_list[6:10] + [shadow_frames_list[5]])
        shadow_frames_dict.DOWN = double_list(shadow_frames_list[11:15] + [shadow_frames_list[10]])
        shadow_frames_dict.LEFT = double_list(shadow_frames_list[16:20] + [shadow_frames_list[15]])

        return zombie_frames_dict, shadow_frames_dict
    
    def load_zombie_listening_frames(self) -> ('MummyMazePlayerManager.MummyMazeFramesManager', 'MummyMazePlayerManager.MummyMazeFramesManager'): # type: ignore

        def extract_listening_frames(sheet: pygame.Surface, frame_size: int) -> List[pygame.Surface]:
            """Extract frames from a sprite sheet given each frame's width and height."""
            sheet_width, sheet_height = sheet.get_size()
            frames: List[pygame.Surface] = []   
            
            for x in range(0, sheet_width, frame_size):
                frames.append(sheet.subsurface(pygame.Rect(x, 0, frame_size, frame_size)))

            return frames
        
        """Load player finding sprite sheet and split into directional frames."""
        

        # Load and scale player finding sprite sheet
        finding_surface = pygame.image.load(os.path.join("assets", "images", "whitelisten.gif")).convert_alpha()
        finding_surface.set_colorkey((0,0,0))
        finding_surface = pygame.transform.scale(finding_surface, (finding_surface.get_width() *TILE_SIZE//60, finding_surface.get_height() *TILE_SIZE//60))

        # load and scale shadow finding sprite sheet
        shadow_finding_surface = pygame.image.load(os.path.join("assets", "images", "_whitelisten.gif")).convert_alpha()
        shadow_finding_surface = pygame.transform.scale(shadow_finding_surface, (shadow_finding_surface.get_width() *TILE_SIZE//60, shadow_finding_surface.get_height() *TILE_SIZE//60))
        shadow_finding_surface = self.get_black_shadow_surface(shadow_finding_surface)

        finding_frames = extract_listening_frames(finding_surface, finding_surface.get_height())
        shadow_finding_frames = extract_listening_frames(shadow_finding_surface, shadow_finding_surface.get_height())

        return finding_frames, shadow_finding_frames


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
        if self.movement_list: # Nếu vẫn còn di chuyển dở thì không tính toán gì thêm
            return False

        next_pos = self.grid_position[:] # Bắt đầu từ vị trí hiện tại của zombie
        
        for _ in range(2):
            # Nếu đã bắt được người chơi thì dừng
            if next_pos == player_position:
                break
            
            # Tính khoảng cách
            diff_x = player_position[0] - next_pos[0]
            diff_y = player_position[1] - next_pos[1]

            # --- 1. Ưu tiên đi Ngang (Horizontal) ---
            if diff_x != 0:
                direction = RIGHT if diff_x > 0 else LEFT
                self.movement_list.append(direction)
                if self.zombie_can_move(next_pos, direction):
                    next_pos[0] += (1 if diff_x > 0 else -1)
            
            # --- 2. Nếu ngang thẳng hàng, đi Dọc (Vertical) ---
            # Lưu ý: Mummy Maze chỉ đi dọc khi diff_x == 0
            elif diff_y != 0:
                print("Zombie is moving", DOWN if diff_y > 0 else UP)
                direction = DOWN if diff_y > 0 else UP
                self.movement_list.append(direction)
                if self.zombie_can_move(next_pos, direction):
                    next_pos[1] += (1 if diff_y > 0 else -1)


        return len(self.movement_list) > 0
    def update_zombie(self, screen: pygame.Surface) -> None:
        """Render and animate the zombie according to its movement list."""
        move_distance_x = 0
        move_distance_y = 0
        grid_x = 0
        grid_y = 0

        if self.movement_list:
            if self.movement_frame_index == 0: # check if starting movement
                self.is_standing = False

            self.facing_direction = self.movement_list[0]
            print("Zombie is moving (1)", self.facing_direction)
            self.current_frame = getattr(self.zombie_frames, str(self.facing_direction))[self.movement_frame_index]
            self.current_shadow_frame = getattr(self.shadow_zombie_frames, str(self.facing_direction))[self.movement_frame_index]

            # Calculate movement offsets
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

            screen.blit(self.current_shadow_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1) + move_distance_x,
                                                    MARGIN_TOP + 0 + TILE_SIZE * (self.grid_position[1] - 1) + move_distance_y))
            screen.blit(self.current_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1) + move_distance_x,
                                             MARGIN_TOP + 0 + TILE_SIZE * (self.grid_position[1] - 1) + move_distance_y))

            self.movement_frame_index += 1
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                self.movement_list.pop(0)
                self.grid_position[0] += grid_x
                self.grid_position[1] += grid_y

                self.is_standing = True
                self.start_standing = time.time()  ## start standing timer
        else:

            self.current_frame = getattr(self.zombie_frames, str(self.facing_direction))[self.total_frames - 1]
            self.current_shadow_frame = getattr(self.shadow_zombie_frames, str(self.facing_direction))[self.total_frames - 1]

            if self.is_standing == True and self.facing_direction == DOWN and time.time() - self.start_standing >= self.idle_time_threshold:
                self.current_frame = self.listen_frames[self.listening_frame_index]
                self.current_shadow_frame = self.shadow_listen_frames[self.listening_frame_index]
                self.listening_frame_index += 1

                if self.listening_frame_index >= len(self.listen_frames):
                    self.listening_frame_index = 0
                    self.start_standing = time.time() ## reset standing timer
                    self.idle_time_threshold = random.randint(8,16) ## random time threshold for next finding animation


            screen.blit(self.current_shadow_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1),
                                                    MARGIN_TOP + 0 + TILE_SIZE * (self.grid_position[1] - 1)))
            screen.blit(self.current_frame, (MARGIN_LEFT + 4 + TILE_SIZE * (self.grid_position[0] - 1),
                                             MARGIN_TOP + 0 + TILE_SIZE * (self.grid_position[1] - 1)))
