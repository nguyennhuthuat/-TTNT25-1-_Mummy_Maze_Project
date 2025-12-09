import os
import time
from typing import List, Tuple, Optional, Any
import pygame
import random
from .utils import *
from .settings import *

# Giả định import các hằng số và hàm helper
# from settings import UP, DOWN, LEFT, RIGHT, TILE_SIZE, MARGIN_LEFT, MARGIN_TOP
# from utils import FrameSet, double_list, extract_sprite_frames

class MummyMazeZombieManager:
    """
    Zombie handling: loading frames, chasing movement, and idle 'listening' animation.
    """

    def __init__(self, length: int = 6, grid_position: Optional[List[int]] = None, map_data: Any = None):
        self.length = length
        
        # Fix: Mutable default argument anti-pattern
        self.grid_position = grid_position if grid_position is not None else [1, 2]
        self.map_data = map_data

        # 1. Load Resources
        self.zombie_frames, self.shadow_zombie_frames = self.load_zombie_frames()
        self.listen_frames, self.shadow_listen_frames = self.load_zombie_listening_frames()
        self.mumwalk_sound = pygame.mixer.Sound(os.path.join("Assets", "sounds", "mumwalk60b.wav"))

        # 2. Movement State
        self.movement_list: List[str] = []
        self.is_standing: bool = True
        self.facing_direction: str = DOWN
        self.speed = TILE_SIZE  # Renamed from Speed (PEP 8)

        # 3. Animation State
        self.total_frames = 10
        self.movement_frame_index = 0
        
        # Idle/Listening State
        self.listening_frame_index = 0
        self.idle_time_threshold = random.randint(3, 8)
        self.start_standing = time.time()

        # 4. Set initial frames (Idle at start)
        self.update_current_frames(frame_index=self.total_frames - 1)

    def update_current_frames(self, frame_index: int) -> None:
        """Helper to update both sprite and shadow frames based on direction."""
        direction_key = str(self.facing_direction)
        self.current_frame = getattr(self.zombie_frames, direction_key)[frame_index]
        self.current_shadow_frame = getattr(self.shadow_zombie_frames, direction_key)[frame_index]

    def get_black_shadow_surface(self, frame: pygame.Surface) -> pygame.Surface:
        """Convert an original shadow surface to a pure black silhouette."""
        image = frame.copy()
        image.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(image)
        return mask.to_surface(setcolor=(0, 0, 0), unsetcolor=None)

    def _process_image_resource(self, filename: str) -> pygame.Surface:
        """Helper to load, scale, and set colorkey for images."""
        path = os.path.join("assets", "images", filename)
        surface = pygame.image.load(path).convert_alpha()
        scale_factor = TILE_SIZE / 60
        new_size = (int(surface.get_width() * scale_factor), 
                    int(surface.get_height() * scale_factor))
        return pygame.transform.scale(surface, new_size)

    def load_zombie_frames(self) -> Tuple[Any, Any]:
        """Load zombie sprite sheet and split into directional frames."""
        # Load Resources
        zombie_surface = self._process_image_resource("whitemummy.gif")
        zombie_surface.set_colorkey((0, 0, 0))
        
        # Load Shadow (process image then convert to black silhouette)
        shadow_surface = self._process_image_resource("_whitemummy.gif")
        shadow_surface = self.get_black_shadow_surface(shadow_surface)

        # Extract Frames
        w_frame = zombie_surface.get_width() // 5
        h_frame = zombie_surface.get_height() // 4
        
        z_frames_list = extract_sprite_frames(zombie_surface, w_frame, h_frame)
        s_frames_list = extract_sprite_frames(shadow_surface, w_frame, h_frame)

        # Helper to assign to FrameSet
        def create_frameset(source_list):
            fs = FrameSet([], [], [], [])
            fs.UP = double_list(source_list[1:5] + [source_list[0]])
            fs.RIGHT = double_list(source_list[6:10] + [source_list[5]])
            fs.DOWN = double_list(source_list[11:15] + [source_list[10]])
            fs.LEFT = double_list(source_list[16:20] + [source_list[15]])
            return fs

        return create_frameset(z_frames_list), create_frameset(s_frames_list)

    def load_zombie_listening_frames(self) -> Tuple[List[pygame.Surface], List[pygame.Surface]]:
        """Load special listening/idle animation frames."""
        
        def extract_listening_frames(sheet: pygame.Surface, frame_size: int) -> List[pygame.Surface]:
            sheet_width, _ = sheet.get_size()
            frames = []
            for x in range(0, sheet_width, frame_size):
                frames.append(sheet.subsurface(pygame.Rect(x, 0, frame_size, frame_size)))
            return frames

        # Load Resources
        finding_surface = self._process_image_resource("whitelisten.gif")
        finding_surface.set_colorkey((0, 0, 0))
        
        shadow_finding_surface = self._process_image_resource("_whitelisten.gif")
        shadow_finding_surface = self.get_black_shadow_surface(shadow_finding_surface)

        # Extract
        frame_h = finding_surface.get_height()
        finding_frames = extract_listening_frames(finding_surface, frame_h)
        shadow_finding_frames = extract_listening_frames(shadow_finding_surface, frame_h)

        return finding_frames, shadow_finding_frames

    def zombie_can_move(self, position: List[int], facing_direction: str) -> bool:
        """Check if zombie can move in facing_direction considering wall tiles."""
        x, y = position
        map_w = len(self.map_data[0])
        
        try:
            if facing_direction == UP:
                if y - 1 <= 0: return False
                return (self.map_data[y - 1][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and \
                       (self.map_data[y - 2][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])
            
            if facing_direction == DOWN:
                if y + 1 > map_w: return False
                return (self.map_data[y - 1][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*']) and \
                       (self.map_data[y][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*'])
            
            if facing_direction == LEFT:
                if x - 1 <= 0: return False
                return (self.map_data[y - 1][x - 1] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*']) and \
                       (self.map_data[y - 1][x - 2] not in ['r', 'br', 'tr', 't*', 'l*', 'b*'])
            
            if facing_direction == RIGHT:
                if x + 1 > map_w: return False
                return (self.map_data[y - 1][x - 1] not in ['r', 'br', 'tr', 't*', 'l*', 'b*']) and \
                       (self.map_data[y - 1][x] not in ['l', 'tl', 'bl', 'b*', 't*', 'r*'])
        except IndexError:
            return False
        return True

    def zombie_movement(self, player_position: List[int]) -> int:
        """Determine next movement(s) for the zombie to approach the player."""
        if self.movement_list:
            return False

        next_pos = self.grid_position[:]
        
        for _ in range(2):
            if next_pos == player_position:
                break
            
            diff_x = player_position[0] - next_pos[0]
            diff_y = player_position[1] - next_pos[1]

            # --- 1. Horizontal Priority ---
            if diff_x != 0:
                direction = RIGHT if diff_x > 0 else LEFT
                self.movement_list.append(direction)
                if self.zombie_can_move(next_pos, direction):
                    next_pos[0] += (1 if diff_x > 0 else -1)
            
            # --- 2. Vertical (Only if aligned horizontally) ---
            elif diff_y != 0:
                direction = DOWN if diff_y > 0 else UP
                self.movement_list.append(direction)
                if self.zombie_can_move(next_pos, direction):
                    next_pos[1] += (1 if diff_y > 0 else -1)

        return len(self.movement_list) > 0

    def draw_zombie(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Render zombie and shadow."""
        base_x = MARGIN_LEFT + TILE_SIZE * (self.grid_position[0] - 1) + offset_x
        base_y = MARGIN_TOP + TILE_SIZE * (self.grid_position[1] - 1) + offset_y
        
        screen.blit(self.current_shadow_frame, (base_x, base_y))
        screen.blit(self.current_frame, (base_x, base_y))

    def update_zombie(self, screen: pygame.Surface) -> None:
        """Render and animate the zombie (Moving or Idle/Listening)."""
        move_distance_x = 0
        move_distance_y = 0
        grid_dx = 0
        grid_dy = 0
        
        # --- STATE 1: MOVING ---
        if self.movement_list:
            if self.movement_frame_index == 0:
                self.is_standing = False
                self.mumwalk_sound.play()
                self.facing_direction = self.movement_list[0]

            # Update walking frames
            self.update_current_frames(self.movement_frame_index)

            # Calculate offsets
            step_pixels = (self.movement_frame_index + 1) * (self.speed // self.total_frames)
            can_move = self.zombie_can_move(self.grid_position, self.facing_direction)

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

            self.draw_zombie(screen, move_distance_x, move_distance_y)
            
            # Advance frame
            self.movement_frame_index += 1
            
            # End of step
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                self.movement_list.pop(0)
                
                if can_move:
                    self.grid_position[0] += grid_dx
                    self.grid_position[1] += grid_dy

                self.is_standing = True
                self.start_standing = time.time()

        # --- STATE 2: IDLE / LISTENING ---
        else:
            # Default idle frame (standing still)
            self.update_current_frames(self.total_frames - 1)

            # Check logic for Listening Animation (Special Idle)
            # Conditions: Standing + Facing DOWN + Time elapsed > Threshold
            is_idle_timeout = (time.time() - self.start_standing >= self.idle_time_threshold)
            
            if self.is_standing and self.facing_direction == DOWN and is_idle_timeout:
                
                # Override with listening frames
                self.current_frame = self.listen_frames[self.listening_frame_index]
                self.current_shadow_frame = self.shadow_listen_frames[self.listening_frame_index]
                
                self.listening_frame_index += 1

                # If listening animation finishes loop
                if self.listening_frame_index >= len(self.listen_frames):
                    self.listening_frame_index = 0
                    self.start_standing = time.time() # Reset timer
                    self.idle_time_threshold = random.randint(8, 16) # New random threshold

            self.draw_zombie(screen, 0, 0)