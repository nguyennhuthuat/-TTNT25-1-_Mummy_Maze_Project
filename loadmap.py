"""
Mummy Maze Game - Map Loader and Game Engine
Handles map loading, sprite rendering, player/zombie movement, and game logic.
"""

import pygame
import os
from typing import List, Tuple, Dict, Optional, Callable
import maps

# =============================================================================
# CONSTANTS
# =============================================================================

# Direction constants
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 64

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BACKGROUND = (20, 20, 30)

# Game settings
FPS = 60
ANIMATION_SPEED = 0.15

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_sprite_frames(sprite_sheet: pygame.Surface, frame_width: int, 
                         frame_height: int, num_frames: int, row: int = 0) -> List[pygame.Surface]:
    """
    Extract individual frames from a sprite sheet.
    
    Args:
        sprite_sheet: The sprite sheet surface
        frame_width: Width of each frame
        frame_height: Height of each frame
        num_frames: Number of frames to extract
        row: Row index in the sprite sheet (default 0)
    
    Returns:
        List of pygame.Surface objects representing each frame
    """
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        source_rect = pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height)
        frame.blit(sprite_sheet, (0, 0), source_rect)
        frames.append(frame)
    return frames


def double_list(input_list: List) -> List:
    """
    Double each element in a list for smoother animation.
    
    Args:
        input_list: Original list to double
    
    Returns:
        New list with each element repeated twice
    """
    result = []
    for item in input_list:
        result.extend([item, item])
    return result


def clean_map_data(map_data: List[List[str]]) -> List[List[str]]:
    """
    Return a cleaned copy of map data without mutating the input.
    Removes empty strings and normalizes tile identifiers.
    
    Args:
        map_data: Original map data as 2D list
    
    Returns:
        Cleaned copy of map data
    """
    cleaned = []
    for row in map_data:
        cleaned_row = []
        for cell in row:
            # Normalize cell data - replace empty with None
            cleaned_cell = cell if cell and cell.strip() else ""
            cleaned_row.append(cleaned_cell)
        cleaned.append(cleaned_row)
    return cleaned


# =============================================================================
# TILE RENDERING CLASS
# =============================================================================

