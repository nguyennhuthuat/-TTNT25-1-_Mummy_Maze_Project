import pygame
import os

pygame.init()
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Load Map Example")
clock = pygame.time.Clock() # For controlling frame rate

class Mum_Map:  
    
    def __init__(self, length):

        self.length = length
        self.database = { # dictionary to link tile id to drawing function
            't': 'draw_top_wall_tile',
            'b': 'draw_bottom_wall_tile',
            'l': 'draw_left_wall_tile',
            'r': 'draw_right_wall_tile',
            'tr': 'draw_top_right_wall_tile',
            'tl': 'draw_top_left_wall_tile',
            'br': 'draw_bottom_right_wall_tile',
            'bl': 'draw_bottom_left_wall_tile',
            'l*': 'draw_left_t_wall_tile',
            'r*': 'draw_right_t_wall_tile',
            't*': 'draw_top_t_wall_tile',
            'b*': 'draw_bottom_t_wall_tile'}
        
        self.map_data = [['', '', '', '', 'bl', ''],
                         ['r', '', 'tl', '', '', ''],
                         ['', 'r', 'bl', '', '', 't'],
                         ['', '', '', '', '', ''],
                         ['', 'l', '', 'tl', 't*', ''],
                         ['', '', '', '', 'r', '']]
        
        self.stair_positions = (7, 5) # (row, column) position of the stair tile in the map_data
        
        self.TILE_SIZE = 70 # Size of each tile in the grid
        self.backdrop_width = 575 # Set width  size for the backdrop
        self.backdrop_height = 558 # Set height size for the backdrop
        self.margin_left = 78 + (screen_width-self.backdrop_width)//2 # distance from left edge to game square left edge
        self.margin_top = 93 + (screen_height-self.backdrop_height)//2 # distance from top edge to game square top edge
        # Load background and game square images
        self.backdrop = pygame.image.load(os.path.join("assets","image", "backdrop.png")).convert()
        self.backdrop = pygame.transform.scale(self.backdrop, (self.backdrop_width, self.backdrop_height))
        self.game_square = pygame.image.load(os.path.join("assets","image", "floor" + str(self.length) + ".png")).convert_alpha()
        self.game_square = pygame.transform.scale(self.game_square, (self.TILE_SIZE*6, self.TILE_SIZE*6)) 


        self.load_tiles()
       
    
    def load_tiles(self):
        #seperate wall image to cut from walls6.png 
        area_surface = pygame.image.load(os.path.join("assets","image", "walls" + str(self.length) + ".png")).convert_alpha()

        area_to_cut = pygame.Rect(0, 0, 12,78)
        self.down_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (14,91))

        area_to_cut = pygame.Rect(12, 0, 72,18)
        self.lying_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (84,21))

        area_to_cut = pygame.Rect(84, 0, 12,74)
        self.up_standing_wall = pygame.transform.scale(area_surface.subsurface(area_to_cut), (14,87)) ### bottom col wall = 14x91, rol wall = 84x21, top col wall = 14x87
        
        #seperate stair image to cut from stairs.png
        area_stair_surface = pygame.image.load(os.path.join("assets","image", "stairs" + str(self.length) + ".png")).convert_alpha()
        
        area_to_cut = pygame.Rect(2, 0, 54, 66)
        self.top_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (63,77))

        area_to_cut = pygame.Rect(60, 0, 54, 66)
        self.right_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (63,77))

        area_to_cut = pygame.Rect(114, 0, 54, 34)
        self.bottom_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (63,36))

        area_to_cut = pygame.Rect(170, 0, 54, 66)
        self.left_stair = pygame.transform.scale(area_stair_surface.subsurface(area_to_cut), (63,77)) 
        #bottom, left, right : 54x66 scaled to 63x77; top: 54x36 scaled to 63x42
        return 0
    
    def draw_top_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))  
    def draw_bottom_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y + self.TILE_SIZE - 14))
    def draw_left_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
    def draw_right_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x + self.TILE_SIZE - 3, self.margin_top + self.TILE_SIZE*y - 14))
    def draw_bottom_left_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y + self.TILE_SIZE - 14))
    def draw_top_left_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
    def draw_bottom_right_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (self.margin_left + self.TILE_SIZE*x + self.TILE_SIZE - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y + self.TILE_SIZE - 14))
    def draw_top_right_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x + self.TILE_SIZE - 3, self.margin_top + self.TILE_SIZE*y - 14))
    def draw_left_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.up_standing_wall, (self.margin_left + self.TILE_SIZE*x + self.TILE_SIZE - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y + self.TILE_SIZE - 14))
    def draw_right_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y + self.TILE_SIZE - 14))
    def draw_top_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.up_standing_wall, (self.margin_left + self.TILE_SIZE*x + self.TILE_SIZE - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y + self.TILE_SIZE - 14))
    def draw_bottom_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x - 3, self.margin_top + self.TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (self.margin_left + self.TILE_SIZE*x + self.TILE_SIZE - 3, self.margin_top + self.TILE_SIZE*y - 14))    

    def draw_stair(self, screen):
        def draw_bottom_stair(self, screen, row, col):
            x = self.margin_left + self.TILE_SIZE*(row - 1) 
            y = self.margin_top + self.TILE_SIZE*(col - 1) - 2
            screen.blit(self.bottom_stair, (x, y))

        def draw_top_stair(self, screen, row, col):
            x = self.margin_left + self.TILE_SIZE*(row - 1) - self.top_stair.get_width() - 3
            y = self.margin_top + self.TILE_SIZE*(col - 1) - self.top_stair.get_height()  + self.TILE_SIZE
            screen.blit(self.top_stair, (x, y))

        def draw_left_stair(self, screen, row, col):
            x = self.margin_left + self.TILE_SIZE*(row - 1) 
            y = self.margin_top + self.TILE_SIZE*(col - 1) - 5
            screen.blit(self.left_stair, (x, y))

        def draw_right_stair(self, screen, row, col):
            x = self.margin_left + self.TILE_SIZE*(row - 1) 
            y = self.margin_top + self.TILE_SIZE*(col - 1) - 5
            screen.blit(self.right_stair, (x, y))
        
        
        row, col = self.stair_positions
      #check position and draw corresponding stair
        if col == len(self.map_data[0]) + 1:
            draw_bottom_stair(self, screen, row, col)
        elif col == 0:
            draw_top_stair(self, screen, row, col)
            print("vẽ thang trên")
        elif row == 0:
            draw_left_stair(self, screen, row, col)
        elif row == len(self.map_data[0]) + 1:
            draw_right_stair(self, screen, row, col)
        else: print(len(self.map_data[0]))
    

    def draw_map(self, screen):
        screen.blit(self.backdrop, ((screen_width-self.backdrop_width)//2, (screen_height-self.backdrop_height)//2))
        screen.blit(self.game_square, ( self.margin_left, self.margin_top)) 
        for row_index, row in enumerate(self.map_data): #draw walls based on map_data
            for col_index, tile_id in enumerate(row):
                if tile_id.strip() and (tile_id in self.database.keys()):  # Only draw if tile_id is not empty
                    getattr(self, self.database[tile_id])(screen, col_index + 1, row_index + 1) # Call the drawing function based on tile_id
                elif tile_id.strip() and tile_id not in self.database.keys():
                    print(f"Warning: tile_id '{tile_id}' at ({row_index}, {col_index}) not found in database. Skipping drawing.")
                    continue

        #draw stair
        self.draw_stair(screen)

class player:
    def __init__(self):
        pass
    def load_player(self):
        pass 
my_map = Mum_Map(6)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    my_map.draw_map(screen)  

    x, y = pygame.mouse.get_pos()
    print(x,y)
    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

