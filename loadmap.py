import pygame
import os
import time

RIGHT = "RIGHT"
LEFT = "LEFT"
UP = "UP"    
DOWN = "DOWN"
IDLE_status = "IDLE" 
UP_status = "UP"
DOWN_status = "DOWN"  
LEFT_status = "LEFT"
RIGHT_status = "RIGHT"
map_data = [['l', 'r', 't', 'b', 'bl', 'br'],
            ['tr', 'tl', 't*', 'b*', 'r*', 'l*'],
            ['', 'r', '   bl   ', '', '', 't'],
            ['', '', '', '', '   ', ''],
            ['', 'l', '', 'tl', 't*', ''],
            ['', '     ', '', '', 'r', '']]


pygame.init()
screen_width = 1000
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Load Map Example")
clock = pygame.time.Clock() # For controlling frame rate

def clean_map_data(map_data):
    for col_index, col in enumerate(map_data): #dr aw walls based on map_data
            for row_index, tile_id in enumerate(col):
                map_data[col_index][row_index] = map_data[col_index][row_index].strip()
    print(map_data)
    return map_data
map_data = clean_map_data(map_data)
                
class MummyMazeMapManager:  
    
    def __init__(self, length,map_data):

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
        
        self.map_data = map_data
        
        self.stair_positions = (7, 5) # (row, column) position of the stair tile in the map_data
        
        # Load background and game square images
        self.backdrop = pygame.image.load(os.path.join("assets","image", "backdrop.png")).convert()
        self.backdrop = pygame.transform.scale(self.backdrop, (backdrop_width, backdrop_height))
        self.game_square = pygame.image.load(os.path.join("assets","image", "floor" + str(self.length) + ".png")).convert_alpha()
        self.game_square = pygame.transform.scale(self.game_square, (TILE_SIZE*6, TILE_SIZE*6)) 


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
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))  
    def draw_bottom_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y + TILE_SIZE - 14))
    def draw_left_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
    def draw_right_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x + TILE_SIZE - 3, margin_top + TILE_SIZE*y - 14))
    def draw_bottom_left_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y + TILE_SIZE - 14))
    def draw_top_left_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
    def draw_bottom_right_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (margin_left + TILE_SIZE*x + TILE_SIZE - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y + TILE_SIZE - 14))
    def draw_top_right_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x + TILE_SIZE - 3, margin_top + TILE_SIZE*y - 14))
    def draw_left_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.up_standing_wall, (margin_left + TILE_SIZE*x + TILE_SIZE - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y + TILE_SIZE - 14))
    def draw_right_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y + TILE_SIZE - 14))
    def draw_top_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.up_standing_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.up_standing_wall, (margin_left + TILE_SIZE*x + TILE_SIZE - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y + TILE_SIZE - 14))
    def draw_bottom_t_wall_tile(self, screen, x, y): # x,y: the cell at row x, column y in a square table/board
        x -= 1
        y -= 1
        screen.blit(self.lying_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x - 3, margin_top + TILE_SIZE*y - 14))
        screen.blit(self.down_standing_wall, (margin_left + TILE_SIZE*x + TILE_SIZE - 3, margin_top + TILE_SIZE*y - 14))    

    def draw_stair(self, screen):
        def draw_bottom_stair(self, screen, row, col):
            x = margin_left + TILE_SIZE*(row - 1) 
            y = margin_top + TILE_SIZE*(col - 1) - 2
            screen.blit(self.bottom_stair, (x, y))

        def draw_top_stair(self, screen, row, col):
            x = margin_left + TILE_SIZE*(row - 1) - self.top_stair.get_width() - 3
            y = margin_top + TILE_SIZE*(col - 1) - self.top_stair.get_height()  + TILE_SIZE
            screen.blit(self.top_stair, (x, y))

        def draw_left_stair(self, screen, row, col):
            x = margin_left + TILE_SIZE*(row - 1) 
            y = margin_top + TILE_SIZE*(col - 1) - 5
            screen.blit(self.left_stair, (x, y))

        def draw_right_stair(self, screen, row, col):
            x = margin_left + TILE_SIZE*(row - 1) 
            y = margin_top + TILE_SIZE*(col - 1) - 5
            screen.blit(self.right_stair, (x, y))
        
        
        row, col = self.stair_positions

      #   DRAW STAIRCheck position and draw corresponding stair
        if col == len(self.map_data[0]) + 1:
            draw_bottom_stair(self, screen, row, col)
        elif col == 0:
            draw_top_stair(self, screen, row, col)
        elif row == 0:
            draw_left_stair(self, screen, row, col)
        elif row == len(self.map_data[0]) + 1:
            draw_right_stair(self, screen, row, col)
    

    def draw_map(self, screen):
        screen.blit(self.backdrop, ((screen_width-backdrop_width)//2, (screen_height-backdrop_height)//2))
        screen.blit(self.game_square, ( margin_left, margin_top)) 

        #draw stair
        self.draw_stair(screen)

    def draw_walls(self, screen):
        for col_index, col in enumerate(self.map_data): #dr aw walls based on map_data
            for row_index, tile_id in enumerate(col):
                if tile_id.strip() and (tile_id in self.database.keys()):  # Only draw if tile_id is not empty
                    getattr(self, self.database[tile_id])(screen, row_index + 1, col_index + 1) # Call the drawing function based on tile_id
                    #getattr(object, name[, default]) -> value
                elif tile_id.strip() and tile_id not in self.database.keys():
                    print(f"Warning: tile_id '{tile_id}' at ({col_index}, {row_index}) not found in database. Skipping drawing.")
                    continue

class MummyMazePlayerManager:
    class MummyMazeFramesManager:
        def __init__(self,UP, DOWN, LEFT, RIGHT):
            self.UP = UP
            self.DOWN = DOWN
            self.LEFT = LEFT
            self.RIGHT = RIGHT

    def __init__(self, length, grid_position :list, map_data):
        self.length = length
        self.player_frames = self.load_player_images()
        self.map_data = map_data

        self.grid_position = grid_position  # [row, column] position of the player in the grid
        
        self.movement_list = []  # List to store movement directions
        self.movement_frame_index = 0  # Index to track the current frame in the movement animation ( 0 -> 9)
        self.facing_direction = DOWN  # Initial facing direction
        self.total_frames = 10  # Total frames per movement direction
        self.current_frame = getattr(self.player_frames,self.facing_direction)[self.total_frames - 1]  # Start with the first frame facing down
        self.Speed = 70

    def get_player_position(self,grid_position): ###!!!!!!!!
        return [(margin_left + TILE_SIZE*(grid_position[0] - 1) + 4), (margin_top + TILE_SIZE*(grid_position[1]-1) + 4)]
    
    def load_player_images(self):
        def double_list(input_list):
            return [item for item in input_list for _ in range(2)]
        def extract_sprite_frames(sheet, frame_width, frame_height):
            sheet_width, sheet_height = sheet.get_size()
            frames = []
            for y in range(0, sheet_height, frame_height):
                for x in range(0, sheet_width, frame_width):
                    frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                    frames.append(frame)
            return frames
        player_surface = pygame.image.load(os.path.join("assets","image", "explorer" + str(self.length) + ".png")).convert_alpha()
        player_surface = pygame.transform.scale(player_surface, (player_surface.get_width()*7//6, player_surface.get_height()*7//6))
        
        # sperate player sprite sheet into frames, each movement direction has 5 frames, total 20 frames
        # visit assets/image/mummy_white6.png to see the sprite sheet
        player_frame = extract_sprite_frames(player_surface, player_surface.get_width()//5, player_surface.get_height()//4) 
        player_go_up_frames = player_frame[1:5]
        player_go_up_frames.append(player_frame[0])
        # self.player_go_up_frames.append(self.player_go_up_frames[0])
        player_go_right_frames = player_frame[6:10]
        player_go_right_frames.append(player_frame[5])
        # self.player_go_right_frames.append(self.player_go_right_frames[0])
        player_go_down_frames = player_frame[11:15]
        player_go_down_frames.append(player_frame[10])
        # self.player_go_down_frames.append(self.player_go_down_frames[0])
        player_go_left_frames = player_frame[16:20]
        player_go_left_frames.append(player_frame[15])
        # self.player_go_left_frames.append(self.player_go_left_frames[0])
        return self.MummyMazeFramesManager(double_list(player_go_up_frames), double_list(player_go_down_frames), double_list(player_go_left_frames), double_list(player_go_right_frames))

    def player_can_move(self, direction, facing_direction): #check if have walls on the way
        
        x = direction[0]
        y = direction[1]
        if facing_direction == UP:
            return (y-1 > 0) and (self.map_data[y-1][x-1] not in ['t', 'tl','tr','b*','l*','r*']) and (self.map_data[y-2][x-1] not in ['b','bl','br','t*','l*','r*'])
        if facing_direction == DOWN:
            return (y+1 <= len(self.map_data[0])) and (self.map_data[y-1][x-1] not in ['b','bl','br','t*','l*','r*']) and (self.map_data[y][x-1] not in ['t', 'tl','tr','b*','l*','r*'])
        if facing_direction == LEFT:
            print(self.map_data[y-1][x-1], self.map_data[y-1][x-2])
            return (x-1 > 0) and (self.map_data[y-1][x-1] not in ['l', 'tl','bl','b*','t*','r*']) and (self.map_data[y-1][x-2] not in ['r','br','tr','t*','l*','b*'])
        if facing_direction == RIGHT:
            return (x+1 <= len(self.map_data[0])) and (self.map_data[y-1][x-1] not in ['r','br','tr','t*','l*','b*']) and (self.map_data[y-1][x] not in ['l', 'tl','bl','b*','t*','r*'])
        return True
    
    def update_player(self, screen):
        move_distance_x = 0 # sai so khoang cach tinh theo pixel
        move_distance_y = 0
        grid_x = 0  #sai so khoang cach tinh theo o vuon don vi
        grid_y = 0

        if self.movement_list:
            self.facing_direction = self.movement_list[0] # Get the current movement direction
            self.current_frame = getattr(self.player_frames, str(self.facing_direction))[self.movement_frame_index]

            if self.player_can_move(self.grid_position, self.facing_direction):
                if self.facing_direction == UP:
                    move_distance_x = 0
                    move_distance_y = - (self.movement_frame_index + 1) * (self.Speed//self.total_frames)   
                    print(self.movement_frame_index)     
                    grid_x = 0
                    grid_y = -1            
                elif self.facing_direction == DOWN:
                    move_distance_x = 0
                    move_distance_y = (self.movement_frame_index + 1) * (self.Speed//self.total_frames) 
                    grid_x = 0
                    grid_y = 1
                elif self.facing_direction == LEFT:
                    move_distance_x = - (self.movement_frame_index + 1) * (self.Speed//self.total_frames) 
                    move_distance_y = 0
                    grid_x = -1
                    grid_y = 0
                elif self.facing_direction == RIGHT:
                    move_distance_x = (self.movement_frame_index + 1) * (self.Speed//self.total_frames) 
                    move_distance_y = 0
                    grid_x = 1
                    grid_y = 0            

            screen.blit(self.current_frame, (margin_left + 4 + TILE_SIZE*(self.grid_position[0] - 1) + move_distance_x, margin_top + 4 + TILE_SIZE*(self.grid_position[1] - 1) + move_distance_y))

            self.movement_frame_index += 1
            if self.movement_frame_index >= self.total_frames:
                self.movement_frame_index = 0
                self.movement_list.pop(0)  # Remove the completed movement
                self.grid_position[0] += grid_x
                self.grid_position[1] += grid_y
        else:
            screen.blit(self.current_frame, (margin_left + 4 + TILE_SIZE*(self.grid_position[0] - 1) + move_distance_x, margin_top + 4 + TILE_SIZE*(self.grid_position[1] - 1) + move_distance_y))
        print(f'position of explorer: {self.grid_position}')

        


    
TILE_SIZE = 70 # Size of each tile in the grid
backdrop_width = 575 # Set width  size for the backdrop
backdrop_height = 558 # Set height size for the backdrop
margin_left = 78 + (screen_width - backdrop_width)//2 # distance from left edge to game square left edge
margin_top = 93 + (screen_height - backdrop_height)//2 # distance from top edge to game square top edge
    
MummyMazeMap = MummyMazeMapManager(6, map_data)
MummyExplorer = MummyMazePlayerManager(6, [6,6], map_data)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if MummyExplorer.movement_list == []:
                        MummyExplorer.movement_list.append(UP)                    
                        MummyExplorer.facing_direction = UP
                elif event.key == pygame.K_DOWN:
                    if MummyExplorer.movement_list == []:
                        MummyExplorer.movement_list.append(DOWN)
                        MummyExplorer.facing_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    if MummyExplorer.movement_list == []:
                        MummyExplorer.movement_list.append(LEFT)
                        MummyExplorer.facing_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    if MummyExplorer.movement_list == []:
                        MummyExplorer.movement_list.append(RIGHT)
                        MummyExplorer.facing_direction = RIGHT

    MummyMazeMap.draw_map(screen)  
    MummyExplorer.update_player(screen)
    MummyMazeMap.draw_walls(screen)


    # x, y = pygame.mouse.get_pos()
    # print(x,y)
    

    pygame.display.flip()
    clock.tick(60)
    time.sleep(0.03)

pygame.quit()

