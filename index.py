import sys
import time
import math

import pygame

from Assets.module.map_collection import maps_collection  # Import a collection of maps

from Assets.module.utils import *
from Assets.module.map import MummyMazeMapManager, SidePanel, HintPackage
from Assets.module.explorer import MummyMazePlayerManager
from Assets.module.zombies import MummyMazeZombieManager
from Assets.module.scorpion import MummyMazeScorpionManager
from Assets.module.settings import *
from Assets.module.pointpackage import PersonalPointPackage, GlobalPointPackage
from Assets.module.load_save_data import save_data, load_data
from Assets.module.game_algorithms import Shortest_Path


# ---------------------------------------------------------------------------- #
# ----------------------------Initial Game Setup------------------------------ #
# ---------------------------------------------------------------------------- #

# Pygame setup
pygame.init()
pygame.mixer.init()  # Initialize the mixer module for sound
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mummy Maze Deluxe - 25TNT1 - Dudes Chase Money")
clock = pygame.time.Clock()


# Tải font chữ
try:
    main_font = pygame.font.SysFont("comic sans ms", 24)
    footer_font = pygame.font.SysFont("comic sans ms", 14)
    title_font = pygame.font.SysFont("Arial", 25, bold=True)
except Exception as e:
    main_font = pygame.font.Font(None, 36)
    footer_font = pygame.font.Font(None, 18)
    title_font = pygame.font.Font(None, 52)

# --- TẢI ÂM THANH ---
try:
    # 1. Nhạc nền (Music) - Thường dùng cho nhạc dài
    pygame.mixer.music.load("./assets/music/game.it")
    pygame.mixer.music.set_volume(0.5)  # Độ lớn từ 0.0 đến 1.0

    # 2. Hiệu ứng âm thanh (Sound) - Thường dùng cho tiếng động ngắn
    click_sound = pygame.mixer.Sound("./assets/sounds/click.wav")
    finish_sound = pygame.mixer.Sound("./assets/sounds/click.wav")
except Exception as e:
    print(f"Lỗi tải âm thanh: {e}")
    click_sound = None
    finish_sound = None

# Tải thanh loading
LOADING_BAR_X = 280
LOADING_BAR_Y = 546

# Kích thước mục tiêu
BAR_TARGET_WIDTH = 630
BAR_TARGET_HEIGHT = 22

try:
    # 1. Load ảnh gốc (340x24)
    img_orig = pygame.image.load("./assets/images/titlebar.png").convert_alpha()

    # 2. Kéo dài nó ra đúng kích thước khung rỗng (630x22)
    loading_bar_img = pygame.transform.scale(
        img_orig, (BAR_TARGET_WIDTH, BAR_TARGET_HEIGHT)
    )

    # 3. Lưu lại kích thước mới để dùng cho hàm chạy
    loading_bar_w = BAR_TARGET_WIDTH
    loading_bar_h = BAR_TARGET_HEIGHT

except Exception as e:
    loading_bar_img = None
    print(f"Lỗi tải ảnh loading: {e}")


# Main game setup
game_data = load_data()
current_level = game_data.get("current_level", 0)

start_button = Button(
    0,  # X tạm thời là 0
    center_y + 260,  # Điều chỉnh số này để nút lên/xuống đúng vị trí bảng đá
    100,  # Width
    35,  # Height
    text="",
    image_path="./assets/images/click_here_to_enter_button.png",
    hover_image_path="./assets/images/h_click_here_to_enter_button.png",
)
start_button.rect.centerx = SCREEN_WIDTH // 2
main_menu_buttons = [start_button]


# -------------------------------------------------------------------------------#
# ---------------------------------Main function---------------------------------#
# -------------------------------------------------------------------------------#


