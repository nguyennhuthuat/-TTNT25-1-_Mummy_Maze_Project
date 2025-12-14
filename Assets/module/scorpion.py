import os
import time
from typing import List, Tuple, Optional, Any
import pygame
import random
from .utils import *
from .settings import *

class MummyMazeScorpionManager:
    """
    Scorpion handling: loading frames, simple chasing movement, and rendering.
    """

    def __init__(self, length: int = 6, grid_position: Optional[List[int]] = None, map_data: Any = None):
        self.length = length
        
        # Fix: Mutable default argument anti-pattern
        self.grid_position = grid_position if grid_position is not None else [1, 2]
        self.map_data = map_data

        # 1. Load Resources
        self.scorpion_frames, self.shadow_scorpion_frames = self.load_scorpion_frames()
        self.mumwalk_sound = pygame.mixer.Sound(os.path.join("Assets", "sounds", "mumwalk60b.wav"))

        # 2. Movement State
        self.movement_list: List[str] = []
        self.is_standing: bool = True
        self.facing_direction: str = DOWN
        
        # 3. Animation State
        self.total_frames = 10
        self.movement_frame_index = 0
        self.speed = TILE_SIZE  # Renamed from Speed to speed (PEP 8)

        # 4. Set initial frames
        # Sử dụng logic để lấy frame cuối cùng (idle)
        self.update_current_frames(frame_index=self.total_frames - 1)

        # 5. Timing
        # time threshold (in seconds) to trigger idle listening animation
        self.idle_time_threshold = random.randint(3, 8) 
        self.start_standing = time.time()

    def update_current_frames(self, frame_index: int) -> None:
        """Helper to update both sprite and shadow frames to avoid repetition."""
        direction_key = str(self.facing_direction)
        self.current_frame = getattr(self.scorpion_frames, direction_key)[frame_index]
        self.current_shadow_frame = getattr(self.shadow_scorpion_frames, direction_key)[frame_index]

    def get_black_shadow_surface(self, frame: pygame.Surface) -> pygame.Surface:
        """Convert an original shadow surface to a pure black silhouette."""
        image = frame.copy()
        image.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(image)
        # setcolor=(0, 0, 0) -> Absolute black
        return mask.to_surface(setcolor=(0, 0, 0), unsetcolor=None)

    def load_scorpion_frames(self) -> Tuple[Any, Any]:
        """Load scorpion sprite sheet and split into directional frames."""
        
        # --- Load and scale scorpion sprite sheet ---
        scorpion_path = os.path.join("assets", "images", "scorpion.gif")
        scorpion_surface = pygame.image.load(scorpion_path).convert_alpha()
        scorpion_surface.set_colorkey((0, 0, 0))
        
        scale_factor = TILE_SIZE / 60
        new_size = (int(scorpion_surface.get_width() * scale_factor), 
                    int(scorpion_surface.get_height() * scale_factor))
        
        scorpion_surface = pygame.transform.scale(scorpion_surface, new_size)

        # --- Load and scale shadow sprite sheet ---
        shadow_path = os.path.join("assets", "images", "_scorpion.gif")
        shadow_surface = pygame.image.load(shadow_path)
        shadow_surface = pygame.transform.scale(shadow_surface, new_size)
        shadow_surface = self.get_black_shadow_surface(shadow_surface)

        # --- Extract frames ---
        w_frame = scorpion_surface.get_width() // 5
        h_frame = scorpion_surface.get_height() // 4
        
        sc_frames = extract_sprite_frames(scorpion_surface, w_frame, h_frame)
        sh_frames = extract_sprite_frames(shadow_surface, w_frame, h_frame)

        # --- Assign frames using dictionary mapping to reduce code duplication ---
        # Assuming FrameSet structure: UP, RIGHT, DOWN, LEFT
        # Indices based on original code: UP(1-5), RIGHT(6-10), DOWN(11-15), LEFT(16-20)
        
        def create_frameset(source_list):
            fs = FrameSet([], [], [], [])
            fs.UP = double_list(source_list[1:5] + [source_list[0]])
            fs.RIGHT = double_list(source_list[6:10] + [source_list[5]])
            fs.DOWN = double_list(source_list[11:15] + [source_list[10]])
            fs.LEFT = double_list(source_list[16:20] + [source_list[15]])
            return fs

        return create_frameset(sc_frames), create_frameset(sh_frames)

    def scorpion_can_move(self, position: List[int], facing_direction: str) -> bool:
        """
        Check if scorpion can move in facing_direction considering wall tiles.
        Logic preserved from original code.
        """
        x, y = position
        map_w = len(self.map_data[0])
        # Note: In the original code, map_data usage implies map_data[y][x]
        
        # Define blocking walls for each direction based on original logic
        # format: (offset_y, offset_x, blocked_tiles_list)
        try:
            if facing_direction == UP:
                if y - 1 <= 0: return False
                tile_curr = self.map_data[y - 1][x - 1]
                tile_next = self.map_data[y - 2][x - 1]
                return (tile_curr not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and \
                       (tile_next not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])

            if facing_direction == DOWN:
                if y + 1 > map_w: return False # Note: Original used len(map_data[0]) for Y check? Kept as is.
                tile_curr = self.map_data[y - 1][x - 1]
                tile_next = self.map_data[y][x - 1]
                return (tile_curr not in ['b', 'bl', 'br', 't*', 'l*', 'r*']) and \
                       (tile_next not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*'])

            if facing_direction == LEFT:
                if x - 1 <= 0: return False
                tile_curr = self.map_data[y - 1][x - 1]
                tile_next = self.map_data[y - 1][x - 2]
                return (tile_curr not in ['l', 'tl', 'bl', 'b*', 't*', 'r*']) and \
                       (tile_next not in ['r', 'br', 'tr', 't*', 'l*', 'b*'])

            if facing_direction == RIGHT:
                if x + 1 > map_w: return False
                tile_curr = self.map_data[y - 1][x - 1]
                tile_next = self.map_data[y - 1][x]
                return (tile_curr not in ['r', 'br', 'tr', 't*', 'l*', 'b*']) and \
                       (tile_next not in ['l', 'tl', 'bl', 'b*', 't*', 'r*'])
        except IndexError:
            return False
            
        return True

    def scorpion_movement(self, player_position: List[int]) -> bool:
        """Determine next movement(s) to approach player (max 2 steps)."""
        if self.movement_list:
            return False

        next_pos = self.grid_position[:]
        
        for _ in range(2):
            if next_pos == player_position:
                break
            
            diff_x = player_position[0] - next_pos[0]
            diff_y = player_position[1] - next_pos[1]
            moved = False

            # --- 1. Horizontal Priority ---
            if diff_x != 0:
                direction = RIGHT if diff_x > 0 else LEFT
                self.movement_list.append(direction)
                if self.scorpion_can_move(next_pos, direction):
                    next_pos[0] += (1 if diff_x > 0 else -1)
                    moved = True
            
            # --- 2. Vertical (Only if aligned horizontally per Mummy Maze rules) ---
            elif diff_y != 0:
                direction = DOWN if diff_y > 0 else UP
                self.movement_list.append(direction)
                if self.scorpion_can_move(next_pos, direction):
                    next_pos[1] += (1 if diff_y > 0 else -1)
                    moved = True
            
            # If logic requires stopping if blocked, handling is implicit by just appending dir
            # but not updating next_pos for the next loop iteration.

        return len(self.movement_list) > 0

    def draw_scorpion(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Render the scorpion and its shadow."""
        base_x = MARGIN_LEFT + TILE_SIZE * (self.grid_position[0] - 1) + offset_x
        base_y = MARGIN_TOP + TILE_SIZE * (self.grid_position[1] - 1) + offset_y
        
        screen.blit(self.current_shadow_frame, (base_x, base_y))
        screen.blit(self.current_frame, (base_x, base_y))

    def update_scorpion(self, screen: pygame.Surface) -> None:
        """Render and animate the scorpion according to its movement list."""
        move_distance_x = 0
        move_distance_y = 0
        grid_dx = 0
        grid_dy = 0

        if self.movement_list:
            # --- START MOVING ---
            if self.movement_frame_index == 0:
                self.is_standing = False
                self.mumwalk_sound.play()
                # Set direction for this move step
                self.facing_direction = self.movement_list[0]

            # Update frames based on current direction and index
            self.update_current_frames(self.movement_frame_index)

            # --- CALCULATE OFFSETS ---
            # Calculate pixel offset for smooth animation
            step_pixels = (self.movement_frame_index + 1) * (self.speed // self.total_frames)
            
            can_move = self.scorpion_can_move(self.grid_position, self.facing_direction)

            if can_move:
                if self.facing_direction == UP:
                    move_distance_y = -step_pixels
                    grid_dy = -1
                elif self.facing_direction == DOWN:
                    move_distance_y = step_pixels
                    grid_dy = 1
                elif self.facing_direction == LEFT:
                    move_distance_x = -step_pixels
                    grid_dx = -1
                elif self.facing_direction == RIGHT:
                    move_distance_x = step_pixels
                    grid_dx = 1

            # Draw with offset
            self.draw_scorpion(screen, move_distance_x, move_distance_y)
            
            # --- ADVANCE FRAME ---
            self.movement_frame_index += 1
            
            # --- FINISH ONE STEP ---
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                self.movement_list.pop(0)
                
                # Update logical grid position only if movement was valid
                if can_move:
                    self.grid_position[0] += grid_dx
                    self.grid_position[1] += grid_dy

                self.is_standing = True
                self.start_standing = time.time()
        else:
            # --- IDLE STATE ---
            # Show the last frame (standing still)
            self.update_current_frames(self.total_frames - 1)
            self.draw_scorpion(screen, 0, 0)