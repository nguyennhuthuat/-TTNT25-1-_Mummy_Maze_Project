import pygame
# Direction constants
RIGHT = "RIGHT"
LEFT = "LEFT"
UP = "UP"
DOWN = "DOWN"

# Layout constants (kept module-level so classes can use them)
TILE_SIZE = 30  # Size of each tile in the grid !!!!!!!! CHANGE WHEN LOADING DIFFERENT MAP SIZES !!!!!!!!!
BACKDROP_WIDTH = 657 #575
BACKDROP_HEIGHT = 638 #558
GAME_FLOOR_WIDTH = 480
GAME_FLOOR_HEIGHT = 480
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 670

# BACKDROP MARGINS
MARGIN_BACKDROP_X = (SCREEN_WIDTH - BACKDROP_WIDTH) // 2 
MARGIN_BACKDROP_Y = (SCREEN_HEIGHT - BACKDROP_HEIGHT) // 2

# FLOOR MARGINS
MARGIN_LEFT = 88 + MARGIN_BACKDROP_X
MARGIN_TOP = 106 + MARGIN_BACKDROP_Y


# -----------------------------------------------------------------------------#
# ---------------------------------- MAIN LOBBY -------------------------------#
# -----------------------------------------------------------------------------#
# --- 4. Tạo các nút ---
BTN_WIDTH = 200
BTN_HEIGHT = 50
GAP = 20        # Khoảng cách giữa các nút
OFFSET_X = 50   # Độ lệch ra hai bên so với tâm
OFFSET_Y = 170  # Độ lệch xuống dưới so với tâm màn hình (để vào giữa bảng đá)

center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2

# --- 2. Set màu sắc và Font chữ ---
COLOR_BACKGROUND = (30, 30, 30)       # Màu nền 
COLOR_BUTTON = (139, 105, 20)         # Màu nút
COLOR_BUTTON_HOVER = (205, 92, 92)    # Màu nút khi di chuột qua
COLOR_TEXT = (255, 255, 255)      # Màu chữ



