import os
import time
from typing import List, Tuple, Optional, Any
import random
import pygame
from .utils import *
from .settings import *


class MummyMazePlayerManager:
    """
    Player handling: loading frames, movement, and rendering.
    """

    def __init__(self, length: int = 6, grid_position: Optional[List[int]] = None, data: Any = None, tile_size: int = TILE_SIZE) -> None:
        self.length = length
        self.TILE_SIZE = tile_size
        # Fix: Mutable default argument
        self.grid_position = grid_position if grid_position is not None else [1, 2]
        
        self.map_data = data["map_data"] if data and "map_data" in data else []
        self.__superdata = data

        # 1. Load Resources
        # Giữ nguyên logic load riêng biệt để đảm bảo shadow không bị lỗi
        self.player_frames, self.shadow_player_frames = self.load_player_frames()
        self.finding_frames, self.shadow_finding_frames = self.load_player_finding_frames()
        
        self.expwalk_sound = pygame.mixer.Sound(os.path.join("Assets", "sounds", "expwalk60b.wav"))

        # 2. Movement State
        self.movement_list: List[str] = []
        self.is_standing: bool = True
        self.facing_direction: str = UP
        self.speed = tile_size  # Renamed from Speed

        # 3. Animation State
        self.total_frames = 10
        self.movement_frame_index = 0
        
        # Idle/Finding State
        self.finding_frame_index = 0
        self.idle_time_threshold = random.randint(3, 8)
        self.start_standing = time.time()

        # 4. Set initial frames
        self.update_current_frames(frame_index=self.total_frames - 1)

    def get_x(self):
        return self.grid_position[0]
    def get_y(self):
        return self.grid_position[1]

    def start_game_effect(self,screen,image_screen, goal: list, facing_direction: str = RIGHT) -> None:
        def draw_spotlight(surface: pygame.Surface, pos: Tuple[int, int], radius: int) -> None:
            # pygame.SRCALPHA cho phép tạo surface với kênh alpha (độ trong suốt)
            mask.fill((0, 0, 0, 255)) 


            pygame.draw.circle(hole, (255, 255, 255, 255), pos, radius)

            # special_flags=pygame.BLEND_RGBA_SUB sẽ trừ màu trắng (255) khỏi mask, tạo lỗ hổng trong suốt
            mask.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            surface.blit(mask, (0, 0))

        # Create mask surfaces
        mask = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        hole = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        start_pos = goal.copy()

        grid_dx = 0
        grid_dy = 0
        move_distance_x = 0
        move_distance_y = 0

        # Sound 
        Mummyhowl = pygame.mixer.Sound(os.path.join("Assets", "sounds", "mummyhowl.wav"))

        end_effect = False
        
        # Initialize start position based on facing direction
        match facing_direction:
            case 'UP':
                start_pos[1] = min(self.length + 2, start_pos[1] + 2)
                grid_dx = 0 
                grid_dy = -1
            case 'DOWN':
                start_pos[1] = max(-1, start_pos[1] - 2)
                grid_dx = 0
                grid_dy = 1
            case 'LEFT':
                start_pos[0] = min(self.length + 2, start_pos[0] + 2)
                grid_dx = -1
                grid_dy = 0
            case 'RIGHT':
                start_pos[0] = max(-1, start_pos[0] - 2)
                grid_dx = 1
                grid_dy = 0

        self.grid_position = start_pos
        self.facing_direction = facing_direction
        
        # Explorer come in
        while not end_effect:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            # Sound effect
            if self.movement_frame_index == 0:
                self.expwalk_sound.play()

            # Clear Screen
            screen.fill((0,0,0))

            # Calculate Step Pixels
            step_pixels = (self.movement_frame_index + 1) * (self.speed // self.total_frames)

            self.update_current_frames(self.movement_frame_index)
            
            # Calculate Movement Offsets
            match facing_direction:
                case 'UP':
                    move_distance_y = -step_pixels
                case 'DOWN':
                    move_distance_y = step_pixels
                case 'LEFT':
                    move_distance_x = -step_pixels
                case 'RIGHT':
                    move_distance_x = step_pixels

            self.draw_player(screen, move_distance_x, move_distance_y)

            # Update Frame Index
            self.movement_frame_index += 1
            
            # Check if step finished
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                
                # Logic: Update grid position only at end of animation
                self.grid_position[0] += grid_dx
                self.grid_position[1] += grid_dy

            # Check if reach goal
            if self.grid_position == goal:
                end_effect = True

            pygame.display.flip()
            pygame.time.Clock().tick(60) 
            time.sleep(0.04)      

        time.sleep(0.4)     # delay
        # Show board game effect
        radiant = 100
        base_x = MARGIN_LEFT + self.TILE_SIZE * (self.grid_position[0] - 1) + self.TILE_SIZE // 2
        base_y = MARGIN_TOP + self.TILE_SIZE * (self.grid_position[1] - 1) + self.TILE_SIZE // 2

        # Calculate max radiant needed
        max_radiant = max(max(base_x, SCREEN_WIDTH - base_x), max(base_y, SCREEN_HEIGHT - base_y))
        print("Starting board reveal effect...", max_radiant)


        while radiant < max_radiant:  # Continue until full screen is revealed
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Draw previous game state
            screen.blit(image_screen, (0,0))

            # Draw spotlight
            draw_spotlight(screen, (base_x, base_y), radiant)

            radiant = int(radiant * 1.3)

            pygame.display.flip()
            pygame.time.Clock().tick(60) 
            time.sleep(0.02)

        Mummyhowl.play()

    @property
    def is_in_trap(self) -> bool:
        """Check if player is currently on a trap tile."""
        x, y = self.grid_position
        if self.__superdata and self.__superdata["trap_pos"] != []:
            for tx, ty in self.__superdata["trap_pos"]:
                if (x - 1, y - 1) == (tx - 1, ty - 1):
                    return True
                
        return False

    def update_current_frames(self, frame_index: int) -> None:
        """Helper to update both sprite and shadow frames based on direction."""
        direction_key = str(self.facing_direction)
        self.current_frame = getattr(self.player_frames, direction_key)[frame_index]
        self.current_shadow_frame = getattr(self.shadow_player_frames, direction_key)[frame_index]

    def get_black_shadow_surface(self, frame: pygame.Surface) -> pygame.Surface:
        """Convert an original shadow surface to a black silhouette."""
        image = frame.copy()
        image.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(image)
        # setcolor=(0, 0, 0) -> Absolute black
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

    def _create_frameset(self, frames_list: List[pygame.Surface]) -> Any:
        """Helper to map a list of frames to UP/RIGHT/DOWN/LEFT logic."""
        fs = FrameSet([], [], [], [])
        # Indices based on original code logic
        fs.UP = double_list(frames_list[1:5] + [frames_list[0]])
        fs.RIGHT = double_list(frames_list[6:10] + [frames_list[5]])
        fs.DOWN = double_list(frames_list[11:15] + [frames_list[10]])
        fs.LEFT = double_list(frames_list[16:20] + [frames_list[15]])
        return fs

    def load_player_frames(self) -> Tuple[Any, Any]:
        """Load player sprite sheet and split into directional frames."""
        
        # 1. Load NORMAL sprite
        player_surface = self._load_and_scale_image("explorer.gif", is_shadow=False).convert_alpha()
        player_surface.set_colorkey((0, 0, 0))

        # 2. Load SHADOW sprite (Load -> Scale -> then Convert to Black)
        shadow_surface = self._load_and_scale_image("_explorer.gif", is_shadow=True)
        shadow_surface = self.get_black_shadow_surface(shadow_surface)

        # 3. Extract Frames
        w_frame = player_surface.get_width() // 5
        h_frame = player_surface.get_height() // 4
        
        player_frames_list = extract_sprite_frames(player_surface, w_frame, h_frame)
        shadow_frames_list = extract_sprite_frames(shadow_surface, w_frame, h_frame)

        return self._create_frameset(player_frames_list), self._create_frameset(shadow_frames_list)

    def load_player_finding_frames(self) -> Tuple[List[pygame.Surface], List[pygame.Surface]]:
        """Load player finding sprite sheet (horizontal strip)."""
        
        def extract_strip_frames(sheet: pygame.Surface) -> List[pygame.Surface]:
            frame_size = sheet.get_height() # Square frames based on height
            sheet_width = sheet.get_width()
            frames = []
            for x in range(0, sheet_width, frame_size):
                frames.append(sheet.subsurface(pygame.Rect(x, 0, frame_size, frame_size)))
            return frames

        # 1. Load NORMAL finding
        finding_surface = self._load_and_scale_image("explorer_finding.gif", is_shadow=False)
        # finding_surface.set_colorkey((0, 0, 0))

        # 2. Load SHADOW finding
        shadow_finding_surface = self._load_and_scale_image("_explorer_finding.gif", is_shadow=True)
        shadow_finding_surface = self.get_black_shadow_surface(shadow_finding_surface)

        return extract_strip_frames(finding_surface), extract_strip_frames(shadow_finding_surface)

    def player_can_move(self, position: List[int], facing_direction: str, gate_opened: bool = False) -> bool:
        """Check if player can move in facing_direction considering wall tiles."""
        x, y = position
        map_w = len(self.map_data[0])
        
        try:
            if facing_direction == UP:
                if y - 1 <= 0: return False

                # Check if gate is in the way
                if self.__superdata["gate_pos"] != [] and not gate_opened:
                    gx, gy = self.__superdata["gate_pos"]
                    if (x - 1, y - 2) == (gx - 1, gy - 1):
                        return False
                
                # If gate not in the way or opened, check walls
                return (self.map_data[y - 1][x - 1] not in ['t', 'tl', 'tr', 'b*', 'l*', 'r*']) and \
                       (self.map_data[y - 2][x - 1] not in ['b', 'bl', 'br', 't*', 'l*', 'r*'])
            
            if facing_direction == DOWN:
                if y + 1 > map_w: return False

                # Check if gate is in the way
                if self.__superdata["gate_pos"] != [] and not gate_opened:
                    gx, gy = self.__superdata["gate_pos"]
                    if (x - 1, y - 1) == (gx - 1, gy - 1):
                        return False
                    else:
                        print(f"curent player pos: {(x-1, y-1)}, gate pos: {(gx, gy)}")

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

    def update_player_status(self, facing_direction: str) -> None:
        """Update player facing direction when inputs are received."""
        self.facing_direction = facing_direction
        self.movement_list.append(facing_direction)

        self.is_standing = False
        self.finding_frame_index = 0 # reset finding animation
        
        # Note: self.start_moving not strictly needed for logic, but kept if you debug speed
        self.expwalk_sound.play()

    def draw_player(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Render player and shadow with offset."""
        base_x = MARGIN_LEFT + self.TILE_SIZE * (self.grid_position[0] - 1) + offset_x
        base_y = MARGIN_TOP + self.TILE_SIZE * (self.grid_position[1] - 1) + offset_y
        
        screen.blit(self.current_shadow_frame, (base_x, base_y))
        screen.blit(self.current_frame, (base_x, base_y))

    def update_player(self, screen: pygame.Surface, gate_opened: bool = False) -> bool:
        """
        Update player animation and position.
        Returns True when a movement step completes (for turn-based logic).
        """
        move_completed = False
        move_distance_x = 0
        move_distance_y = 0
        grid_dx = 0
        grid_dy = 0

        # --- STATE 1: MOVING ---
        if self.movement_list:
            self.facing_direction = self.movement_list[0]
            
            # Update animation frames based on direction
            self.update_current_frames(self.movement_frame_index)

            # Calculate Movement Offsets
            if self.player_can_move(self.grid_position, self.facing_direction, gate_opened = gate_opened):
                step_pixels = (self.movement_frame_index + 1) * (self.speed // self.total_frames)
                
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

            self.draw_player(screen, move_distance_x, move_distance_y)

            # Update Frame Index
            self.movement_frame_index += 1
            
            # Check if step finished
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                
                # Logic: Update grid position only at end of animation
                self.grid_position[0] += grid_dx
                self.grid_position[1] += grid_dy
                
                self.movement_list.pop(0)
                
                # Reset idle timer after move
                self.idle_time_threshold = random.randint(3, 8)
                self.start_standing = time.time()
                
                move_completed = True
                self.is_standing = True

        # --- STATE 2: IDLE / FINDING ANIMATION ---
        else:
            # Default to last frame (Standing still)
            self.update_current_frames(self.total_frames - 1)

            # Check Logic for Finding Animation (Look around)
            # Condition: Standing + Facing DOWN + Time elapsed > Threshold
            is_idle_timeout = (time.time() - self.start_standing >= self.idle_time_threshold)

            if self.is_standing and self.facing_direction == DOWN and is_idle_timeout:
                self.current_frame = self.finding_frames[self.finding_frame_index]
                self.current_shadow_frame = self.shadow_finding_frames[self.finding_frame_index]
                
                self.finding_frame_index += 1

                # If finding loop finishes
                if self.finding_frame_index >= len(self.finding_frames):
                    self.finding_frame_index = 0
                    self.start_standing = time.time() # Reset timer
                    self.idle_time_threshold = random.randint(8, 16) # New random threshold

            self.draw_player(screen, 0, 0)
    
        return move_completed
    

pygame.quit()