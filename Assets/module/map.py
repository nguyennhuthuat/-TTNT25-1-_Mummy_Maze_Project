import os
from typing import List, Tuple
import pygame

from typing import Any

from .settings import *
from .utils import *
from .fonts import MetricFont



class GateKeyManager:
    def __init__(self,length: int = 6, tile_size: int = TILE_SIZE, key_pos: Tuple = (), gate_pos: Tuple = ()) -> None:
        self.length = length
        self.TILE_SIZE = tile_size

        # Sound 
        self.gate_sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "gate.wav"))

        self.__key_pos = key_pos
        self.gate_pos = gate_pos

        self.__current_key_frame_index = 0
        self.__current_gate_frame_index = 0

        self.__is_opening_gate = False
        self.__is_changing_gate_status = False

        self.__key_frames, self.__shadow_key_frames = self.get_key_frames()
        self.__gate_frames = self.get_gate_frames()

    def get_key_pos(self) -> Tuple[int, int]: #
        """Get the key position in (row, col) format."""
        return self.__key_pos
    
    def get_gate_pos(self) -> Tuple[int, int]: #
        """Get the gate position in (row, col) format."""
        return self.gate_pos
    
    def is_opening_gate(self) -> bool: #
        """Check if the gate is currently opening."""
        return self.__is_opening_gate
    
    def change_gate_status(self): #
        """Trigger gate opening/closing animation."""
        self.__is_opening_gate = not self.__is_opening_gate
        self.__is_changing_gate_status = True
        
        # Sound effect
        self.gate_sound.play()


    def is_finished_changeing_gate_status(self) -> bool:
        """Check if gate has finished opening/closing animation."""
        return not self.__is_changing_gate_status

    def get_key_frames(self) -> Tuple[Any, Any]:
        """Load key sprite sheet and split into directional frames."""
        
        # 1. Load NORMAL sprite
        key_surface = load_and_scale_image(self.TILE_SIZE, "key.png", is_shadow=False)

        # 2. Load SHADOW sprite (Load -> Scale -> then Convert to Black)
        shadow_surface = load_and_scale_image(self.TILE_SIZE, "_key.gif", is_shadow=True)
        shadow_surface = get_black_shadow_surface(shadow_surface)

        # 3. Extract Frames
        w_frame = key_surface.get_height()
        h_frame = key_surface.get_height()
        
        key_frames_list = extract_sprite_frames(key_surface, w_frame, h_frame)
        shadow_frames_list = extract_sprite_frames(shadow_surface, w_frame, h_frame)

        return (key_frames_list, shadow_frames_list)

    def get_gate_frames(self) -> List[Any]:
        """Load gate sprite sheet and split into directional frames."""
        
        # 1. Load NORMAL sprite
        gate_surface = load_and_scale_image(self.TILE_SIZE, "gate.gif", is_shadow=False)

        # 2. Extract Frames
        w_frame = gate_surface.get_width() // 8
        h_frame = gate_surface.get_height()
        
        gate_frames_list = double_list(extract_sprite_frames(gate_surface, w_frame, h_frame))

        return gate_frames_list
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the key at its position."""
        if not self.__key_pos:
            return
        # Calculate pixel position
        row, col = self.__key_pos[0], self.__key_pos[1]
        x = MARGIN_LEFT + self.TILE_SIZE * (row - 1) + (self.TILE_SIZE - self.__key_frames[0].get_width()) // 2
        y = MARGIN_TOP + self.TILE_SIZE * (col - 1) + (self.TILE_SIZE - self.__key_frames[0].get_height()) // 2

        # Draw shadow first
        shadow_frame = self.__shadow_key_frames[self.__current_key_frame_index]
        screen.blit(shadow_frame, (x, y))

        # Draw actual key
        key_frame = self.__key_frames[self.__current_key_frame_index]
        screen.blit(key_frame, (x, y))

        # Update frame index for animation
        self.__current_key_frame_index = (self.__current_key_frame_index + 1) % len(self.__key_frames)


        """Draw the gate at its position."""
        if not self.gate_pos:
            return
        
        # Calculate pixel position
        row, col = self.gate_pos[0], self.gate_pos[1]
        x = MARGIN_LEFT + self.TILE_SIZE * (row - 1) + (self.TILE_SIZE - self.__gate_frames[0].get_width()) // 2
        y = MARGIN_TOP + self.TILE_SIZE * (col - 1) + self.TILE_SIZE - self.__gate_frames[0].get_height() // 2 - 10

        gate_frame = self.__gate_frames[self.__current_gate_frame_index]
        screen.blit(gate_frame, (x, y))

        # Update frame index for animation
        if self.__is_changing_gate_status:    # If gate is in the process of opening/closing
            if self.__is_opening_gate:
                self.__current_gate_frame_index += 1
                if self.__current_gate_frame_index >= len(self.__gate_frames):
                    self.__current_gate_frame_index = len(self.__gate_frames) - 1
                    self.__is_changing_gate_status = False
            else: 
                self.__current_gate_frame_index -= 1
                if self.__current_gate_frame_index < 0:
                    self.__current_gate_frame_index = 0
                    self.__is_changing_gate_status = False
        
        else:                                  # If gate is static (fully open or fully closed)
            if self.__is_opening_gate:
                self.__current_gate_frame_index = len(self.__gate_frames) - 1
            else:
                self.__current_gate_frame_index = 0
    
class TrapManager: 
    def __init__(self, length: int = 6, tile_size: int = TILE_SIZE, trap_positions: List[Tuple] = []) -> None:
        """
        Initialize the TrapManager. 
        
        Args:
            length: The grid length (default: 6)
            tile_size: Size of each tile in pixels
            trap_positions: List of trap positions in (row, col) format
        """
        self.length = length
        self.TILE_SIZE = tile_size
        
        # Use list copy to avoid mutable default argument issue
        self.__trap_pos = trap_positions.copy() if trap_positions else []

        self.__trap_image = self.load_trap_image()

    def get_pos(self) -> List[Tuple[int, int]]:
        """
        Get all trap positions. 
        
        Returns:
            List of trap positions in (row, col) format
        """
        return self.__trap_pos

    def load_trap_image(self) -> pygame.Surface:
        """
        Load and scale the trap image according to tile size.
        
        Returns:
            Scaled trap surface
            
        Raises:
            FileNotFoundError: If trap image file does not exist
        """
        scale_factor = self.TILE_SIZE / 60

        path = os.path. join("assets", "images", "trap.png")
        
        # Check if file exists before loading
        if not os.path.exists(path):
            raise FileNotFoundError(f"Trap image not found: {path}")
        
        surface = pygame. image.load(path).convert_alpha()
        
        new_size = (int(surface.get_width() * scale_factor), 
                    int(surface. get_height() * scale_factor))
        
        surface.set_colorkey((0, 0, 0))
        return pygame.transform.smoothscale(surface, new_size)

    def draw(self, screen: pygame. Surface) -> None:
        """
        Draw all traps at their positions.
        
        Args:
            screen:  Pygame surface to draw on
        """
        for pos in self.__trap_pos:
            # Validate position tuple
            if not pos or len(pos) < 2:
                continue
            
            row, col = pos
            x = MARGIN_LEFT + self.TILE_SIZE * (row - 1) + (self.TILE_SIZE - self.__trap_image.get_width()) // 2
            y = MARGIN_TOP + self.TILE_SIZE * (col - 1) + (self.TILE_SIZE - self.__trap_image. get_height()) // 2
            
            screen.blit(self.__trap_image, (x, y))
    
    def check_collision(self, player_pos: List[int]) -> bool:
        """
        Check if player collides with any trap.
        
        Args:
            player_pos: Player position in (row, col) format
            
        Returns:
            True if player position matches any trap position, False otherwise
        """
        player_pos = tuple(player_pos)
        if not player_pos or len(player_pos) < 2:
            return False
        
        return player_pos in self.__trap_pos

class MummyMazeMapManager:
    """Handles tile/stair drawing and tile graphics loading."""

    def __init__(
        self,
        length: int = 6,
        stair_position: Tuple[int, int] = (1, 7),
        data: dict = None,
        tile_size: int = TILE_SIZE,
    ) -> None:
        
        self.__superdata = data
        self.length = length  # size of square map (length x length)
        # Map from tile id to a bound drawing method (set up using bound methods)
        # Will be populated after methods are available (we can set here using bound methods)
        self.map_data = data["map_data"] if data else [["" for _ in range(length)] for _ in range(length)]
        self.stair_positions = stair_position
        self.is_opening_gate = False

        self.TILE_SIZE = tile_size

        # padding to center walls/stairs based on map size
        self.padding_left = SCREEN_WIDTH // (10 * self.length) // 4
        self.padding_top = SCREEN_HEIGHT // (10 * self.length) * 2 + 1

        # Add traps if any
        trap_pos = self.get_trap_pos()
        if trap_pos != []:
            self.__is_trap_exists = True
            self.trap = TrapManager(self.length, self.TILE_SIZE, trap_pos)
        else:
            self.__is_trap_exists = False

        # Add gate and key if any
        key_pos = self.get_key_pos()
        gate_pos = self.get_gate_pos()
        if key_pos != () and gate_pos != ():
            self.__is_kg_exists = True
            self.gate_key = GateKeyManager(self.length, self.TILE_SIZE, key_pos, gate_pos)
        else:
            self.__is_kg_exists = False

        # Load background and floor images (pygame must be initialized before calling)
        self.backdrop = pygame.image.load(
            os.path.join("assets", "images", "backdrop.png")
        ).convert()
        self.backdrop = pygame.transform.scale(
            self.backdrop, (BACKDROP_WIDTH, BACKDROP_HEIGHT)
        )
        self.game_floor = pygame.image.load(
            os.path.join("assets", "images", "floor" + str(self.length) + ".png")
        ).convert_alpha()
        self.game_floor = pygame.transform.scale(
            self.game_floor, (GAME_FLOOR_WIDTH, GAME_FLOOR_HEIGHT)
        )

        # Prepare tile images
        self.load_tiles()

        # Populate the database mapping tile ids to bound functions
        self.database = {
            "t": self.draw_top_wall_tile,
            "b": self.draw_bottom_wall_tile,
            "l": self.draw_left_wall_tile,
            "r": self.draw_right_wall_tile,
            "tr": self.draw_top_right_wall_tile,
            "tl": self.draw_top_left_wall_tile,
            "br": self.draw_bottom_right_wall_tile,
            "bl": self.draw_bottom_left_wall_tile,
            "l*": self.draw_left_t_wall_tile,
            "r*": self.draw_right_t_wall_tile,
            "t*": self.draw_top_t_wall_tile,
            "b*": self.draw_bottom_t_wall_tile,
        }

    def is_kg_exists(self) -> bool:
        """Check if gate and key exist in the map."""
        return self.__is_kg_exists
    
    def is_position_in_trap(self, position: Tuple[int, int]) -> bool:
        """Check if a given position is in trap positions."""
        trap_positions = [tuple(pos) for pos in self.get_trap_pos()]
        print(position, trap_positions)
        return tuple(position) in trap_positions
    def is_trap_exists(self) -> bool:
        """Check if traps exist in the map."""
        return self.__is_trap_exists

    def get_trap_pos(self):
        """Get all trap positions in (row, col) format."""
        trap_positions = []
        if self.__superdata and "trap_pos" in self.__superdata and self.__superdata["trap_pos"] != []:
            trap_positions = self.__superdata["trap_pos"]

        return [tuple(trap_positions[i]) for i in range(len(trap_positions))]
    
    def get_key_pos(self):
        """Get the key position in (row, col) format."""
        if self.__superdata and "key_pos" in self.__superdata and self.__superdata["key_pos"] != []:
            key_position = self.__superdata["key_pos"]
            return (key_position[0], key_position[1]) # Convert to tuple
        else:
            return ()
    
    def get_gate_pos(self):
        """Get the gate position in (row, col) format."""
        if self.__superdata and "gate_pos" in self.__superdata and self.__superdata["gate_pos"] != []:
            gate_position = self.__superdata["gate_pos"]
            return (gate_position[0], gate_position[1]) # Convert to tuple
        else:
            return ()

    def load_tiles(self) -> None:
        """Cut and scale wall/stair images from spritesheets according to map size."""
        area_surface = pygame.image.load(
            os.path.join("assets", "images", "walls6.png")
        ).convert_alpha()

        area_to_cut = pygame.Rect(0, 0, 12, 78)
        self.down_standing_wall = pygame.transform.scale(
            area_surface.subsurface(area_to_cut),
            (12 * self.TILE_SIZE // 60, 78 * self.TILE_SIZE // 60),
        )

        area_to_cut = pygame.Rect(12, 0, 72, 18)
        self.lying_wall = pygame.transform.scale(
            area_surface.subsurface(area_to_cut),
            (72 * self.TILE_SIZE // 60, 18 * self.TILE_SIZE // 60),
        )

        area_to_cut = pygame.Rect(84, 0, 12, 78)
        self.up_standing_wall = pygame.transform.scale(
            area_surface.subsurface(area_to_cut),
            (12 * self.TILE_SIZE // 60, 78 * self.TILE_SIZE // 60),
        )

        area_stair_surface = pygame.image.load(
            os.path.join("assets", "images", "stairs.png")
        ).convert_alpha()

        area_to_cut = pygame.Rect(2, 0, 54, 66)
        self.top_stair = pygame.transform.scale(
            area_stair_surface.subsurface(area_to_cut),
            (54 * self.TILE_SIZE // 60, 66 * self.TILE_SIZE // 60),
        )

        area_to_cut = pygame.Rect(60, 0, 54, 66)
        self.right_stair = pygame.transform.scale(
            area_stair_surface.subsurface(area_to_cut),
            (54 * self.TILE_SIZE // 60, 66 * self.TILE_SIZE // 60),
        )

        area_to_cut = pygame.Rect(114, 0, 54, 34)
        self.bottom_stair = pygame.transform.scale(
            area_stair_surface.subsurface(area_to_cut),
            (54 * self.TILE_SIZE // 60, 34 * self.TILE_SIZE // 60),
        )

        area_to_cut = pygame.Rect(170, 0, 54, 66)
        self.left_stair = pygame.transform.scale(
            area_stair_surface.subsurface(area_to_cut),
            (54 * self.TILE_SIZE // 60, 66 * self.TILE_SIZE // 60),
        )

    # Tile drawing methods (x and y are 1-based grid coordinates)
    def draw_top_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )

    def draw_bottom_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top,
            ),
        )

    def draw_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )

    def draw_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )

    def draw_bottom_left_wall_tile(
        self, screen: pygame.Surface, x: int, y: int
    ) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.up_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top,
            ),
        )

    def draw_top_left_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )

    def draw_bottom_right_wall_tile(
        self, screen: pygame.Surface, x: int, y: int
    ) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.up_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top,
            ),
        )

    def draw_top_right_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )

    def draw_left_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.up_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top,
            ),
        )

    def draw_right_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top,
            ),
        )

    def draw_top_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.up_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.up_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y + self.TILE_SIZE - self.padding_top,
            ),
        )

    def draw_bottom_t_wall_tile(self, screen: pygame.Surface, x: int, y: int) -> None:
        x -= 1
        y -= 1
        screen.blit(
            self.lying_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )
        screen.blit(
            self.down_standing_wall,
            (
                MARGIN_LEFT + self.TILE_SIZE * x + self.TILE_SIZE - self.padding_left,
                MARGIN_TOP + self.TILE_SIZE * y - self.padding_top,
            ),
        )

    def draw_stair(self, screen: pygame.Surface) -> None:
        """Draw the stair graphic according to stair_positions."""
        row, col = self.stair_positions

        def draw_bottom_stair(
            screen_inner: pygame.Surface, row_i: int, col_i: int
        ) -> None:
            x = MARGIN_LEFT + self.TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - 2
            screen_inner.blit(self.bottom_stair, (x, y))

        def draw_top_stair(
            screen_inner: pygame.Surface, row_i: int, col_i: int
        ) -> None:
            x = (
                MARGIN_LEFT + self.TILE_SIZE * (row_i - 1)
            )
            y = (
                MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - self.top_stair.get_height() + self.TILE_SIZE
            )
            screen_inner.blit(self.top_stair, (x, y))

        def draw_left_stair(
            screen_inner: pygame.Surface, row_i: int, col_i: int
        ) -> None:
            x = MARGIN_LEFT + self.TILE_SIZE * (row_i - 1)
            y = MARGIN_TOP + self.TILE_SIZE * (col_i - 1) - 5
            screen_inner.blit(self.left_stair, (x, y))

        def draw_right_stair(
            screen_inner: pygame.Surface, row_i: int, col_i: int
        ) -> None:
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
            print(
                f"Warning: stair position {self.stair_positions} is invalid. No stair drawn."
            )


    def draw_map(self, screen: pygame.Surface) -> None:
        screen.blit(self.backdrop, (MARGIN_BACKDROP_X, MARGIN_BACKDROP_Y))
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
                elif tid and tid not in "TKG":  # T: Trap, K: Key, G: Gate
                    # If tile id is unknown, warn and skip
                    print(
                        f"Warning: tile_id '{tid}' at ({col_index}, {row_index}) not found in database. Skipping drawing."
                    )

    def draw_gate_key(self, screen: pygame.Surface) -> None:
        """Draw gate and key if they exist."""
        if self.__is_kg_exists:
            self.gate_key.draw(screen)

    def draw_trap(self, screen: pygame.Surface) -> None:
        """Draw traps if they exist."""
        if self.__is_trap_exists:
            self.trap.draw(screen)

class SidePanel:
    """
    Class quản lý khung bên trái với các button: UNDO MOVE, RESET MAZE, OPTIONS, WORLD MAP, QUIT TO MAIN.
    Sử dụng Khung.png làm nền và buttonkhung.png cho các nút.
    """

    # Kích thước panel (nhỏ hơn nữa)
    PANEL_WIDTH = 220
    PANEL_HEIGHT = 638  # Bằng chiều cao cửa sổ game

    # Kích thước button
    BUTTON_WIDTH = 180
    BUTTON_HEIGHT = 50
    BUTTON_GAP = 6  # Không có khoảng cách giữa 4 button đầu

    # Tên các button theo thứ tự
    BUTTON_LABELS = ["UNDO MOVE", "RESET MAZE", "HINT", "OPTIONS", "QUIT TO MAIN"]

    def __init__(self, x: int = 5, y: int = 16) -> None:
        """
        Khởi tạo SidePanel.
        :param x: Tọa độ x của panel
        :param y: Tọa độ y của panel
        """
        self.x = x
        self.y = y

        # Load và scale ảnh Khung.png
        khung_original = pygame.image.load(
            os.path.join("assets", "images", "Khung.png")
        ).convert_alpha()
        self.panel_img = pygame.transform.scale(
            khung_original, (self.PANEL_WIDTH, self.PANEL_HEIGHT)
        )

        # Load và scale ảnh buttonkhung.png
        btn_original = pygame.image.load(
            os.path.join("assets", "images", "buttonkhung.png")
        ).convert_alpha()
        self.button_img = pygame.transform.scale(
            btn_original, (self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        )

        # Tạo button hover (sáng hơn)
        self.button_hover_img = self.button_img.copy()
        self.button_hover_img.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_ADD)

        # Tạo button pressed (tối hơn)
        self.button_pressed_img = self.button_img.copy()
        self.button_pressed_img.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_SUB)

        # Font cho text trên button 
        font_path = os.path.join("assets", "Fonts", "VT323-Regular.ttf")
        # self.font = pygame.font.Font(font_path, 30)
        # self.score_font = pygame.font.Font(font_path, 55)
        # self.score_label_font = pygame.font.Font(font_path, 40)

        self.font = MetricFont("headerfont")
        self.score_font = MetricFont("headerfont", 40)
        self.score_label_font = MetricFont("headerfont")

        # Trạng thái các button
        self.button_states = {label: "normal" for label in self.BUTTON_LABELS}
        self.button_rects = {}

        # Hiệu ứng flash cho RESET MAZE
        self.reset_flash_timer = 0
        self.reset_flash_duration = 300  # ms

        self._calculate_button_positions()

    def reset_button_states(self) -> None:
        """Reset tất cả button về trạng thái normal."""
        for label in self.button_states. keys():
            self.button_states[label] = "normal"

    def _calculate_button_positions(self) -> None:
        """Tính toán vị trí các button - căn giữa đối xứng trong khung."""
        # Căn giữa button theo chiều ngang của panel - dịch sang phải 5px để căn đối xứng
        button_x = self.x + (self.PANEL_WIDTH - self.BUTTON_WIDTH) // 2 + 5

        # Tính toán vị trí Y cho 4 button đầu tiên
        # Vùng khả dụng: từ sau logo (y=180) đến trước button QUIT
        top_area_start = self.y + 180
        bottom_area_end = self.y + self.PANEL_HEIGHT - self.BUTTON_HEIGHT - 25

        # Tính tổng chiều cao cần cho 4 button
        total_4_buttons_height = 4 * self.BUTTON_HEIGHT + 3 * self.BUTTON_GAP

        # Vùng giữa: từ top_area_start đến (bottom_area_end - khoảng cách)
        available_height = (
            bottom_area_end - top_area_start - 40
        )  # 40px gap trước QUIT button

        # Căn giữa 4 button trong vùng khả dụng
        start_y = top_area_start + (available_height - total_4_buttons_height) // 2

        # 4 button đầu tiên: UNDO MOVE, RESET MAZE, OPTIONS, WORLD MAP
        for i, label in enumerate(self.BUTTON_LABELS[:4]):
            button_y = start_y + i * (self.BUTTON_HEIGHT + self.BUTTON_GAP)
            self.button_rects[label] = pygame.Rect(
                button_x, button_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT
            )

        # Button QUIT TO MAIN ở dưới cùng - căn giữa đối xứng
        quit_y = self.y + self.PANEL_HEIGHT - self.BUTTON_HEIGHT - 25
        self.button_rects["QUIT TO MAIN"] = pygame.Rect(
            button_x, quit_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT
        )

    def handle_event(self, event: pygame.event.Event) -> str:
        """
        Xử lý sự kiện chuột.
        :param event: Sự kiện pygame
        :return: Tên button được click hoặc None
        """
        mouse_pos = pygame.mouse.get_pos()

        # Cập nhật trạng thái hover
        for label, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                if self.button_states[label] != "pressed":
                    self.button_states[label] = "hover"
            else:
                if self.button_states[label] != "pressed":
                    self.button_states[label] = "normal"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, rect in self.button_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.button_states[label] = "pressed"

                    # Hiệu ứng flash cho RESET MAZE
                    if label == "RESET MAZE":
                        self.reset_flash_timer = pygame.time.get_ticks()

                    return label

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for label in self.button_states.keys():
                if self.button_states[label] == "pressed":
                    self.button_states[label] = "normal"

        return None

    def update(self) -> None:
        """Cập nhật trạng thái panel."""
        mouse_pos = pygame.mouse.get_pos()
        for label, rect in self.button_rects.items():
            if self.button_states[label] != "pressed":
                if rect.collidepoint(mouse_pos):
                    self.button_states[label] = "hover"
                else:
                    self.button_states[label] = "normal"

    def draw(self, screen: pygame.Surface, score: int = 0) -> None:
        """
        Vẽ panel lên màn hình.
        :param screen: Surface pygame để vẽ
        :param score: Điểm số hiện tại
        """
        # Vẽ ảnh khung nền
        screen.blit(self.panel_img, (self.x, self.y))

        # Vẽ Score - hiển thị ngay trên button QUIT TO MAIN
        quit_rect = self.button_rects.get("QUIT TO MAIN")
        if quit_rect:
            center_x = self.x + self.PANEL_WIDTH // 2

            # Draw Score Number (Màu vàng cam)
            score_text = str(score)
            score_surface = self.score_font.render(score_text, True, (255, 200, 0))
            score_rect = score_surface.get_rect(center=(center_x, quit_rect.top - 65))
            screen.blit(score_surface, score_rect)

            # Draw "SCORE" label (Màu nâu tối)
            label_surface = self.score_label_font.render("SCORE", True, (60, 20, 20))
            label_rect = label_surface.get_rect(center=(center_x, quit_rect.top - 25))
            screen.blit(label_surface, label_rect)

        # Vẽ các button
        for label, rect in self.button_rects.items():
            state = self.button_states[label]

            # Chọn hình button dựa trên trạng thái
            if state == "pressed":
                btn_img = self.button_pressed_img
            elif state == "hover":
                btn_img = self.button_hover_img
            else:
                btn_img = self.button_img

            # Hiệu ứng flash cho RESET MAZE
            if label == "RESET MAZE" and self.reset_flash_timer > 0:
                elapsed = pygame.time.get_ticks() - self.reset_flash_timer
                if elapsed < self.reset_flash_duration:
                    flash_img = btn_img.copy()
                    flash_alpha = int(80 * (1 - elapsed / self.reset_flash_duration))
                    flash_img.fill(
                        (flash_alpha, flash_alpha, 0),
                        special_flags=pygame.BLEND_RGB_ADD,
                    )
                    btn_img = flash_img
                else:
                    self.reset_flash_timer = 0

            # Vẽ button
            screen.blit(btn_img, rect.topleft)

            # Vẽ text trên button
            text_color = (220, 200, 150)  # Màu vàng nhạt giống ảnh mẫu
            if state == "hover":
                text_color = (255, 240, 180)
            elif state == "pressed":
                text_color = (180, 160, 120)

            text_surface = self.font.render(label, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

class HintPackage:
    def __init__(self, tile_size: int = TILE_SIZE) -> None:
        self.TILE_SIZE= tile_size
        self.facing_direction = DOWN
        self.show_hint = False

        self.__hint_frame, self.__shadow_hint_frame = self.load_hint_image()
    
    def load_hint_image(self) -> Tuple[FrameSet, FrameSet]:
        """
        Load and scale the hint image according to tile size.
        
        Returns:
            Scaled hint surface"""
        hint_surface = load_and_scale_image(self.TILE_SIZE, "arrows.gif", use_colorkey=True)

        hint_shadow = load_and_scale_image(self.TILE_SIZE, "_arrows.gif", is_shadow=True)
        hint_shadow = get_black_shadow_surface(hint_shadow)

        w_frame = hint_surface.get_width() 
        h_frame = hint_surface.get_height() // 4

        hint_frames_list = extract_sprite_frames(hint_surface, w_frame, h_frame)
        shadow_frames_list = extract_sprite_frames(hint_shadow, w_frame, h_frame)

        #up, down, left, right

        res_hint_frames = FrameSet(hint_frames_list[3], hint_frames_list[0], hint_frames_list[2], hint_frames_list[1])
        res_shadow_frames = FrameSet(shadow_frames_list[3], shadow_frames_list[0], shadow_frames_list[2], shadow_frames_list[1])
        return (res_hint_frames, res_shadow_frames)

    def draw(self, screen: pygame.Surface, player_pos: List[int], facing_direction: str = None) -> None:
        if self.facing_direction == "WIN":
            return
        
        if facing_direction is None:
            facing_direction = self.facing_direction
        else:
            self.facing_direction = facing_direction

        # Calculate position to draw hint
        x, y = player_pos
        match facing_direction:
            case "UP":
                x, y = x, y - 1
            case "DOWN":
                x, y = x, y + 1
            case "LEFT":
                x, y = x - 1, y
            case "RIGHT":
                x, y = x + 1, y
        current_image = getattr(self.__hint_frame, facing_direction)
        current_shadow = getattr(self.__shadow_hint_frame, facing_direction)

        hint_x = MARGIN_LEFT + self.TILE_SIZE * (x - 1) + (self.TILE_SIZE - current_image.get_width()) // 2
        hint_y = MARGIN_TOP + self.TILE_SIZE * (y - 1) + (self.TILE_SIZE - current_image.get_height()) // 2

        screen.blit(current_shadow, (hint_x, hint_y))
        screen.blit(current_image, (hint_x, hint_y))

pygame.quit()
