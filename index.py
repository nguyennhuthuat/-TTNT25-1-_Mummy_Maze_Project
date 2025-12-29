import os
import sys
import json
import time

from cryptography.fernet import Fernet
import pygame

from Assets.module.map_collection import maps_collection  # Import a collection of maps

from Assets.module.utils import *
from Assets.module.map import MummyMazeMapManager
from Assets.module.explorer import MummyMazePlayerManager
from Assets.module.zombies import MummyMazeZombieManager
from Assets.module.scorpion import MummyMazeScorpionManager
from Assets.module.settings import *
from Assets.module.pointpackage import PersonalPointPackage, GlobalPointPackage
from Assets.module.load_save_data import save_data, load_data



# ---------------------------------------------------------------------------- #
# ----------------------------Initial Game Setup------------------------------ #
# ---------------------------------------------------------------------------- #

# Pygame setup
pygame.init()
pygame.mixer.init() # Initialize the mixer module for sound 
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mummy Maze Deluxe - 25TNT1 - Dudes Chase Money")
clock = pygame.time.Clock()


# Font setup
try:
    main_font = pygame.font.SysFont("comic sans ms", 24) 
    footer_font = pygame.font.SysFont("comic sans ms", 14) # Thêm dòng này (size 14 thay vì 24)
    title_font = pygame.font.SysFont("comic sans ms", 50)
except Exception as e:
    main_font = pygame.font.Font(None, 36)
    footer_font = pygame.font.Font(None, 18) # Font mặc định nhỏ hơn
    title_font = pygame.font.Font(None, 52)


# Main game setup
game_data = load_data()
current_level = game_data["level"]

start_button = Button(
    0, # X tạm thời là 0
    center_y + 250, # Điều chỉnh số này để nút lên/xuống đúng vị trí bảng đá
    100, # Width 
    35,  # Height
    text="", 
    image_path="./assets/images/click_here_to_enter_button.png",
    hover_image_path="./assets/images/h_click_here_to_enter_button.png"
)
start_button.rect.centerx = SCREEN_WIDTH // 2
main_menu_buttons = [start_button]




#-------------------------------------------------------------------------------#
#---------------------------------Main function---------------------------------#
#-------------------------------------------------------------------------------#

def show_lose_window(screen):

    # Tải Background chính
    try:
        bg = pygame.image.load('./assets/images/background_window.png').convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg = None

    try:
        logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        print("Can't load logo image")

    try:
        main_font = pygame.font.SysFont("comic sans ms", 24) 
        footer_font = pygame.font.SysFont("comic sans ms", 14) # Thêm dòng này (size 14 thay vì 24)
        title_font = pygame.font.SysFont("comic sans ms", 50)
        font_btn = pygame.font.SysFont('Arial', 50, bold = 30)
    except Exception as e:
        main_font = pygame.font.Font(None, 36)
        footer_font = pygame.font.Font(None, 18) # Font mặc định nhỏ hơn
        title_font = pygame.font.Font(None, 52)

    # Màu sắc
    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # TẢI ẢNH BẢNG (Board)
    try:
        board_img = pygame.image.load('./assets/images/window.png').convert_alpha()
        scale_factor = 1.48
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.scale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x-250, center_y-150, 500, 300)

    #TẢI TÊN GAME
    scale_size = 1.2
    logo_img = pygame.image.load('./assets/images/menulogo.png').convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (logo_img.get_width() * scale_size, logo_img.get_height() * scale_size))
    logo_rect = logo_img.get_rect(center=(center_x, center_y - 250))

    #TẢI DÒNG "GAME OVER"
    game_over_img = pygame.image.load('./assets/images/game_over.png').convert_alpha()
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
    overlay.set_alpha(150) # Độ mờ (0-255)
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
                    user_action = "let user try again"; running = False
                elif rect_undo_move.collidepoint(mouse_pos):
                    user_action = "undo the previous move"; running = False
                elif rect_abandon_hope.collidepoint(mouse_pos):
                    user_action = "left"; running = False
                elif rect_save_and_quit.collidepoint(mouse_pos):
                    user_action = "save the game status"; running = False

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
        for rect, text in [(rect_try_again, "TRY AGAIN"), 
                           (rect_abandon_hope, "ABANDON HOPE"),
                           (rect_save_and_quit, "SAVE AND QUIT"),
                           (rect_undo_move, "UNDO MOVE")]:
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)
        
        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
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

