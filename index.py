import os
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass
import random

import pygame

from Assets.module.map_collection import maps_collection  # Import a collection of maps

from Assets.module.utils import load_level, get_winning_position
from Assets.module.map import MummyMazeMapManager
from Assets.module.explorer import MummyMazePlayerManager
from Assets.module.zombies import MummyMazeZombieManager
from Assets.module.scorpion import MummyMazeScorpionManager
from Assets.module.settings import SCREEN_WIDTH, SCREEN_HEIGHT, UP, DOWN, LEFT, RIGHT


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


def show_victory_window(screen, clock, current_level, elapsed_time=0, total_score=0):
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
    base_points = 110
    bonus_points = max(0, 100 - int(elapsed_time))
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
                return False, new_total_score

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

    return result, new_total_score


def main():

    pygame.init()
    pygame.mixer.init()  # Initialize the mixer module for sound

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Mummy Maze Deluxe")
    clock = pygame.time.Clock()

    current_level_index = 0
    level_start_time = time.time()  # Bắt đầu đếm thời gian
    total_score = 0  # Tổng điểm tích lũy

    map_length, stair_position, map_data, player_start, zombie_starts = load_level(
        current_level_index
    )
    winning_position = get_winning_position(stair_position, map_length)

    current_tile_size = (
        480 // map_length
    )  # Dynamically set tile size based on map length
    MummyMazeMap = MummyMazeMapManager(
        length=map_length,
        stair_position=stair_position,
        map_data=map_data,
        tile_size=current_tile_size,
    )
    MummyExplorer = MummyMazePlayerManager(
        length=map_length,
        grid_position=player_start,
        map_data=map_data,
        tile_size=current_tile_size,
    )
    MummyZombies = [
        MummyMazeZombieManager(
            length=map_length,
            grid_position=pos,
            map_data=map_data,
            tile_size=current_tile_size,
        )
        for pos in zombie_starts
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if (
                not MummyZombies[0].movement_list and not MummyExplorer.movement_list
            ):  # Only allow player input if zombies are standing
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        MummyExplorer.update_player_status(UP)

                    elif event.key == pygame.K_DOWN:
                        MummyExplorer.update_player_status(DOWN)

                    elif event.key == pygame.K_LEFT:
                        MummyExplorer.update_player_status(LEFT)

                    elif event.key == pygame.K_RIGHT:
                        MummyExplorer.update_player_status(RIGHT)

        # Kiểm tra win condition TRƯỚC khi vẽ
        if winning_position and MummyExplorer.grid_position == winning_position:
            elapsed_time = time.time() - level_start_time

            # Hiển thị cửa sổ chiến thắng
            continue_game, total_score = show_victory_window(
                screen, clock, current_level_index + 1, elapsed_time, total_score
            )

            if not continue_game:
                running = False
                continue

            current_level_index += 1
            if current_level_index < len(maps_collection):
                map_length, stair_position, map_data, player_start, zombie_starts = (
                    load_level(current_level_index)
                )
                winning_position = get_winning_position(stair_position, map_length)
                current_tile_size = 480 // map_length
                MummyMazeMap = MummyMazeMapManager(
                    length=map_length,
                    stair_position=stair_position,
                    map_data=map_data,
                    tile_size=current_tile_size,
                )
                MummyExplorer = MummyMazePlayerManager(
                    length=map_length,
                    grid_position=player_start,
                    map_data=map_data,
                    tile_size=current_tile_size,
                )
                MummyZombies = [
                    MummyMazeZombieManager(
                        length=map_length,
                        grid_position=pos,
                        map_data=map_data,
                        tile_size=current_tile_size,
                    )
                    for pos in zombie_starts
                ]
                level_start_time = time.time()  # Reset thời gian

                # Clear màn hình về màu đen trước khi vẽ map mới
                screen.fill((0, 0, 0))
            else:
                print("Congratulations! You have completed all levels!")
                running = False
            continue

        MummyMazeMap.draw_map(screen)

        player_turn_completed = MummyExplorer.update_player(screen)

        for zombie in MummyZombies:
            if player_turn_completed:
                zombie.zombie_movement(MummyExplorer.grid_position)
            zombie.update_zombie(screen)
        MummyMazeMap.draw_walls(screen)

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.04)

    pygame.quit()


if __name__ == "__main__":
    main()
