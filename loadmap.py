import pygame
import os




pygame.init()

screen_width = 1000
screen_height = 600
TILE_SIZE = 70 # Size of each tile in the grid
backdrop_width = 575 # Set width  size for the backdrop
backdrop_height = 558 # Set height size for the backdrop

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Load Map Example")
clock = pygame.time.Clock() # For controlling frame rate


# Load background and game square images
backdrop = pygame.image.load(os.path.join("assets","image", "backdrop.jpg")).convert()

 

backdrop = pygame.transform.scale(backdrop, (backdrop_width, backdrop_height))
game_square = pygame.image.load(os.path.join("assets","image", "floor6.jpg")).convert_alpha()
game_square = pygame.transform.scale(game_square, (TILE_SIZE*6, TILE_SIZE*6)) 

class Mum_Map:  
    
    def __init__(self):
        self.database = {
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
        
        self.map_data = [['', '', '', '', '', ''],
                         ['r ', '', 'tl', '', '', ''],
                         ['', '', '', '', '', ''],
                         ['', '', '', '', '', ''],
                         ['', '', '', '', '', ''],
                         ['', '', '', '', '', '']]
        
        self.load_image()

        self.margin_left = 78 + (screen_width-backdrop_width)//2 # distance from left edge to game square left edge
        self.margin_top = 93 + (screen_height-backdrop_height)//2 # distance from top edge to game square top edge
    def load_image_(self, id):
        img_path = os.path.join("assets","image", self.database[id])
        img = pygame.image.load(img_path).convert_alpha()
        return img
    
    def load_image(self):
        #seperate wall image to cut from walls6.png 
        area_surface = pygame.image.load(os.path.join("assets","image", 'walls6.png')).convert_alpha()

        area_to_cut = pygame.Rect(0, 0, 12,78)
        self.down_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (14,91))

        area_to_cut = pygame.Rect(12, 0, 72,18)
        self.lying_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (86,21))

        area_to_cut = pygame.Rect(84, 0, 12,74)
        self.up_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (14,87)) ### bottom col wall = 14x91, rol wall = 86x21, top col wall = 14x87

        return 0


    def draw_map(self, screen, map_data):
        for row_index, row in enumerate(map_data):
            for col_index, tile_id in enumerate(row):
                if tile_id.strip():  # Only draw if tile_id is not empty
                    img = self.load_image(tile_id)
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    screen.blit(img, (x, y))
        

my_map = Mum_Map()


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # draw game background and square at center
    screen.blit(backdrop, ((screen_width-backdrop_width)//2, (screen_height-backdrop_height)//2))
    screen.blit(game_square, ( my_map.margin_left, my_map.margin_top)) 
      
      
    screen.blit(my_map.up_standing_wall, (my_map.margin_left + TILE_SIZE*4 - 4, my_map.margin_top + TILE_SIZE*4 -87))
    screen.blit(my_map.lying_wall, (my_map.margin_left + TILE_SIZE*4 - 4, my_map.margin_top + TILE_SIZE*4 - 16))
    # screen.blit(my_map.down_standing_wall, (my_map.margin_left + TILE_SIZE*4 - 3, my_map.margin_top + TILE_SIZE*4 - 16))
    screen.blit(my_map.down_standing_wall, (my_map.margin_left + TILE_SIZE*5 -2, my_map.margin_top + TILE_SIZE*4 - 16))


    x, y = pygame.mouse.get_pos()
    print(x,y)
    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

