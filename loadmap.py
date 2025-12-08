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
from Assets.module.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UP, DOWN, LEFT, RIGHT
)
def main():


    pygame.init()
    pygame.mixer.init() # Initialize the mixer module for sound
    
    expwalk_sound = pygame.mixer.Sound(os.path.join("Assets", "sounds", "expwalk60b.wav"))
    mumwalk_sound = pygame.mixer.Sound(os.path.join("Assets", "sounds", "mumwalk60b.wav"))

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Load Map Example")
    clock = pygame.time.Clock()

    current_level_index = 7
    map_length, stair_position, map_data, player_start, zombie_starts = load_level(current_level_index)
    winning_position = get_winning_position(stair_position, map_length)

    MummyMazeMap = MummyMazeMapManager(map_length, stair_position, map_data)
    MummyExplorer = MummyMazePlayerManager(map_length, player_start, map_data)
    MummyZombies = [MummyMazeZombieManager(map_length, pos, map_data) for pos in zombie_starts]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if MummyZombies[0].is_standing:  # Only allow player input if zombies are standing
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if not MummyExplorer.movement_list:
                            MummyExplorer.update_player_status(UP)
                            expwalk_sound.play()
                    elif event.key == pygame.K_DOWN:
                        if not MummyExplorer.movement_list:
                            MummyExplorer.update_player_status(DOWN)
                            expwalk_sound.play()

                    elif event.key == pygame.K_LEFT:
                        if not MummyExplorer.movement_list:
                            MummyExplorer.update_player_status(LEFT)
                            expwalk_sound.play()

                    elif event.key == pygame.K_RIGHT:
                        if not MummyExplorer.movement_list:
                            MummyExplorer.update_player_status(RIGHT)
                            expwalk_sound.play()

        MummyMazeMap.draw_map(screen)

        player_turn_completed = MummyExplorer.update_player(screen)

        for zombie in MummyZombies:
            zombie.update_zombie(screen)
        MummyMazeMap.draw_walls(screen)

        if player_turn_completed:
            for zombie in MummyZombies:
                zombie.zombie_movement(MummyExplorer.grid_position)
                if zombie.movement_list and zombie.movement_frame_index == 0:
                    mumwalk_sound.play()

        # Check for win condition
        if winning_position and MummyExplorer.grid_position == winning_position:
            print("You Won! Loading next level...")
            current_level_index += 1
            if current_level_index < len(maps_collection):
                map_length, stair_position, map_data, player_start, zombie_starts = load_level(current_level_index)
                winning_position = get_winning_position(stair_position, map_length)

                MummyMazeMap = MummyMazeMapManager(map_length, stair_position, map_data)
                MummyExplorer = MummyMazePlayerManager(map_length, player_start, map_data)
                MummyZombies = [MummyMazeZombieManager(map_length, pos, map_data) for pos in zombie_starts]
            else:
                print("Congratulations! You have completed all levels!")
                running = False

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.04)

    pygame.quit()


if __name__ == "__main__":
    main()