import sys
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass
import random

import pygame

from Assets.module.map_collection import maps_collection  # Import a collection of maps

from Assets.module.utils import *
from Assets.module.map import MummyMazeMapManager
from Assets.module.explorer import MummyMazePlayerManager
from Assets.module.zombies import MummyMazeZombieManager
from Assets.module.scorpion import MummyMazeScorpionManager
from Assets.module.settings import *
from Assets.module.text import show_victory_window
from Assets.module.pointpackage import PersonalPointPackage, GlobalPointPackage



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
current_level_index = 0

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
                running
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

def main_game(current_level_index = current_level_index):
        
    
    map_length, stair_position, map_data, player_start, zombie_starts, BaseLevelScore = load_level(current_level_index)
    winning_position, goal_direction = get_winning_position(stair_position, map_length)
    
    current_tile_size = 480 // map_length  # Dynamically set tile size based on map length
    MummyMazeMap = MummyMazeMapManager(length = map_length, stair_position = stair_position, map_data = map_data, tile_size = current_tile_size)
    MummyExplorer = MummyMazePlayerManager(length = map_length, grid_position = player_start, map_data = map_data, tile_size=current_tile_size)
    MummyZombies = [MummyMazeZombieManager(length = map_length, grid_position = pos, map_data = map_data, tile_size=current_tile_size) for pos in zombie_starts]
    ScoreTracker = GlobalPointPackage(BaseLevelScore = BaseLevelScore)


    running = True
    ################### MAIN GAME LOOP ##################
    screen.blit(pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))  # Clear screen at start of game
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if not MummyZombies[0].movement_list and not MummyExplorer.movement_list:  # Only allow player input if zombies are standing
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        MummyExplorer.update_player_status(UP)

                    elif event.key == pygame.K_DOWN:
                        MummyExplorer.update_player_status(DOWN)

                    elif event.key == pygame.K_LEFT:
                        MummyExplorer.update_player_status(LEFT)

                    elif event.key == pygame.K_RIGHT:
                        MummyExplorer.update_player_status(RIGHT)

                    ####################### CHECK WIN CONDITION #######################
                    if winning_position and MummyExplorer.grid_position == winning_position and MummyExplorer.facing_direction == goal_direction:
                        
                        ScoreTracker.player.end_counting()
                        print(ScoreTracker.player.total_score)


                        continue_game = show_victory_window(
                            screen, clock, current_level_index + 1, elapsed_time=ScoreTracker.player.elapsed_time, base_score=ScoreTracker.player.base_score, bonus_score=ScoreTracker.player.bonus_score, total_score=ScoreTracker.player.total_score
                        )

                        if not continue_game:
                            running = False
                            continue

                        current_level_index += 1
                        if current_level_index < len(maps_collection):
                            ScoreTracker.player.reset()
                            map_length, stair_position, map_data, player_start, zombie_starts, ScoreTracker.player.max_score = load_level(current_level_index)
                            winning_position, goal_direction = get_winning_position(stair_position, map_length)

                            current_tile_size = 480 // map_length  # Dynamically set tile size based on map length
                            MummyMazeMap = MummyMazeMapManager(length = map_length, stair_position = stair_position, map_data = map_data, tile_size = current_tile_size)
                            MummyExplorer = MummyMazePlayerManager(length = map_length, grid_position = player_start, map_data = map_data, tile_size=current_tile_size)
                            MummyZombies = [MummyMazeZombieManager(length = map_length, grid_position = pos, map_data = map_data, tile_size=current_tile_size) for pos in zombie_starts]
                        else:
                            print("Congratulations! You have completed all levels!")
                            running = False


            
        MummyMazeMap.draw_map(screen)

        player_turn_completed = MummyExplorer.update_player(screen)

        for zombie in MummyZombies:
            if player_turn_completed:
                zombie.zombie_movement(MummyExplorer.grid_position)
            zombie.update_zombie(screen)
        MummyMazeMap.draw_walls(screen)


        # Check for win condition

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.04)

    pygame.quit()

def main(action = "lobby"):

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
                pygame.quit()
                sys.exit()

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