class TileRenderer:
    """Handles rendering of map tiles using direct method references."""
    
    def __init__(self, tile_size: int = TILE_SIZE):
        """
        Initialize tile renderer.
        
        Args:
            tile_size: Size of each tile in pixels
        """
        self.tile_size = tile_size
        self.tile_images: Dict[str, pygame.Surface] = {}
        self._load_tile_images()
        
        # Direct bound method references for tile rendering
        self.tile_renderers: Dict[str, Callable] = {
            't': self.draw_top_wall,
            'b': self.draw_bottom_wall,
            'l': self.draw_left_wall,
            'r': self.draw_right_wall,
            'tl': self.draw_top_left_corner,
            'tr': self.draw_top_right_corner,
            'bl': self.draw_bottom_left_corner,
            'br': self.draw_bottom_right_corner,
            't*': self.draw_top_wall_special,
            'b*': self.draw_bottom_wall_special,
            'l*': self.draw_left_wall_special,
            'r*': self.draw_right_wall_special,
        }
    
    def _load_tile_images(self):
        """Load tile images from assets folder."""
        # Mapping of tile types to safe filenames
        tile_filename_map = {
            't': 'tile_t.png',
            'b': 'tile_b.png',
            'l': 'tile_l.png',
            'r': 'tile_r.png',
            'tl': 'tile_tl.png',
            'tr': 'tile_tr.png',
            'bl': 'tile_bl.png',
            'br': 'tile_br.png',
            't*': 'tile_t_special.png',
            'b*': 'tile_b_special.png',
            'l*': 'tile_l_special.png',
            'r*': 'tile_r_special.png',
        }
        
        for tile_type, filename in tile_filename_map.items():
            try:
                path = os.path.join('Assets', 'Images', filename)
                if os.path.exists(path):
                    image = pygame.image.load(path).convert_alpha()
                    self.tile_images[tile_type] = pygame.transform.scale(
                        image, (self.tile_size, self.tile_size)
                    )
                else:
                    # Create placeholder if image doesn't exist
                    self.tile_images[tile_type] = self._create_placeholder_tile(tile_type)
            except Exception:
                self.tile_images[tile_type] = self._create_placeholder_tile(tile_type)
    
    def _create_placeholder_tile(self, tile_type: str) -> pygame.Surface:
        """Create a placeholder tile for missing images."""
        surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        color = (100, 100, 100)
        
        if 't' in tile_type:
            pygame.draw.rect(surface, color, (0, 0, self.tile_size, 10))
        if 'b' in tile_type:
            pygame.draw.rect(surface, color, (0, self.tile_size - 10, self.tile_size, 10))
        if 'l' in tile_type:
            pygame.draw.rect(surface, color, (0, 0, 10, self.tile_size))
        if 'r' in tile_type:
            pygame.draw.rect(surface, color, (self.tile_size - 10, 0, 10, self.tile_size))
        
        return surface
    
    def draw_tile(self, screen: pygame.Surface, tile_type: str, x: int, y: int):
        """
        Draw a tile using direct method reference.
        
        Args:
            screen: Surface to draw on
            tile_type: Type of tile to draw
            x: X coordinate
            y: Y coordinate
        """
        renderer = self.tile_renderers.get(tile_type)
        if renderer:
            renderer(screen, x, y)
        elif tile_type == '':
            self.draw_floor(screen, x, y)
    
    def draw_floor(self, screen: pygame.Surface, x: int, y: int):
        """Draw floor tile."""
        pygame.draw.rect(screen, (40, 35, 30), 
                        (x, y, self.tile_size, self.tile_size))
    
    def draw_top_wall(self, screen: pygame.Surface, x: int, y: int):
        """Draw top wall."""
        tile = self.tile_images.get('t')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_bottom_wall(self, screen: pygame.Surface, x: int, y: int):
        """Draw bottom wall."""
        tile = self.tile_images.get('b')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_left_wall(self, screen: pygame.Surface, x: int, y: int):
        """Draw left wall."""
        tile = self.tile_images.get('l')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_right_wall(self, screen: pygame.Surface, x: int, y: int):
        """Draw right wall."""
        tile = self.tile_images.get('r')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_top_left_corner(self, screen: pygame.Surface, x: int, y: int):
        """Draw top-left corner."""
        tile = self.tile_images.get('tl')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_top_right_corner(self, screen: pygame.Surface, x: int, y: int):
        """Draw top-right corner."""
        tile = self.tile_images.get('tr')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_bottom_left_corner(self, screen: pygame.Surface, x: int, y: int):
        """Draw bottom-left corner."""
        tile = self.tile_images.get('bl')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_bottom_right_corner(self, screen: pygame.Surface, x: int, y: int):
        """Draw bottom-right corner."""
        tile = self.tile_images.get('br')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_top_wall_special(self, screen: pygame.Surface, x: int, y: int):
        """Draw special top wall."""
        tile = self.tile_images.get('t*')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_bottom_wall_special(self, screen: pygame.Surface, x: int, y: int):
        """Draw special bottom wall."""
        tile = self.tile_images.get('b*')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_left_wall_special(self, screen: pygame.Surface, x: int, y: int):
        """Draw special left wall."""
        tile = self.tile_images.get('l*')
        if tile:
            screen.blit(tile, (x, y))
    
    def draw_right_wall_special(self, screen: pygame.Surface, x: int, y: int):
        """Draw special right wall."""
        tile = self.tile_images.get('r*')
        if tile:
            screen.blit(tile, (x, y))


# =============================================================================
# SPRITE CLASSES
# =============================================================================