def show_lose_window(screen):

    # Tải Background chính
    try:
        bg = pygame.image.load("./assets/images/background_window.png").convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg = None

    try:
        logo_image = pygame.image.load(
            "./assets/images/DudesChaseMoneyLogo.png"
        ).convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        print("Can't load logo image")

    try:
        main_font = pygame.font.SysFont("comic sans ms", 24)
        footer_font = pygame.font.SysFont(
            "comic sans ms", 14
        )  # Thêm dòng này (size 14 thay vì 24)
        title_font = pygame.font.SysFont("comic sans ms", 50)
        font_btn = pygame.font.SysFont("Arial", 50, bold=30)
    except Exception as e:
        main_font = pygame.font.Font(None, 36)
        footer_font = pygame.font.Font(None, 18)  # Font mặc định nhỏ hơn
        title_font = pygame.font.Font(None, 52)

    # Màu sắc
    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # TẢI ẢNH BẢNG (Board)
    try:
        board_img = pygame.image.load("./assets/images/window.png").convert_alpha()
        scale_factor = 1.48
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.scale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x - 250, center_y - 150, 500, 300)

    # TẢI TÊN GAME
    scale_size = 1.2
    logo_img = pygame.image.load("./assets/images/menulogo.png").convert_alpha()
    logo_img = pygame.transform.scale(
        logo_img,
        (logo_img.get_width() * scale_size, logo_img.get_height() * scale_size),
    )
    logo_rect = logo_img.get_rect(center=(center_x, center_y - 250))

    # TẢI DÒNG "GAME OVER"
    game_over_img = pygame.image.load("./assets/images/game_over.png").convert_alpha()
    game_over_img = pygame.transform.scale(game_over_img, (300, 300))
    game_over_rect = game_over_img.get_rect(center=(center_x - 50, center_y + 120))

    # Định vị nút bấm
    btn_w, btn_h = 300, 100
    gap = 60

    rect_try_again = pygame.Rect(0, 0, btn_w, btn_h)
    rect_try_again.center = (center_x - (btn_w // 2 + gap), center_y + 190)

    rect_undo_move = pygame.Rect(0, 0, btn_w, btn_h)
    rect_undo_move.center = (center_x - (btn_w // 2 + gap), center_y + 190 + 90)

    rect_abandon_hope = pygame.Rect(0, 0, btn_w, btn_h)
    rect_abandon_hope.center = (center_x + (btn_w // 2 + gap), center_y + 190)

    rect_save_and_quit = pygame.Rect(0, 0, btn_w, btn_h)
    rect_save_and_quit.center = (center_x + (btn_w // 2 + gap), center_y + 190 + 90)

    # Tạo lớp phủ mờ (Alpha)
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(150)  # Độ mờ (0-255)
    overlay.fill(COLOR_BG_OVERLAY)

    running = True
    user_action = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_try_again.collidepoint(mouse_pos):
                    user_action = "let user try again"
                    running = False
                elif rect_undo_move.collidepoint(mouse_pos):
                    user_action = "undo the previous move"
                    running = False
                elif rect_abandon_hope.collidepoint(mouse_pos):
                    user_action = "left"
                    running = False
                elif rect_save_and_quit.collidepoint(mouse_pos):
                    user_action = "save the game status"
                    running = False

        # 1. Vẽ ảnh nền Game trước
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((100, 150, 100))

        screen.blit(overlay, (0, 0))

        screen.blit(logo_img, logo_rect)

        # 2. Vẽ lose_window
        if board_img:
            screen.blit(board_img, board_rect)
        else:
            pygame.draw.rect(screen, (210, 180, 140), board_rect)

        # Vẽ tên game
        screen.blit(logo_img, logo_rect)

        # Vẽ "GAME OVER"
        screen.blit(game_over_img, game_over_rect)

        # 3. Vẽ chữ lên các nút
        for rect, text in [
            (rect_try_again, "TRY AGAIN"),
            (rect_abandon_hope, "ABANDON HOPE"),
            (rect_save_and_quit, "SAVE AND QUIT"),
            (rect_undo_move, "UNDO MOVE"),
        ]:
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

        footer_text_surf = footer_font.render(
            "Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR
        )
        footer_text_rect = footer_text_surf.get_rect(
            centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT
        )
        screen.blit(footer_text_surf, footer_text_rect)

        screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))

        pygame.display.flip()

    return user_action


def draw_text_with_outline(
    screen, text, font, color, outline_color, center_pos, outline_width=2
):
    """
    Vẽ text với viền đen để dễ đọc hơn.
    """
    # Vẽ outline (viền đen)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                outline_rect = outline_surface.get_rect(
                    center=(center_pos[0] + dx, center_pos[1] + dy)
                )
                screen.blit(outline_surface, outline_rect)

    # Vẽ text chính
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    screen.blit(text_surface, text_rect)


def show_victory_window(
    screen,
    clock,
    current_level,
    elapsed_time=0,
    base_score=0,
    bonus_score=0,
    total_score=0,
):
    """
    Hiển thị cửa sổ chiến thắng với background Victorybackground.png.
    Text rõ ràng với viền đen để dễ đọc.

    Args:
        screen: Pygame screen surface
        clock: Pygame clock object
        current_level: Số thứ tự màn chơi vừa hoàn thành
        elapsed_time: Thời gian hoàn thành màn (giây)
        total_score: Tổng điểm tích lũy từ tất cả các màn

    Returns:
        tuple: (continue_game: bool, new_total_score: int)
    """
    # Load background image
    try:
        victory_bg = pygame.image.load("Assets/images/Victorybackground.png")
        victory_bg = pygame.transform.scale(victory_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Cannot load Victorybackground.png: {e}")
        victory_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        victory_bg.fill((30, 25, 20))

    screen.blit(victory_bg, (0, 0))

    # Load fonts - sử dụng VT323 font từ Assets/Fonts
    try:
        title_font = pygame.font.Font("Assets/Fonts/VT323-Regular.ttf", 60)
        info_font = pygame.font.Font("Assets/Fonts/VT323-Regular.ttf", 38)
        rank_font = pygame.font.Font("Assets/Fonts/VT323-Regular.ttf", 44)
        button_font = pygame.font.Font("Assets/Fonts/VT323-Regular.ttf", 36)
    except:
        title_font = pygame.font.Font(None, 55)
        info_font = pygame.font.Font(None, 32)
        rank_font = pygame.font.Font(None, 36)
        button_font = pygame.font.Font(None, 32)

    # Màu sắc - màu sáng hơn để nổi bật
    YELLOW = (255, 230, 0)
    ORANGE = (255, 160, 50)
    RED = (255, 80, 80)
    BLACK = (0, 0, 0)
    DARK_BROWN = (40, 30, 20)

    center_x = SCREEN_WIDTH // 2

    # === TITLE: "YOU HAVE ESCAPED THE MAZE!" ===
    # Vẽ shadow trước
    title_text = "YOU HAVE ESCAPED THE MAZE!"
    shadow_surface = title_font.render(title_text, True, DARK_BROWN)
    shadow_rect = shadow_surface.get_rect(center=(center_x + 3, 48))
    screen.blit(shadow_surface, shadow_rect)
    # Vẽ text chính với viền dày
    draw_text_with_outline(
        screen, title_text, title_font, YELLOW, BLACK, (center_x, 45), outline_width=4
    )

    # === Explorer sprite ===
    explorer_y = 160
    try:
        explorer_img = pygame.image.load("Assets/images/explorerlookingmap.png")
        explorer_img = pygame.transform.scale(explorer_img, (90, 90))
        explorer_rect = explorer_img.get_rect(center=(center_x, explorer_y))
        screen.blit(explorer_img, explorer_rect)
    except:
        pygame.draw.circle(screen, (200, 180, 140), (center_x, explorer_y), 35)

    # === Thông tin thời gian và điểm ===
    info_start_y = 260
    line_spacing = 50

    # Tính thời gian
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_str = f"Time: {minutes} minutes and {seconds} seconds"

    # Tính điểm màn này
    base_points = base_score
    bonus_points = bonus_score
    level_points = base_points + bonus_points

    # Cộng vào tổng điểm
    new_total_score = total_score + level_points

    # Vẽ các dòng thông tin với viền
    draw_text_with_outline(
        screen,
        time_str,
        info_font,
        ORANGE,
        BLACK,
        (center_x, info_start_y),
        outline_width=2,
    )

    draw_text_with_outline(
        screen,
        f"Base Points: +{base_points}",
        info_font,
        ORANGE,
        BLACK,
        (center_x, info_start_y + line_spacing),
        outline_width=2,
    )

    draw_text_with_outline(
        screen,
        f"Bonus Points: +{bonus_points}",
        info_font,
        ORANGE,
        BLACK,
        (center_x, info_start_y + line_spacing * 2),
        outline_width=2,
    )

    # === Rank info ===
    total_points = new_total_score

    # Định nghĩa ngưỡng rank
    rank_thresholds = [0, 150, 250, 1000]
    rank_names = ["Cursed!", "Novice", "Explorer", "Legend!"]

    # Tìm rank hiện tại
    current_rank_index = 0
    for i in range(len(rank_thresholds) - 1, -1, -1):
        if total_points >= rank_thresholds[i]:
            current_rank_index = i
            break

    rank = rank_names[current_rank_index]

    rank_y = info_start_y + line_spacing * 3 + 20
    draw_text_with_outline(
        screen,
        "Your current rank:",
        info_font,
        YELLOW,
        BLACK,
        (center_x, rank_y),
        outline_width=2,
    )

    draw_text_with_outline(
        screen, rank, rank_font, YELLOW, BLACK, (center_x, rank_y + 40), outline_width=2
    )

    # === Next rank info ===
    if current_rank_index < len(rank_names) - 1:
        next_threshold = rank_thresholds[current_rank_index + 1]
        draw_text_with_outline(
            screen,
            f"Next rank at {next_threshold} points",
            info_font,
            RED,
            BLACK,
            (center_x, rank_y + 95),
            outline_width=2,
        )
    else:
        draw_text_with_outline(
            screen,
            "Max rank achieved!",
            info_font,
            RED,
            BLACK,
            (center_x, rank_y + 95),
            outline_width=2,
        )

    # === Button "ENTER THE NEXT CHAMBER" ===
    button_y = SCREEN_HEIGHT - 55
    button_text = "ENTER THE NEXT CHAMBER"

    # Vẽ shadow cho button
    shadow_btn = button_font.render(button_text, True, DARK_BROWN)
    shadow_btn_rect = shadow_btn.get_rect(center=(center_x + 2, button_y + 2))
    screen.blit(shadow_btn, shadow_btn_rect)

    # Vẽ button với viền dày
    draw_text_with_outline(
        screen,
        button_text,
        button_font,
        YELLOW,
        BLACK,
        (center_x, button_y),
        outline_width=3,
    )

    # Vẽ underline đậm hơn
    button_surface = button_font.render(button_text, True, YELLOW)
    button_width = button_surface.get_width()
    underline_y = button_y + 22
    # Shadow underline
    pygame.draw.line(
        screen,
        DARK_BROWN,
        (center_x - button_width // 2 + 2, underline_y + 2),
        (center_x + button_width // 2 + 2, underline_y + 2),
        4,
    )
    # Main underline
    pygame.draw.line(
        screen,
        YELLOW,
        (center_x - button_width // 2, underline_y),
        (center_x + button_width // 2, underline_y),
        4,
    )

    # Tạo clickable rect cho button
    button_rect = pygame.Rect(
        center_x - button_width // 2 - 20, button_y - 20, button_width + 40, 60
    )

    pygame.display.flip()

    # === Chờ người chơi tương tác ===
    waiting = True
    result = True

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    result = False
                    waiting = False

            # Hover effect
            if event.type == pygame.MOUSEMOTION:
                screen.blit(victory_bg, (0, 0))

                # Vẽ lại title với shadow
                shadow_surface = title_font.render(title_text, True, DARK_BROWN)
                shadow_rect = shadow_surface.get_rect(center=(center_x + 3, 48))
                screen.blit(shadow_surface, shadow_rect)
                draw_text_with_outline(
                    screen,
                    title_text,
                    title_font,
                    YELLOW,
                    BLACK,
                    (center_x, 45),
                    outline_width=4,
                )

                try:
                    screen.blit(explorer_img, explorer_rect)
                except:
                    pygame.draw.circle(
                        screen, (200, 180, 140), (center_x, explorer_y), 35
                    )

                draw_text_with_outline(
                    screen,
                    time_str,
                    info_font,
                    ORANGE,
                    BLACK,
                    (center_x, info_start_y),
                    outline_width=2,
                )
                draw_text_with_outline(
                    screen,
                    f"Base Points: +{base_points}",
                    info_font,
                    ORANGE,
                    BLACK,
                    (center_x, info_start_y + line_spacing),
                    outline_width=2,
                )
                draw_text_with_outline(
                    screen,
                    f"Bonus Points: +{bonus_points}",
                    info_font,
                    ORANGE,
                    BLACK,
                    (center_x, info_start_y + line_spacing * 2),
                    outline_width=2,
                )
                draw_text_with_outline(
                    screen,
                    "Your current rank:",
                    info_font,
                    YELLOW,
                    BLACK,
                    (center_x, rank_y),
                    outline_width=2,
                )
                draw_text_with_outline(
                    screen,
                    rank,
                    rank_font,
                    YELLOW,
                    BLACK,
                    (center_x, rank_y + 40),
                    outline_width=2,
                )

                # Next rank info động
                if current_rank_index < len(rank_names) - 1:
                    next_threshold = rank_thresholds[current_rank_index + 1]
                    draw_text_with_outline(
                        screen,
                        f"Next rank at {next_threshold} points",
                        info_font,
                        RED,
                        BLACK,
                        (center_x, rank_y + 95),
                        outline_width=2,
                    )
                else:
                    draw_text_with_outline(
                        screen,
                        "Max rank achieved!",
                        info_font,
                        RED,
                        BLACK,
                        (center_x, rank_y + 95),
                        outline_width=2,
                    )

                # Button với hover - shadow và underline
                # Shadow button
                screen.blit(shadow_btn, shadow_btn_rect)

                if button_rect.collidepoint(event.pos):
                    hover_color = (255, 255, 180)  # Sáng hơn khi hover
                    draw_text_with_outline(
                        screen,
                        button_text,
                        button_font,
                        hover_color,
                        BLACK,
                        (center_x, button_y),
                        outline_width=4,
                    )
                    pygame.draw.line(
                        screen,
                        DARK_BROWN,
                        (center_x - button_width // 2 + 2, underline_y + 2),
                        (center_x + button_width // 2 + 2, underline_y + 2),
                        5,
                    )
                    pygame.draw.line(
                        screen,
                        hover_color,
                        (center_x - button_width // 2, underline_y),
                        (center_x + button_width // 2, underline_y),
                        5,
                    )
                else:
                    draw_text_with_outline(
                        screen,
                        button_text,
                        button_font,
                        YELLOW,
                        BLACK,
                        (center_x, button_y),
                        outline_width=3,
                    )
                    pygame.draw.line(
                        screen,
                        DARK_BROWN,
                        (center_x - button_width // 2 + 2, underline_y + 2),
                        (center_x + button_width // 2 + 2, underline_y + 2),
                        4,
                    )
                    pygame.draw.line(
                        screen,
                        YELLOW,
                        (center_x - button_width // 2, underline_y),
                        (center_x + button_width // 2, underline_y),
                        4,
                    )

                pygame.display.flip()

        clock.tick(60)

    return result


def run_loading_screen():
    # Phát nhạc nền (số -1 có nghĩa là lặp vô tận)
    if pygame.mixer.music.get_busy() == False:
        pygame.mixer.music.play(-1)

    progress = 0
    loading = True

    # Hàm nội bộ để vẽ chữ sóng
    def draw_wave_text(surface, text, font, color, outline_color, start_pos):
        base_x, base_y = start_pos
        current_x = base_x

        time_now = pygame.time.get_ticks()

        for i, char in enumerate(text):
            # --- TOÁN HỌC CHO HIỆU ỨNG SÓNG ---
            bounce_y = math.sin(time_now * 0.01 + i * 0.5) * 3

            # Vị trí của từng chữ cái cụ thể
            char_pos = (current_x, base_y + bounce_y)

            # Vẽ viền cho từng chữ cái
            offsets = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            for ox, oy in offsets:
                char_outline = font.render(char, True, outline_color)
                surface.blit(char_outline, (char_pos[0] + ox, char_pos[1] + oy))

            # Vẽ chữ cái chính
            char_surf = font.render(char, True, color)
            surface.blit(char_surf, char_pos)

            # Cập nhật tọa độ X cho chữ cái tiếp theo
            current_x += font.size(char)[0]

    # Tải background để vẽ (cho giống menu)
    try:
        bg_img = pygame.image.load("./assets/images/mummymazedeluxetitle.png")
        bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg_img = None

    while loading:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if progress < 100:
            progress += 0.45
        else:
            if loading:  # Chỉ phát 1 lần duy nhất khi vừa đầy
                if finish_sound:
                    finish_sound.play()
            loading = False

        # Vẽ Background
        screen.fill(COLOR_BACKGROUND)
        if bg_img:
            screen.blit(bg_img, (0, 0))

        # Vẽ Logo (Nếu muốn)
        try:
            logo_image = pygame.image.load(
                "./assets/images/DudesChaseMoneyLogo.png"
            ).convert_alpha()
            logo_icon = pygame.transform.scale(logo_image, (130, 130))
            screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))
        except:
            pass

        # 1. Vẽ Thanh Loading (Kéo dài 630x22)
        if loading_bar_img:
            current_w = int(BAR_TARGET_WIDTH * (progress / 100))
            if current_w > 0:
                screen.blit(
                    loading_bar_img,
                    (LOADING_BAR_X, LOADING_BAR_Y),
                    (0, 0, current_w, BAR_TARGET_HEIGHT),
                )

        # 2. VẼ CHỮ NHẢY KIỂU SÓNG TRUYỀN
        text_str = f"Loading... {int(progress)}%"

        start_x = 280
        start_y = 546 - 45  # Cách bên trên thanh bar 45 pixel

        draw_wave_text(
            screen, text_str, title_font, (255, 255, 255), (0, 0, 0), (start_x, start_y)
        )

        pygame.display.flip()


def lobby(screen, clock):
    run_loading_screen()
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if start_button.is_clicked(event):
                if click_sound:
                    click_sound.set_volume(0.5)
                    click_sound.play()  # Phát tiếng click
                return "main_menu"

        for button in main_menu_buttons:
            button.check_hover(mouse_pos)
        """+ icon_buttons:"""

        screen.fill(COLOR_BACKGROUND)
        try:
            background_image = pygame.image.load(
                "./assets/images/mummymazedeluxetitle.png"
            )
            background_image = pygame.transform.scale(
                background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            screen.blit(background_image, (0, 0))
        except:
            pass

        try:
            logo_image = pygame.image.load(
                "./assets/images/DudesChaseMoneyLogo.png"
            ).convert_alpha()
            logo_icon = pygame.transform.scale(logo_image, (130, 130))
            screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))
        except:
            pass

        for button in main_menu_buttons:
            button.draw(screen)

        if loading_bar_img:
            # Vẽ trực tiếp ảnh đã scale vào đúng vị trí X, Y
            screen.blit(loading_bar_img, (LOADING_BAR_X, LOADING_BAR_Y))

        footer_text_surf = footer_font.render(
            "Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, COLOR_TEXT
        )
        footer_text_rect = footer_text_surf.get_rect(
            centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT
        )
        screen.blit(footer_text_surf, footer_text_rect)

        pygame.display.flip()
        clock.tick(60)


def main_menu(screen, clock):
    try:
        main_font = pygame.font.SysFont("comic sans ms", 24)
        footer_font = pygame.font.SysFont(
            "comic sans ms", 14
        )  # Thêm dòng này (size 14 thay vì 24)
        title_font = pygame.font.SysFont("comic sans ms", 50)
        font_btn = pygame.font.SysFont("Arial", 50, bold=30)
    except Exception as e:
        main_font = pygame.font.Font(None, 36)
        footer_font = pygame.font.Font(None, 18)  # Font mặc định nhỏ hơn
        title_font = pygame.font.Font(None, 52)

    # Màu sắc
    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # Tải Background chính
    try:
        bg = pygame.image.load("./assets/images/background_window.png").convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg = None

    try:
        logo_image = pygame.image.load(
            "./assets/images/DudesChaseMoneyLogo.png"
        ).convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        print("Can't load logo image")

    # TẢI ẢNH WINDOW
    try:
        board_img = pygame.image.load("./assets/images/window.png").convert_alpha()
        scale_factor = 1.48
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.smoothscale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x - 250, center_y - 150, 500, 300)

    # TẢI TÊN GAME
    scale_size = 1.2
    logo_img = pygame.image.load("./assets/images/menulogo.png").convert_alpha()
    # logo_img = pygame.transform.smoothscale(logo_img, (int(logo_img.get_width() * scale_size), int(logo_img.get_height() * scale_size)))
    logo_rect = logo_img.get_rect(center=(center_x, center_y - 230))

    # Định vị nút bấm
    btn_w, btn_h = 300, 100
    gap = 60

    rect_classic_mode = pygame.Rect(0, 0, btn_w, btn_h)
    rect_classic_mode.center = (center_x - (btn_w // 2 + gap), center_y + 190)

    rect_adventure = pygame.Rect(0, 0, btn_w, btn_h)
    rect_adventure.center = (center_x - (btn_w // 2 + gap), center_y + 190 + 90)

    rect_tutorials = pygame.Rect(0, 0, btn_w, btn_h)
    rect_tutorials.center = (center_x + (btn_w // 2 + gap), center_y + 190)

    rect_quit_game = pygame.Rect(0, 0, btn_w, btn_h)
    rect_quit_game.center = (center_x + (btn_w // 2 + gap), center_y + 190 + 90)

    # Tạo lớp phủ mờ (Alpha)
    overlay = pygame.Surface((w, h))
    overlay.set_alpha(150)  # Độ mờ (0-255)
    overlay.fill(COLOR_BG_OVERLAY)

    running = True
    user_action = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rect_classic_mode.collidepoint(mouse_pos):
                    running = False
                    return "main_game"
                elif rect_tutorials.collidepoint(mouse_pos):
                    running = False
                    return "tutorials"
                elif rect_adventure.collidepoint(mouse_pos):
                    running = False
                    return "adventure"
                elif rect_quit_game.collidepoint(mouse_pos):
                    running = False
                    return "exit"

        # 1. Vẽ ảnh nền Game trước
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((100, 150, 100))

        screen.blit(overlay, (0, 0))

        screen.blit(logo_img, logo_rect)

        # 2. Vẽ lose_window
        if board_img:
            screen.blit(board_img, board_rect)
        else:
            pygame.draw.rect(screen, (210, 180, 140), board_rect)

        # Vẽ tên game
        screen.blit(logo_img, logo_rect)

        # 3. Vẽ chữ lên các nút
        for rect, text in [
            (rect_classic_mode, "CLASSIC MODE"),
            (rect_tutorials, "TUTORIALS"),
            (rect_adventure, "ADVENTURE"),
            (rect_quit_game, "QUIT GAME"),
        ]:
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

        footer_text_surf = footer_font.render(
            "Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR
        )
        footer_text_rect = footer_text_surf.get_rect(
            centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT
        )
        screen.blit(footer_text_surf, footer_text_rect)

        screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))

        pygame.display.flip()
        clock.tick(60)


def create_game_state_image(
    MummyMazeMap: MummyMazeMapManager,
    MummyExplorer: MummyMazePlayerManager,
    MummyZombies: list[MummyMazeZombieManager],
    MummyScorpions: list[MummyMazeScorpionManager],
    side_panel: SidePanel = None,
    ScoreTracker: GlobalPointPackage = None,
):
    # Calculate current level score
    score = ScoreTracker.player.total_score 

    new_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # 1. CLEAR SCREEN
    screen.blit(
        pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0)
    )  

    # 2. DRAW LEFT SIDE PANEL
    side_panel.update()
    side_panel.draw(new_screen, score)

    # 3. DRAW MAP (NOT INCLUDE WALLS)
    MummyMazeMap.draw_map(new_screen)

    # 3.1 DRAW TRAPS IF ANY
    MummyMazeMap.draw_trap(new_screen) 

    # 4. DRAW PLAYER
    if MummyMazeMap.is_kg_exists():
        player_turn_completed = MummyExplorer.update_player(new_screen, gate_opened=MummyMazeMap.gate_key.is_opening_gate())
    else:
        player_turn_completed = MummyExplorer.update_player(new_screen)
        
    # 5. DRAW ZOMBIES
    for zombie in MummyZombies or []:
        if MummyMazeMap.is_kg_exists():
            zombie.update_zombie(new_screen, gate_opened=MummyMazeMap.gate_key.is_opening_gate())
        else:
            zombie.update_zombie(new_screen)

    # 6. DRAW SCORPIONS
    for scorpion in MummyScorpions or []:
        if MummyMazeMap.is_kg_exists():
            scorpion.update_scorpion(new_screen, gate_opened=MummyMazeMap.gate_key.is_opening_gate())
        else:
            scorpion.update_scorpion(new_screen)

    # 7. DRAW KEY & GATE IF ANY
    MummyMazeMap.draw_gate_key(new_screen)

    # 8. DRAW WALLS OVER EVERYTHING
    MummyMazeMap.draw_walls(new_screen)

    return new_screen


def main_game(current_level= 1):

    def save(is_playing = False):
        # Save game state before exiting
        game_data["is_playing"] = is_playing
        game_data["level"] = current_level + 1
        game_data["time_elapsed"] = ScoreTracker.player.current_time_elapsed
        game_data["bonus_score"] = ScoreTracker.player.bonus_score
        game_data["hint_penalty"] = ScoreTracker.player.hint_penalty
        game_data["total_score"] = ScoreTracker.player.total_score

        if game_data["is_playing"]:
            game_data["explorer_position"] = MummyExplorer.grid_position.copy()
            game_data["explorer_direction"] = MummyExplorer.facing_direction
            game_data["zombie_positions"] = (
                [zombie.grid_position.copy() for zombie in MummyZombies]
                if MummyZombies
                else []
            )
            game_data["zombie_directions"] = (
                [zombie.facing_direction for zombie in MummyZombies]
                if MummyZombies
                else []
            )

            game_data["scorpion_positions"] = (
                [scorpion.grid_position.copy() for scorpion in MummyScorpions]
                if MummyScorpions
                else []
            )
            game_data["scorpion_directions"] = (
                [scorpion.facing_direction for scorpion in MummyScorpions]
                if MummyScorpions
                else []
            )
            game_data["history_states"] = history_states.copy()
        else:
            game_data["explorer_position"] = None
            game_data["explorer_direction"] = None
            game_data["zombie_positions"] = None
            game_data["zombie_directions"] = None
            game_data["scorpion_positions"] = None
            game_data["scorpion_directions"] = None
            game_data["history_states"] = []
            game_data["bonus_score"] = 0
            game_data["hint_penalty"] = 0
            game_data["time_elapsed"] = 0
        save_data(game_data)

    (
        map_length,
        stair_position,
        map_data,
        player_start,
        zombie_starts,
        scorpion_starts,
        BaseLevelScore,
    ) = load_level(current_level)

    winning_position, goal_direction = get_winning_position(stair_position, map_length)

    current_tile_size = (
        480 // map_length
    )  # Dynamically set tile size based on map length

#--------------------------------------------------------#
#------------INITIALIZE GAME OBJECTS HERE----------------#
#--------------------------------------------------------#
    # flag to track if player has completed their turn
    player_turn_completed = False

    MummyMazeMap = MummyMazeMapManager(
        length=map_length,
        stair_position=stair_position,
        data=map_data,
        tile_size=current_tile_size,
    )
    MummyExplorer = MummyMazePlayerManager(
        length=map_length,
        grid_position=player_start,
        data=map_data,
        tile_size=current_tile_size,
    )
    MummyZombies = (
        [
            MummyMazeZombieManager(
                length=map_length,
                grid_position=pos,
                data=map_data,
                tile_size=current_tile_size,
            )
            for pos in zombie_starts
        ]
        if zombie_starts
        else None
    )
    MummyScorpions = (
        [
            MummyMazeScorpionManager(
                length=map_length,
                grid_position=pos,
                data=map_data,
                tile_size=current_tile_size,
            )
            for pos in scorpion_starts
        ]
        if scorpion_starts
        else None
    )
    ScoreTracker = GlobalPointPackage(BaseLevelScore=BaseLevelScore)

    # To store previous game states for undo functionality
    history_states = []  

    # Khởi tạo SidePanel (khung bên trái với các button) - căn giữa cùng với game
    side_panel = SidePanel(x=MARGIN_LEFT_OFFSET, y=16)

    # Initialize hint package
    hint = HintPackage(current_tile_size)

    #----------------------------------------------------------------------#
    #-----------------------HANDLE LOADED GAME STATE-----------------------#
    #----------------------------------------------------------------------#

    # If is_playing is True, load previous state
    if game_data.get("is_playing", False):

        # Explorer
        if game_data.get("explorer_position", None) is not None and game_data.get("explorer_direction", None) is not None:
            MummyExplorer.grid_position = game_data["explorer_position"].copy()
            MummyExplorer.facing_direction = game_data["explorer_direction"]

        # Zombies
        if MummyZombies and game_data.get("zombie_positions", None) is not None and \
            game_data.get("zombie_directions", None) is not None:
            saved_zombie_positions = game_data["zombie_positions"]
            saved_zombie_directions = game_data.get("zombie_directions", []) # facing directions
            
            # if counts match, restore positions and directions
            if len(saved_zombie_positions) == len(MummyZombies):
                for idx, zombie in enumerate(MummyZombies):
                    zombie.grid_position = saved_zombie_positions[idx].copy()
                    if idx < len(saved_zombie_directions):
                        zombie.facing_direction = saved_zombie_directions[idx]
            else:
                print(f"Warning: Zombie count mismatch. Using default positions.")
                game_data["is_playing"] = False
        
        # Scorpions
        if MummyScorpions and game_data.get("scorpion_positions", None) is not None and \
            game_data.get("scorpion_directions", None) is not None:
            saved_scorpion_positions = game_data["scorpion_positions"]
            saved_scorpion_directions = game_data.get("scorpion_directions", []) # facing directions
            
            # if counts match, restore positions and directions
            if len(saved_scorpion_positions) == len(MummyScorpions):
                for idx, scorpion in enumerate(MummyScorpions):
                    scorpion.grid_position = saved_scorpion_positions[idx].copy()
                    if idx < len(saved_scorpion_directions):
                        scorpion.facing_direction = saved_scorpion_directions[idx]
            else:
                print(f"Warning: Scorpion count mismatch. Using default positions.")
                game_data["is_playing"] = False


        # ScoreTracker
        ScoreTracker.player.start_counting = time.time() - game_data.get(
            "time_elapsed", 0
        )
        ScoreTracker.player.bonus_score = game_data.get("bonus_score", 0)
        ScoreTracker.player.hint_penalty = game_data.get("hint_penalty", 0)

        # History States
        history_states = (
            game_data.get("history_states", []).copy()
        )

    # Start game effect
    copied_image_screen = create_game_state_image(
        MummyMazeMap, MummyExplorer, MummyZombies, MummyScorpions, side_panel=side_panel, ScoreTracker=ScoreTracker
    )
    MummyExplorer.start_game_effect(
        screen,
        copied_image_screen,
        [MummyExplorer.get_x(), MummyExplorer.get_y()],
        MummyExplorer.facing_direction,
    )

    # Reset time after effect
    if game_data.get("is_playing", False):
        ScoreTracker.player.start_counting = time.time() - game_data.get("time_elapsed", 0)
    else:
        ScoreTracker.player.start_counting = time.time()

    #--------------------------------------------------------#
    #----------------------MAIN GAME-------------------------#
    #--------------------------------------------------------#
    running = True
    player_moved = False   # To track if player made a move this turn
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_data["is_playing"] = True
                save(is_playing= True)
                return "exit"

            # Xử lý sự kiện SidePanel
            panel_clicked = side_panel.handle_event(event)
            if panel_clicked == "UNDO MOVE":
                if history_states != []:
                    last_state = history_states.pop()

                    MummyExplorer.grid_position = last_state["explorer_position"].copy()
                    MummyExplorer.facing_direction = last_state["explorer_direction"]

                    for idx, zombie in enumerate(MummyZombies or []):
                        if idx < len(last_state["zombie_positions"]):
                            zombie.grid_position = last_state["zombie_positions"][
                                idx
                            ].copy()
                            zombie.facing_direction = last_state["zombie_directions"][
                                idx
                            ]

                    for idx, scorpion in enumerate(MummyScorpions or []):
                        if idx < len(last_state["scorpion_positions"]):
                            scorpion.grid_position = last_state["scorpion_positions"][
                                idx
                            ].copy()
                            scorpion.facing_direction = last_state["scorpion_directions"][
                                idx
                            ]
                    
                    ScoreTracker.player.start_counting = (
                        time.time() - last_state["time_elapsed"]
                    )
                    ScoreTracker.player.bonus_score = last_state["bonus_score"]
                    ScoreTracker.player.hint_penalty = last_state["hint_penalty"]
                    MummyMazeMap.is_opening_gate = last_state["is_opening_gate"]

                    # 
                    ScoreTracker.player.hint_penalty += 1
            
            elif panel_clicked == "RESET MAZE":
                
                # Reset side panel buttons first
                side_panel.reset_button_states()

                (
                    map_length,
                    stair_position,
                    map_data,
                    player_start,
                    zombie_starts,
                    scorpion_starts,
                    BaseLevelScore,
                ) = load_level(current_level)

                winning_position, goal_direction = get_winning_position(
                    stair_position, map_length
                )

                current_tile_size = 480 // map_length
                MummyMazeMap = MummyMazeMapManager(
                    length=map_length,
                    stair_position=stair_position,
                    data=map_data,
                    tile_size=current_tile_size,
                )
                MummyExplorer = MummyMazePlayerManager(
                    length=map_length,
                    grid_position=player_start,
                    data=map_data,
                    tile_size=current_tile_size,
                )
                MummyZombies = (
                    [
                        MummyMazeZombieManager(
                            length=map_length,
                            grid_position=pos,
                            data=map_data,
                            tile_size=current_tile_size,
                        )
                        for pos in zombie_starts
                    ]
                    if zombie_starts
                    else None
                )

                MummyScorpions = (
                    [
                        MummyMazeScorpionManager(
                            length=map_length,
                            grid_position=pos,
                            data=map_data,
                            tile_size=current_tile_size,
                        )
                        for pos in scorpion_starts
                    ]
                    if scorpion_starts
                    else None
                )

                # Start game effect
                copied_image_screen = create_game_state_image(
                    MummyMazeMap, MummyExplorer, MummyZombies, MummyScorpions, side_panel=side_panel, ScoreTracker=ScoreTracker
                )
                MummyExplorer.start_game_effect(
                    screen,
                    copied_image_screen,
                    [MummyExplorer.get_x(), MummyExplorer.get_y()],
                    MummyExplorer.facing_direction,
                )

                ScoreTracker.player.reset()
                ScoreTracker.player.start_counting = time.time()
                history_states = []

            elif panel_clicked == "OPTIONS":
                pass  # Thêm hiệu ứng mở bảng options vào
            
            elif panel_clicked == "HINT":
                path = Shortest_Path(
                    map_data, 
                    tuple(MummyExplorer.grid_position), 
                    tuple(winning_position), 
                    zombie_positions = [tuple(zombie.grid_position + [zombie.zombie_type]) for zombie in MummyZombies] if MummyZombies else [],
                    scorpion_positions = [tuple(scorpion.grid_position + [scorpion.scorpion_type]) for scorpion in MummyScorpions] if MummyScorpions else []
                    ) 
                
                if path == []:
                    print("Can't find the way to win. You lose!")
                else:
                    face_direction = get_face_direction(path[0], path[1], MummyMazeMap.map_data) if len(path) >=2 else "WIN"
                    hint.show_hint = True
                    hint.facing_direction = face_direction

                    ScoreTracker.player.hint_penalty += 5  # Increase hint penalty
            
            elif panel_clicked == "QUIT TO MAIN":
                game_data["is_playing"] = True
                save(is_playing= True)
                return "main_menu"

            if not MummyExplorer.movement_list and (
                not MummyZombies
                or all(not zombie.movement_list for zombie in MummyZombies)
            ):  # Only allow player input if zombies are standing

                player_moved = True  # Player is about to make a move
                if event.type == pygame.KEYDOWN:
                    # change show_hint to False when player makes a move
                    hint.show_hint = False

                    # Save current state before making a move
                    history_states.append(
                        {
                            "explorer_position": MummyExplorer.grid_position.copy(),
                            "explorer_direction": MummyExplorer.facing_direction,
                            "zombie_positions": (
                                [zombie.grid_position.copy() for zombie in MummyZombies]
                                if MummyZombies
                                else []
                            ),
                            "zombie_directions": (
                                [zombie.facing_direction for zombie in MummyZombies]
                                if MummyZombies
                                else []
                            ),
                            "scorpion_positions": (
                                [scorpion.grid_position.copy() for scorpion in MummyScorpions]
                                if MummyScorpions
                                else []
                            ),
                            "scorpion_directions": (
                                [scorpion.facing_direction for scorpion in MummyScorpions]
                                if MummyScorpions
                                else []
                            ),
                            "time_elapsed": ScoreTracker.player.current_time_elapsed,
                            "bonus_score": ScoreTracker.player.bonus_score,
                            "hint_penalty": ScoreTracker.player.hint_penalty,
                            "is_opening_gate": MummyMazeMap.gate_key.is_opening_gate() if MummyMazeMap.is_kg_exists() else True,
                        }
                    )

                    # Handle player movement
                    if event.key == pygame.K_UP:
                        MummyExplorer.update_player_status(UP)

                    elif event.key == pygame.K_DOWN:
                        MummyExplorer.update_player_status(DOWN)

                    elif event.key == pygame.K_LEFT:
                        MummyExplorer.update_player_status(LEFT)

                    elif event.key == pygame.K_RIGHT:
                        MummyExplorer.update_player_status(RIGHT)

                    ####################### CHECK WIN CONDITION #######################
                    if (
                        winning_position
                        and MummyExplorer.get_x() == winning_position[0]
                        and MummyExplorer.get_y() == winning_position[1]
                        and MummyExplorer.facing_direction == goal_direction
                    ):

                        # Stop counting time, caculate score (base score + bonus score)
                        ScoreTracker.player.end_counting()
                        game_data["is_playing"] = False
                        save(is_playing= False)

                        continue_game = show_victory_window(
                            screen,
                            clock,
                            current_level + 1,
                            elapsed_time=ScoreTracker.player.elapsed_time,
                            base_score=ScoreTracker.player.base_score,
                            bonus_score=ScoreTracker.player.bonus_score,
                            total_score=ScoreTracker.player.total_score
                            - ScoreTracker.player.base_score
                            - ScoreTracker.player.bonus_score,
                        )

                        if not continue_game:
                            running = False
                            continue

                        current_level += 1
                        if current_level < len(maps_collection):
                            prev_facing = MummyExplorer.facing_direction

                            ScoreTracker.player.reset()
                            (
                                map_length,
                                stair_position,
                                map_data,
                                player_start,
                                zombie_starts,
                                scorpion_starts,
                                ScoreTracker.player.max_score,
                            ) = load_level(current_level)
                            winning_position, goal_direction = get_winning_position(
                                stair_position, map_length
                            )

                            current_tile_size = (
                                480 // map_length
                            )  # Dynamically set tile size based on map length
                            MummyMazeMap = MummyMazeMapManager(
                                length=map_length,
                                stair_position=stair_position,
                                data=map_data,
                                tile_size=current_tile_size,
                            )
                            MummyExplorer = MummyMazePlayerManager(
                                length=map_length,
                                grid_position=player_start,
                                data=map_data,
                                tile_size=current_tile_size,
                            )
                            MummyZombies = (
                                [
                                    MummyMazeZombieManager(
                                        length=map_length,
                                        grid_position=pos,
                                        data=map_data,
                                        tile_size=current_tile_size,
                                    )
                                    for pos in zombie_starts
                                ]
                                if zombie_starts
                                else None
                            )
                            MummyScorpions = (
                                [
                                    MummyMazeScorpionManager(
                                        length=map_length,
                                        grid_position=pos,
                                        data=map_data,
                                        tile_size=current_tile_size,
                                    )
                                    for pos in scorpion_starts
                                ]
                                if scorpion_starts
                                else None
                            )
                            history_states = []  # Reset history states for new level

                            # Start game effect for new level
                            MummyExplorer.facing_direction = prev_facing
                            copied_image_screen = create_game_state_image(
                                MummyMazeMap, MummyExplorer, MummyZombies, MummyScorpions, side_panel=side_panel, ScoreTracker=ScoreTracker
                            )
                            MummyExplorer.start_game_effect(
                                screen,
                                copied_image_screen,
                                [MummyExplorer.get_x(), MummyExplorer.get_y()],
                                MummyExplorer.facing_direction,
                            )

                            # Reset time after effect
                            if game_data["is_playing"]:
                                ScoreTracker.player.start_counting = (
                                    time.time() - game_data["time_elapsed"]
                                )
                            else:
                                ScoreTracker.player.start_counting = time.time()
                        else:
                            print("Congratulations! You have completed all levels!")
                            running = False
                            return "main_menu"


        
        #------------------------------------------------------------------------------------#
        #------------------------------- CHECK LOSE CONDITION -------------------------------#
        #------------------------------------------------------------------------------------#
        reason = None
        if MummyExplorer.is_in_trap:
            reason = "Trapped"
        for zombie in MummyZombies or []:
            if (
                MummyExplorer
                and MummyExplorer.get_x() == zombie.get_x()
                and MummyExplorer.get_y() == zombie.get_y()
            ):
                # Player has been caught by a zombie
                reason = "Zombie"
                break
        for scorpion in MummyScorpions or []:
            if (
                MummyExplorer
                and MummyExplorer.get_x() == scorpion.get_x()
                and MummyExplorer.get_y() == scorpion.get_y()
            ):
                # Player has been caught by a scorpion
                reason = "Scorpion"
                break

        if reason is not None:
            MummyExplorer.start_lose_effect(screen, reason=reason)
            game_data["is_playing"] = False
            save(is_playing = False)

            user_choice = show_lose_window(screen)

            if user_choice == "let user try again":

                return "main_menu"
            elif user_choice == "undo the previous move":
                # Placeholder for undo move function
                if history_states != []:
                    last_state = history_states.pop()
                    MummyExplorer.grid_position = last_state[
                        "explorer_position"
                    ].copy()
                    MummyExplorer.facing_direction = last_state[
                        "explorer_direction"
                    ]
                    for idx, zombie in enumerate(MummyZombies or []):
                        zombie.grid_position = last_state["zombie_positions"][
                            idx
                        ].copy()
                        zombie.facing_direction = last_state["zombie_directions"][
                            idx
                        ]
                    ScoreTracker.player.start_counting = (
                        time.time() - last_state["time_elapsed"]
                    )
                    ScoreTracker.player.bonus_score = last_state["bonus_score"]
                    ScoreTracker.player.hint_penalty = last_state["hint_penalty"]
                    MummyMazeMap.is_opening_gate = last_state["is_opening_gate"]
                else:
                    return "main_game"
            elif user_choice == "left":
                return "lobby"
            elif user_choice == "save the game status":
                # Placeholder for save game function
                return "exit"


        # Calculate total_score
        display_score = ScoreTracker.player.total_score
        
        # -------------------------------------------------------- #
        # ------------------- RENDERING/DRAW---------------------- #
        # -------------------------------------------------------- #
        
        # 1. CLEAR SCREEN
        screen.blit(
            pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0)
        )  

        # 2. DRAW LEFT SIDE PANEL
        side_panel.update()
        side_panel.draw(screen, display_score)

        # 3. DRAW MAP (NOT INCLUDE WALLS)
        MummyMazeMap.draw_map(screen)

        # 3.1 DRAW TRAPS & KEY IF ANY
        MummyMazeMap.draw_trap(screen) 

        # NO NEED TO DRAW KEY TWICE 
        # if MummyMazeMap.is_kg_exists() and MummyMazeMap.gate_key.is_opening_gate():
        #     MummyMazeMap.draw_gate_key(screen)

        # 4. DRAW PLAYER
        if MummyMazeMap.is_kg_exists():
            player_turn_completed = MummyExplorer.update_player(screen, gate_opened=MummyMazeMap.gate_key.is_opening_gate())
        else:
            player_turn_completed = MummyExplorer.update_player(screen)
        
        # 5. DRAW ZOMBIES
        for zombie in MummyZombies or []:
            if player_turn_completed:
                zombie.zombie_movement(MummyExplorer.grid_position)
            
            if MummyMazeMap.is_kg_exists():
                zombie.update_zombie(screen, gate_opened=MummyMazeMap.gate_key.is_opening_gate())
            else:
                zombie.update_zombie(screen)

        # 6. DRAW SCORPIONS
        for scorpion in MummyScorpions or []:
            if player_turn_completed:
                scorpion.scorpion_movement(MummyExplorer.grid_position)
            
            if MummyMazeMap.is_kg_exists():
                scorpion.update_scorpion(screen, gate_opened=MummyMazeMap.gate_key.is_opening_gate())
            else:
                scorpion.update_scorpion(screen)

        # 7. DRAW KEY & GATE IF ANY
        MummyMazeMap.draw_gate_key(screen)

        # 8. DRAW HINT IF ANY
        if hint.show_hint:
            hint.draw(screen, (MummyExplorer.get_x(), MummyExplorer.get_y()))

        # 9. DRAW WALLS OVER EVERYTHING
        MummyMazeMap.draw_walls(screen)
        # if MummyMazeMap.is_kg_exists() and not MummyMazeMap.gate_key.is_opening_gate():
        #     MummyMazeMap.draw_gate_key(screen)

        

        #---- CHECK IF PLAYER TOUCH KEY/ TOUCH TRAPS ----#
        if player_turn_completed:
            if MummyMazeMap.is_kg_exists():
                if MummyExplorer.get_x() == MummyMazeMap.gate_key.get_key_pos()[0] and MummyExplorer.get_y() ==  MummyMazeMap.gate_key.get_key_pos()[1]:
                    if MummyMazeMap.gate_key.is_finished_changeing_gate_status() and player_moved:
                        MummyMazeMap.gate_key.change_gate_status()
                        player_moved = False

        pygame.display.flip()
        clock.tick(120)
        time.sleep(0.04)

    pygame.quit()


def main(action="main_game"):
    """
    ACTION FLOW:
    lobby --> main_menu --> (enter classic mode --> main_game --> lobby)
                                 |--> (open tutorials --> lobby)
                                 |--> (open adventure --> lobby)
                                 |--> (quit game --> exit)

    ACTION LIST:
    lobby, main_menu, main_game, tutorials, adventure, exit
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                action = "exit"

        if action == "lobby":
            action = lobby(screen, clock)

        elif action == "main_menu":
            action = main_menu(screen, clock)

        elif action == "main_game":
            action = main_game()

        elif action == "tutorials":
            # Placeholder for tutorials function
            action = "lobby"

        elif action == "adventure":
            # Placeholder for adventure function
            action = "lobby"

        elif action == "exit":

            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