def show_victory_window(screen, clock, current_level, elapsed_time=0, base_score = 0, bonus_score = 0, total_score=0):
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


def main_menu(screen, clock):
    try:
        main_font = pygame.font.SysFont("comic sans ms", 24) 
        footer_font = pygame.font.SysFont("comic sans ms", 14) # Thêm dòng này (size 14 thay vì 24)
        title_font = pygame.font.SysFont("comic sans ms", 50)
        font_btn = pygame.font.SysFont('Arial', 50, bold = 30)
    except Exception as e:
        main_font = pygame.font.Font(None, 36)
        footer_font = pygame.font.Font(None, 18) # Font mặc định nhỏ hơn
        title_font = pygame.font.Font(None, 52)

    # Màu sắc
    COLOR_BG_OVERLAY = (0, 0, 0)
    TEXT_COLOR       = (40, 20, 10)

    w, h = screen.get_size()
    center_x, center_y = w // 2, h // 2

    # Tải Background chính
    try:
        bg = pygame.image.load('./assets/images/background_window.png').convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg = None
    
    try:
        logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
        logo_icon = pygame.transform.scale(logo_image, (130, 130))
    except:
        print("Can't load logo image")


    # TẢI ẢNH WINDOW
    try:
        board_img = pygame.image.load('./assets/images/window.png').convert_alpha()
        scale_factor = 1.48
        new_w = int(board_img.get_width() * scale_factor)
        new_h = int(board_img.get_height() * scale_factor)
        board_img = pygame.transform.smoothscale(board_img, (new_w, new_h))
        board_rect = board_img.get_rect(center=(center_x, center_y))
    except:
        board_img = None
        board_rect = pygame.Rect(center_x - 250, center_y - 150, 500, 300)

    #TẢI TÊN GAME
    scale_size = 1.2
    logo_img = pygame.image.load('./assets/images/menulogo.png').convert_alpha()
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
    overlay.set_alpha(150) # Độ mờ (0-255)
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
        for rect, text in [(rect_classic_mode, "CLASSIC MODE"), 
                           (rect_tutorials, "TUTORIALS"),
                           (rect_adventure, "ADVENTURE"),
                           (rect_quit_game, "QUIT GAME")]:
            txt_surf = font_btn.render(text, True, TEXT_COLOR)
            txt_rect = txt_surf.get_rect(center=rect.center)
            screen.blit(txt_surf, txt_rect)

        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, TEXT_COLOR)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
        screen.blit(footer_text_surf, footer_text_rect)
        
        screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))


        pygame.display.flip()
        clock.tick(60)

def lobby(screen, clock):
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if start_button.is_clicked(event):
                return "main_menu"

        for button in main_menu_buttons:
            button.check_hover(mouse_pos)
        '''+ icon_buttons:'''

        screen.fill(COLOR_BACKGROUND)
        try:
            background_image = pygame.image.load("./assets/images/mummymazedeluxetitle.png")
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(background_image, (0, 0))
        except:
            pass

        try:
            logo_image = pygame.image.load("./assets/images/DudesChaseMoneyLogo.png").convert_alpha()
            logo_icon = pygame.transform.scale(logo_image, (130, 130))
            screen.blit(logo_icon, (30, SCREEN_HEIGHT - 120))
        except:
            pass

        for button in main_menu_buttons: 
            button.draw(screen) 
        '''+ icon_buttons'''

        footer_text_surf = footer_font.render("Version 1.0.1 | © 25TNT1 - Dudes Chase Money", True, COLOR_TEXT)
        footer_text_rect = footer_text_surf.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT)
        screen.blit(footer_text_surf, footer_text_rect)

        pygame.display.flip()
        clock.tick(60)

