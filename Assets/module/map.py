import os
from typing import List, Tuple
import pygame

from .settings import *


class MummyMazeMapManager:
    """Handles tile/stair drawing and tile graphics loading."""

    def __init__(
        self,
        length: int = 6,
        stair_position: Tuple[int, int] = (1, 7),
        map_data: List[List[str]] = None,
        tile_size: int = TILE_SIZE,
    ) -> None:
        self.length = length  # size of square map (length x length)
        # Map from tile id to a bound drawing method (set up using bound methods)
        # Will be populated after methods are available (we can set here using bound methods)
        self.map_data = map_data
        self.stair_positions = stair_position
        self.is_opening_gate = False

        self.TILE_SIZE = tile_size

        # padding to center walls/stairs based on map size
        self.padding_left = SCREEN_WIDTH // (10 * self.length) // 4
        self.padding_top = SCREEN_HEIGHT // (10 * self.length) * 2 + 1

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
            os.path.join("assets", "images", "stairs6.png")
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
                MARGIN_LEFT
                + self.TILE_SIZE * (row_i - 1)
                - self.top_stair.get_width()
                - 3
            )
            y = (
                MARGIN_TOP
                + self.TILE_SIZE * (col_i - 1)
                - self.top_stair.get_height()
                + self.TILE_SIZE
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
            print("length of map_data:", len(self.map_data[0]))

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
                elif tid:
                    # If tile id is unknown, warn and skip
                    print(
                        f"Warning: tile_id '{tid}' at ({col_index}, {row_index}) not found in database. Skipping drawing."
                    )


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
    BUTTON_LABELS = ["UNDO MOVE", "RESET MAZE", "OPTIONS", "WORLD MAP", "QUIT TO MAIN"]

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

        # Font cho text trên button - sử dụng VT323 từ Assets/Fonts
        font_path = os.path.join("assets", "Fonts", "VT323-Regular.ttf")
        self.font = pygame.font.Font(font_path, 30)
        self.score_font = pygame.font.Font(font_path, 55)
        self.score_label_font = pygame.font.Font(font_path, 40)

        # Trạng thái các button
        self.button_states = {label: "normal" for label in self.BUTTON_LABELS}
        self.button_rects = {}

        # Hiệu ứng flash cho RESET MAZE
        self.reset_flash_timer = 0
        self.reset_flash_duration = 300  # ms

        self._calculate_button_positions()

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


pygame.quit()
