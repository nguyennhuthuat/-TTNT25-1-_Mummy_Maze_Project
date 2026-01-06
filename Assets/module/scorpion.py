import os
import time
from typing import List, Tuple, Optional, Any
import pygame
import random
from .utils import *
from .settings import *
from .game_algorithms import generate_next_scorpion_positions


class MummyMazeScorpionManager:
    """
    Scorpion handling: loading frames, chasing movement.
    """

    def __init__(self, length: int = 6, grid_position: List[int] = None, data: Any = None, tile_size: int = TILE_SIZE) -> None:
        self.length = length
        self.TILE_SIZE = tile_size

        
        # Fix: Mutable default argument anti-pattern
        self.grid_position = [grid_position[0], grid_position[1]] if grid_position is not None else [1, 2]
        self.scorpion_type = grid_position[2] if grid_position is not None and len(grid_position) > 2 else 0 # Default type 0
        
        self.map_data = data["map_data"] if data and "map_data" in data else []
        self.__superdata = data

        # 1. Load Resources
        self.scorpion_frames, self.shadow_scorpion_frames = self.load_scorpion_frames()
        self.scorwalk_sound = pygame.mixer.Sound(os.path.join("Assets", "sounds", "scorpwalk1.wav"))

        # 2. Movement State
        self.movement_list: List[str] = []
        self.is_standing: bool = True
        self.facing_direction: str = DOWN
        self.speed = self.TILE_SIZE  # Renamed from Speed (PEP 8)

        # 3. Animation State
        self.total_frames = 10
        self.movement_frame_index = 0
    

        # 4. Set initial frames (Idle at start)
        self.update_current_frames(frame_index=self.total_frames - 1)

        # 10x10 map movement speed 
        self.move10 = {0: 0, 1: 4, 2: 8, 3: 13, 4: 18, 5: 23, 6: 28, 7: 33, 8: 38, 9: 43, 10: 48, 11: 0,}

    def get_x(self):
        return self.grid_position[0]
    
    def get_y(self):
        return self.grid_position[1]

    def update_current_frames(self, frame_index: int) -> None:
        """Helper to update both sprite and shadow frames based on direction."""
        direction_key = str(self.facing_direction)
        self.current_frame = getattr(self.scorpion_frames, direction_key)[frame_index]
        self.current_shadow_frame = getattr(self.shadow_scorpion_frames, direction_key)[frame_index]

    def get_black_shadow_surface(self, frame: pygame.Surface) -> pygame.Surface:
        """Convert an original shadow surface to a pure black silhouette."""
        image = frame.copy()
        image.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(image)
        return mask.to_surface(setcolor=(0, 0, 0), unsetcolor=None)

    def _load_and_scale_image(self, filename: str = "", is_shadow: bool = False) -> pygame.Surface:
        """Helper just for loading and scaling, NOT applying shadow logic."""
        path = os.path.join("assets", "images", filename)
        surface = pygame.image.load(path).convert_alpha()
        
        scale_factor = self.TILE_SIZE / 60
        new_size = (int(surface.get_width() * scale_factor), 
                    int(surface.get_height() * scale_factor))
        if is_shadow:
            return pygame.transform.scale(surface, new_size)
        else: 
            surface.set_colorkey((0, 0, 0))
            return pygame.transform.smoothscale(surface, new_size)
        
    def load_scorpion_frames(self) -> Tuple[Any, Any]:
        """Load scorpion sprite sheet and split into directional frames."""

        _path = "scorpion.gif"
        # Load Resources
        scorpion_surface = self._load_and_scale_image(_path, is_shadow=False)
        # scorpion_surface.set_colorkey((0, 0, 0))
        
        # Load Shadow (process image then convert to black silhouette)
        shadow_surface = self._load_and_scale_image("_" + _path, is_shadow=True)
        shadow_surface = self.get_black_shadow_surface(shadow_surface)

        # Extract Frames
        w_frame = scorpion_surface.get_width() // 5
        h_frame = scorpion_surface.get_height() // 4
        
        s_frames_list = extract_sprite_frames(scorpion_surface, w_frame, h_frame)
        shadow_frames_list = extract_sprite_frames(shadow_surface, w_frame, h_frame)

        # Helper to assign to FrameSet
        def create_frameset(source_list):
            fs = FrameSet([], [], [], [])
            fs.UP = double_list(source_list[1:5] + [source_list[0]])
            fs.RIGHT = double_list(source_list[6:10] + [source_list[5]])
            fs.DOWN = double_list(source_list[11:15] + [source_list[10]])
            fs.LEFT = double_list(source_list[16:20] + [source_list[15]])
            return fs

        return create_frameset(s_frames_list), create_frameset(shadow_frames_list)

   
    def scorpion_can_move(self, position: List[int], facing_direction: str, gate_opened: bool = False) -> bool:
        """Check if scorpion can move in facing_direction considering wall tiles."""
        x, y = position
        map_w = len(self.map_data[0])
        
        try:
            if facing_direction == UP:
                if y - 1 <= 0: return 
                
                # Check if gate is in the way
                if self.__superdata["gate_pos"] != [] and not gate_opened:
                    gx, gy = self.__superdata["gate_pos"]
                    if (x - 1, y - 2) == (gx - 1, gy - 1):
                        return False
                    
                # if gate not in the way or opened, check walls    
                return (self.map_data[y - 1][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and \
                       (self.map_data[y - 2][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])
            
            if facing_direction == DOWN:
                if y + 1 > map_w: return False

                # Check if gate is in the way
                if self.__superdata["gate_pos"] != [] and not gate_opened:
                    gx, gy = self.__superdata["gate_pos"]
                    if (x - 1, y - 1) == (gx - 1, gy - 1):
                        return False
                    
                # If gate not in the way or opened, check walls
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

    def scorpion_movement(self, player_position: List[int] = [], type: int = 0) -> int:
        """Determine next movement(s) for the scorpion to approach the player."""
        if self.movement_list:
            return False
        
        move_list = generate_next_scorpion_positions(self.map_data, [list(self.grid_position) + [self.scorpion_type]], player_position, show_list=True)
        self.movement_list += move_list

        print(self.movement_list)

        return len(self.movement_list) > 0

    def draw_scorpion(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Render scorpion and shadow."""
        base_x = MARGIN_LEFT + self.TILE_SIZE * (self.grid_position[0] - 1) + offset_x
        base_y = MARGIN_TOP + self.TILE_SIZE * (self.grid_position[1] - 1) + offset_y
        
        screen.blit(self.current_shadow_frame, (base_x, base_y))
        screen.blit(self.current_frame, (base_x, base_y))

    def update_scorpion(self, screen: pygame.Surface, gate_opened: bool = False) -> None:
        """Render and animate the scorpion (Moving or Idle)."""
        move_distance_x = 0
        move_distance_y = 0
        grid_dx = 0
        grid_dy = 0
        
        # --- STATE 1: MOVING ---
        if self.movement_list:
            if self.movement_frame_index == 0:
                self.is_standing = False
                self.scorwalk_sound.play()
                self.facing_direction = self.movement_list[0]

            # Update walking frames
            self.update_current_frames(self.movement_frame_index)

            # Calculate offsets
            step_pixels = (self.movement_frame_index + 1) * (self.speed // self.total_frames) if self.length != 10 else self.move10[self.movement_frame_index + 1]
            can_move = self.scorpion_can_move(self.grid_position, self.facing_direction, gate_opened = gate_opened)

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

            self.draw_scorpion(screen, move_distance_x, move_distance_y)
            
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

        # --- STATE 2: IDLE / EFFECT ---
        else:
            # Default idle frame (standing still)
            self.update_current_frames(self.total_frames - 1)
   
          

            self.draw_scorpion(screen, 0, 0)