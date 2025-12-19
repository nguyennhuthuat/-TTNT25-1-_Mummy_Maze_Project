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
from Assets.module.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UP, DOWN, LEFT, RIGHT
)

import Assets.module.game_algorithms as algorithms
def main():


    pygame.init()
    pygame.mixer.init() # Initialize the mixer module for sound
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Mummy Maze Deluxe")
    clock = pygame.time.Clock()

    current_level_index = 0
    map_length, stair_position, map_data, player_start, zombie_starts = load_level(current_level_index)
    winning_position = get_winning_position(stair_position, map_length)
    
    current_tile_size = 480 // map_length  # Dynamically set tile size based on map length
    MummyMazeMap = MummyMazeMapManager(length = map_length, stair_position = stair_position, map_data = map_data, tile_size = current_tile_size)
    MummyExplorer = MummyMazePlayerManager(length = map_length, grid_position = player_start, map_data = map_data, tile_size=current_tile_size)
    MummyZombies = [MummyMazeZombieManager(length = map_length, grid_position = pos, map_data = map_data, tile_size=current_tile_size) for pos in zombie_starts]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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

            
        MummyMazeMap.draw_map(screen)

        player_turn_completed = MummyExplorer.update_player(screen)

        for zombie in MummyZombies:
            if player_turn_completed:
                zombie.zombie_movement(MummyExplorer.grid_position)
            zombie.update_zombie(screen)
        MummyMazeMap.draw_walls(screen)


        # Check for win condition
        if winning_position and MummyExplorer.grid_position == winning_position:
            print("You Won! Loading next level...")
            current_level_index += 1
            if current_level_index < len(maps_collection):
                map_length, stair_position, map_data, player_start, zombie_starts = load_level(current_level_index)
                winning_position = get_winning_position(stair_position, map_length)

                current_tile_size = 480 // map_length  # Dynamically set tile size based on map length
                MummyMazeMap = MummyMazeMapManager(length = map_length, stair_position = stair_position, map_data = map_data, tile_size = current_tile_size)
                MummyExplorer = MummyMazePlayerManager(length = map_length, grid_position = player_start, map_data = map_data, tile_size=current_tile_size)
                MummyZombies = [MummyMazeZombieManager(length = map_length, grid_position = pos, map_data = map_data, tile_size=current_tile_size) for pos in zombie_starts]
            else:
                print("Congratulations! You have completed all levels!")
                running = False

        pygame.display.flip()
        clock.tick(60)
        time.sleep(0.04)

    pygame.quit()


if __name__ == "__main__":
    main()