def main_game(current_level = current_level):
    def save():
        # Save game state before exiting
        game_data["level"] = current_level
        game_data["time_elapsed"] = ScoreTracker.player.current_time_elapsed
        game_data["bonus_score"] = ScoreTracker.player.bonus_score
        game_data["hint_penalty"] = ScoreTracker.player.hint_penalty
        if game_data["is_playing"]:
            game_data["explorer_position"] = MummyExplorer.grid_position.copy()
            game_data["explorer_direction"] = MummyExplorer.facing_direction
            game_data["zombie_positions"] = [zombie.grid_position.copy() for zombie in MummyZombies] if MummyZombies else []
            game_data["zombie_directions"] = [zombie.facing_direction for zombie in MummyZombies] if MummyZombies else []
            game_data["history_states"] = history_states.copy()
        else:
            game_data["explorer_position"] = None
            game_data["explorer_direction"] = None
            game_data["zombie_positions"] = None
            game_data["zombie_directions"] = None
            game_data["history_states"] = []
        save_data(game_data)
        
    map_length, stair_position, map_data, player_start, zombie_starts, BaseLevelScore = load_level(current_level)

    winning_position, goal_direction = get_winning_position(stair_position, map_length)
    
    current_tile_size = 480 // map_length  # Dynamically set tile size based on map length

    MummyMazeMap = MummyMazeMapManager(length = map_length, stair_position = stair_position, map_data = map_data, tile_size = current_tile_size)
    MummyExplorer = MummyMazePlayerManager(length = map_length, grid_position = player_start, map_data = map_data, tile_size=current_tile_size)
    MummyZombies = [MummyMazeZombieManager(length = map_length, grid_position = pos, map_data = map_data, tile_size=current_tile_size) for pos in zombie_starts] if zombie_starts else None
    ScoreTracker = GlobalPointPackage(BaseLevelScore = BaseLevelScore)
    history_states = []  # To store previous game states for undo functionality

    # If is_playing is True, load previous state
    if game_data["is_playing"]:
        if game_data["explorer_position"] is not None:
            MummyExplorer.grid_position = game_data["explorer_position"].copy()
            MummyExplorer.facing_direction = game_data["explorer_direction"]
        if MummyZombies and game_data["zombie_positions"] is not None:
            for idx, zombie in enumerate(MummyZombies):
                zombie.grid_position = game_data["zombie_positions"][idx].copy()
                zombie.facing_direction = game_data["zombie_directions"][idx]
        ScoreTracker.player.start_counting = time.time() - game_data["time_elapsed"]
        ScoreTracker.player.bonus_score = game_data["bonus_score"]
        ScoreTracker.player.hint_penalty = game_data["hint_penalty"]

        history_states = game_data["history_states"].copy()


    running = True
    ################### MAIN GAME LOOP ##################
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("ccccc")
                game_data["is_playing"] = True
                save()
                return "exit"
            if not MummyExplorer.movement_list and (not MummyZombies or all(not zombie.movement_list for zombie in MummyZombies)):  # Only allow player input if zombies are standing

                if event.type == pygame.KEYDOWN:

                    # Save current state before making a move
                    history_states.append({
                        "explorer_position": MummyExplorer.grid_position.copy(),
                        "explorer_direction": MummyExplorer.facing_direction,
                        "zombie_positions": [zombie.grid_position.copy() for zombie in MummyZombies] if MummyZombies else [],
                        "zombie_directions": [zombie.facing_direction for zombie in MummyZombies] if MummyZombies else [],
                        # scorpion pos, facing direction if any,
                        "time_elapsed": ScoreTracker.player.current_time_elapsed,
                        "bonus_score": ScoreTracker.player.bonus_score,
                        "hint_penalty": ScoreTracker.player.hint_penalty,
                        "is_opening_gate": MummyMazeMap.is_opening_gate
                    })

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
                    if winning_position and MummyExplorer.get_x() == winning_position[0] and MummyExplorer.get_y() == winning_position[1] and MummyExplorer.facing_direction == goal_direction:

                        # Stop counting time, caculate score (base score + bonus score)
                        ScoreTracker.player.end_counting()
                        game_data["is_playing"] = False
                        game_data["level"] = current_level + 1
                        save()

                        continue_game = show_victory_window(
                            screen, clock, current_level + 1, elapsed_time=ScoreTracker.player.elapsed_time, base_score=ScoreTracker.player.base_score, bonus_score=ScoreTracker.player.bonus_score, total_score=ScoreTracker.player.total_score
                        )

                        if not continue_game:
                            running = False
                            continue

                        current_level += 1
                        if current_level < len(maps_collection):
                            ScoreTracker.player.reset()
                            map_length, stair_position, map_data, player_start, zombie_starts, ScoreTracker.player.max_score = load_level(current_level)
                            winning_position, goal_direction = get_winning_position(stair_position, map_length)

                            current_tile_size = 480 // map_length  # Dynamically set tile size based on map length
                            MummyMazeMap = MummyMazeMapManager(length = map_length, stair_position = stair_position, map_data = map_data, tile_size = current_tile_size)
                            MummyExplorer = MummyMazePlayerManager(length = map_length, grid_position = player_start, map_data = map_data, tile_size=current_tile_size)
                            MummyZombies = [MummyMazeZombieManager(length = map_length, grid_position = pos, map_data = map_data, tile_size=current_tile_size) for pos in zombie_starts] if zombie_starts else None
                        else:
                            print("Congratulations! You have completed all levels!")
                            running = False

        ####################### CHECK LOSE CONDITION ####################### 
        for zombie in MummyZombies or []:
            if  MummyExplorer and MummyExplorer.get_x() == zombie.get_x() and MummyExplorer.get_y() == zombie.get_y():
                # Player has been caught by a zombie
                print("You have been caught by a mummy! Game Over.")

                game_data["is_playing"] = False
                save()

                user_choice = show_lose_window(screen)  
            
                if user_choice == "let user try again":
                    

                    return "main_menu" 
                elif user_choice == "undo the previous move":
                    # Placeholder for undo move function
                    if history_states:
                        last_state = history_states.pop()
                        MummyExplorer.grid_position = last_state["explorer_position"].copy()
                        MummyExplorer.facing_direction = last_state["explorer_direction"]
                        for idx, zombie in enumerate(MummyZombies or []):
                            zombie.grid_position = last_state["zombie_positions"][idx].copy()
                            zombie.facing_direction = last_state["zombie_directions"][idx]
                        ScoreTracker.player.start_counting = time.time() - last_state["time_elapsed"]
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

                break          
            
        screen.blit(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))  # Clear screen at start of game
    
        MummyMazeMap.draw_map(screen)
        player_turn_completed = MummyExplorer.update_player(screen)

        for zombie in MummyZombies or []:
            if player_turn_completed:
                zombie.zombie_movement(MummyExplorer.grid_position)
            zombie.update_zombie(screen)
        MummyMazeMap.draw_walls(screen)


        # Check for win condition

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.04)

    pygame.quit()



def main(action = "main_game"):

    '''
    ACTION FLOW: 
    lobby --> main_menu --> (enter classic mode --> main_game --> lobby) 
                                 |--> (open tutorials --> lobby)
                                 |--> (open adventure --> lobby)
                                 |--> (quit game --> exit)
    
    ACTION LIST: 
    lobby, main_menu, main_game, tutorials, adventure, exit
    '''
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