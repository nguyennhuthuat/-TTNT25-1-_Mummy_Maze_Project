import pygame
import os


# ['  ', ' ', ' ', ' ', ' ', ' ']
# ['r ', ' ', 'tl', ' ', ' ', ' ']
# [' ', ' ', ' ', ' ', ' ', ' ']
# [' ', ' ', ' ', ' ', ' ', ' ']
# [' ', ' ', ' ', ' ', ' ', ' ']
# [' ', ' ', ' ', ' ', ' ', ' ']

pygame.init()

screen_width = 1000
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Load Map Example")
clock = pygame.time.Clock() # For controlling frame rate

TILE_SIZE = 70 # Size of each tile in the grid

# Load background and game square images
backdrop = pygame.image.load(os.path.join("assets","nomnom", "backdrop.jpg")).convert()

backdrop_width = 575 # Set width  size for the backdrop
backdrop_height = 558 

backdrop = pygame.transform.scale(backdrop, (backdrop_width, backdrop_height))
game_square = pygame.image.load(os.path.join("assets","nomnom", "floor6.jpg")).convert_alpha()
game_square = pygame.transform.scale(game_square, (TILE_SIZE*6, TILE_SIZE*6)) 

tile_dict = {
    't': 'top_wall_tile.jpg',
    'b': 'bottom_wall_tile.jpg',
    'l': 'left_wall_tile.jpg',
    'r': 'right_wall_tile.jpg',
    'tr': 'top_right_wall_tile.jpg',
    'tl': 'top_left_wall_tile.jpg',
    'br': 'bottom_right_wall_tile.jpg',
    'bl': 'bottom_left_wall_tile.jpg',
    'l*': 'left_t_wall_tile.jpg',
    'r*': 'right_t_wall_tile.jpg',
    't*': 'top_t_wall_tile.jpg',
    'b*': 'bottom_t_wall_tile.jpg'}
# top_wall_tile = pygame.image.load(os.path.join("assets","nomnom", tile_dict['t'])).convert_alpha()




running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # draw game background and square at center
    screen.blit(backdrop, ((screen_width-backdrop_width)//2, (screen_height-backdrop_height)//2))
    screen.blit(game_square, ((screen_width-backdrop_width)//2 + 78,(screen_height-backdrop_height)//2 + 93)) 
    ## 78 is distance from left edge to game square left edge, 93 is distance from top edge to game square top edge


    pygame.display.flip()
    clock.tick(60)

pygame.quit()