class AnimatedSprite:
    """Base class for animated sprites."""
    
    def __init__(self, x: int, y: int, tile_size: int = TILE_SIZE):
        """
        Initialize animated sprite.
        
        Args:
            x: Grid x position
            y: Grid y position
            tile_size: Size of tiles
        """
        self.grid_x = x
        self.grid_y = y
        self.tile_size = tile_size
        self.pixel_x = x * tile_size
        self.pixel_y = y * tile_size
        self.frames: Dict[str, List[pygame.Surface]] = {}
        self.current_frame = 0
        self.current_direction = DOWN
        self.animation_counter = 0.0
    
    def update_animation(self):
        """Update animation frame."""
        self.animation_counter += ANIMATION_SPEED
        direction_frames = self.frames.get(self.current_direction, [])
        if direction_frames and self.animation_counter >= 1.0:
            self.current_frame = (self.current_frame + 1) % len(direction_frames)
            self.animation_counter = 0.0
    
    def draw(self, screen: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """
        Draw the sprite.
        
        Args:
            screen: Surface to draw on
            offset_x: X offset for drawing
            offset_y: Y offset for drawing
        """
        direction_frames = self.frames.get(self.current_direction, [])
        if direction_frames:
            frame = direction_frames[self.current_frame % len(direction_frames)]
            screen.blit(frame, (self.pixel_x + offset_x, self.pixel_y + offset_y))


class Player(AnimatedSprite):
    """Player character with movement and animation."""
    
    def __init__(self, x: int, y: int, tile_size: int = TILE_SIZE):
        """Initialize player."""
        super().__init__(x, y, tile_size)
        self._load_player_frames()
    
    def _load_player_frames(self):
        """Load player animation frames."""
        try:
            # Try to load player sprite sheet
            sprite_path = os.path.join('Assets', 'Images', 'player.png')
            if os.path.exists(sprite_path):
                sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                frame_width, frame_height = 32, 32
                
                # Extract frames for each direction
                self.frames[DOWN] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 0))
                self.frames[LEFT] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 1))
                self.frames[RIGHT] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 2))
                self.frames[UP] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 3))
                
                # Scale frames to tile size
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    self.frames[direction] = [
                        pygame.transform.scale(frame, (self.tile_size, self.tile_size))
                        for frame in self.frames[direction]
                    ]
            else:
                self._create_placeholder_frames()
        except Exception:
            self._create_placeholder_frames()
    
    def _create_placeholder_frames(self):
        """Create placeholder frames if sprite sheet not found."""
        for direction in [UP, DOWN, LEFT, RIGHT]:
            frame = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(frame, (0, 120, 255), 
                             (self.tile_size // 2, self.tile_size // 2), 
                             self.tile_size // 3)
            self.frames[direction] = [frame]
    
    def move(self, direction: str, map_data: List[List[str]]):
        """
        Move player in specified direction if valid.
        
        Args:
            direction: Direction to move (UP/DOWN/LEFT/RIGHT)
            map_data: Map data for collision detection
        """
        new_x, new_y = self.grid_x, self.grid_y
        
        if direction == UP:
            new_y -= 1
        elif direction == DOWN:
            new_y += 1
        elif direction == LEFT:
            new_x -= 1
        elif direction == RIGHT:
            new_x += 1
        
        # Check collision
        if self._can_move(new_x, new_y, map_data):
            self.grid_x, self.grid_y = new_x, new_y
            self.pixel_x = self.grid_x * self.tile_size
            self.pixel_y = self.grid_y * self.tile_size
            self.current_direction = direction
    
    def _can_move(self, x: int, y: int, map_data: List[List[str]]) -> bool:
        """
        Check if movement to position is valid.
        
        Args:
            x: Target grid x
            y: Target grid y
            map_data: Map data
        
        Returns:
            True if movement is valid
        """
        if not map_data or y < 0 or y >= len(map_data):
            return False
        if not map_data[0] or x < 0 or x >= len(map_data[0]):
            return False
        
        tile = map_data[y][x]
        # Can't move into walls
        blocking_tiles = ['t', 'b', 'l', 'r', 'tl', 'tr', 'bl', 'br',
                         't*', 'b*', 'l*', 'r*']
        return tile not in blocking_tiles


class Zombie(AnimatedSprite):
    """Zombie enemy with AI movement."""
    
    def __init__(self, x: int, y: int, zombie_type: int = 0, tile_size: int = TILE_SIZE):
        """
        Initialize zombie.
        
        Args:
            x: Grid x position
            y: Grid y position
            zombie_type: AI type (0-3)
            tile_size: Size of tiles
        """
        super().__init__(x, y, tile_size)
        self.zombie_type = zombie_type
        self._load_zombie_frames()
    
    def _load_zombie_frames(self):
        """Load zombie animation frames."""
        try:
            sprite_path = os.path.join('Assets', 'Images', 'zombie.png')
            if os.path.exists(sprite_path):
                sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                frame_width, frame_height = 32, 32
                
                # Extract frames using helper function
                self.frames[DOWN] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 0))
                self.frames[LEFT] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 1))
                self.frames[RIGHT] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 2))
                self.frames[UP] = double_list(extract_sprite_frames(
                    sprite_sheet, frame_width, frame_height, 4, 3))
                
                # Scale frames
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    self.frames[direction] = [
                        pygame.transform.scale(frame, (self.tile_size, self.tile_size))
                        for frame in self.frames[direction]
                    ]
            else:
                self._create_placeholder_frames()
        except Exception:
            self._create_placeholder_frames()
    
    def _create_placeholder_frames(self):
        """Create placeholder frames if sprite sheet not found."""
        for direction in [UP, DOWN, LEFT, RIGHT]:
            frame = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            pygame.draw.circle(frame, (0, 200, 0), 
                             (self.tile_size // 2, self.tile_size // 2), 
                             self.tile_size // 3)
            self.frames[direction] = [frame]


# =============================================================================
# GAME LEVEL CLASS
# =============================================================================

class GameLevel:
    """Manages a single game level."""
    
    def __init__(self, level_data: Dict, screen: pygame.Surface):
        """
        Initialize game level.
        
        Args:
            level_data: Level configuration dictionary
            screen: Main screen surface
        """
        self.screen = screen
        self.name = level_data.get('name', 'Unknown Level')
        self.map_length = level_data.get('map_length', 6)
        self.map_data = clean_map_data(level_data.get('map_data', []))
        
        # Get actual map dimensions
        map_height = len(self.map_data) if self.map_data else 0
        map_width = len(self.map_data[0]) if self.map_data and self.map_data[0] else 0
        
        # Initialize player (convert from 1-based to 0-based indexing)
        player_start = level_data.get('player_start', [1, 1])
        player_x = max(0, min(map_width - 1, player_start[0] - 1)) if map_width > 0 else 0
        player_y = max(0, min(map_height - 1, player_start[1] - 1)) if map_height > 0 else 0
        self.player = Player(player_x, player_y)
        
        # Initialize zombies (convert from 1-based to 0-based indexing)
        self.zombies: List[Zombie] = []
        zombie_starts = level_data.get('zombie_starts', [])
        for i, zombie_pos in enumerate(zombie_starts):
            zombie_type = i % 4  # Cycle through zombie types
            zombie_x = max(0, min(map_width - 1, zombie_pos[0] - 1)) if map_width > 0 else 0
            zombie_y = max(0, min(map_height - 1, zombie_pos[1] - 1)) if map_height > 0 else 0
            self.zombies.append(Zombie(zombie_x, zombie_y, zombie_type))
        
        # Stair position (goal) - may be outside map boundaries as exit point
        stair_pos = level_data.get('stair_position', (0, 0))
        # Don't clamp stair position - it can be outside the map as an exit
        self.stair_x = stair_pos[0] - 1
        self.stair_y = stair_pos[1] - 1
        
        # Initialize tile renderer
        self.tile_renderer = TileRenderer()
        
        # Game state
        self.game_over = False
        self.level_complete = False
    
    def handle_input(self, keys):
        """
        Handle player input.
        
        Args:
            keys: Pygame key state
        """
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move(UP, self.map_data)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move(DOWN, self.map_data)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(LEFT, self.map_data)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(RIGHT, self.map_data)
    
    def update(self):
        """Update game state."""
        # Update animations
        self.player.update_animation()
        for zombie in self.zombies:
            zombie.update_animation()
        
        # Check win condition
        if (self.player.grid_x == self.stair_x and 
            self.player.grid_y == self.stair_y):
            self.level_complete = True
        
        # Check collision with zombies
        for zombie in self.zombies:
            if (self.player.grid_x == zombie.grid_x and 
                self.player.grid_y == zombie.grid_y):
                self.game_over = True
    
    def draw(self):
        """Draw the level."""
        # Draw tiles
        for row_idx, row in enumerate(self.map_data):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                self.tile_renderer.draw_tile(self.screen, tile, x, y)
        
        # Draw stair (only if within visible bounds)
        if self.stair_x >= 0 and self.stair_y >= 0:
            stair_rect = pygame.Rect(self.stair_x * TILE_SIZE, 
                                     self.stair_y * TILE_SIZE,
                                     TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, (255, 215, 0), stair_rect)
        
        # Draw zombies
        for zombie in self.zombies:
            zombie.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        name_text = font.render(self.name, True, COLOR_WHITE)
        self.screen.blit(name_text, (10, 10))


# =============================================================================
# MAIN GAME FUNCTION
# =============================================================================

def main():
    """Main game loop."""
    # Initialize pygame
    pygame.init()
    
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mummy Maze")
    
    # Game clock
    clock = pygame.time.Clock()
    
    # Load first level
    current_level_index = 0
    level_data = maps.maps_collection[current_level_index]
    current_level = GameLevel(level_data, screen)
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Restart level
                    current_level = GameLevel(level_data, screen)
                elif event.key == pygame.K_n and current_level.level_complete:
                    # Next level
                    current_level_index = (current_level_index + 1) % len(maps.maps_collection)
                    level_data = maps.maps_collection[current_level_index]
                    current_level = GameLevel(level_data, screen)
        
        # Input handling
        keys = pygame.key.get_pressed()
        if not current_level.game_over and not current_level.level_complete:
            current_level.handle_input(keys)
        
        # Update
        current_level.update()
        
        # Draw
        screen.fill(COLOR_BACKGROUND)
        current_level.draw()
        
        # Draw game over / level complete messages
        font = pygame.font.Font(None, 48)
        if current_level.game_over:
            text = font.render("GAME OVER! Press R to restart", True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                              SCREEN_HEIGHT // 2))
        elif current_level.level_complete:
            text = font.render("Level Complete! Press N for next level", True, (0, 255, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                              SCREEN_HEIGHT // 2))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == '__main__':
    main()
