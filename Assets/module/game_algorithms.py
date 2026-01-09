from collections import deque

from click import Tuple
from .utils import is_linked
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'


def is_trap(superdata: list, position: tuple) -> bool:
    """
    Check if a position contains a trap. 
    """
    x, y = position[0], position[1]
    map_data = superdata["map_data"]
    # Check boundaries
    if x < 1 or y < 1 or y > len(map_data) or x > len(map_data[0]):
        return False
    
    # Check if cell is a trap (adjust 'X' based on your map notation)
    return [x,y] in superdata["trap_pos"]

def is_lose(superdata: list, player_position: tuple, zombie_positions: list = [], scorpion_positions: list = []) -> bool:
    """
    Check if player is caught by zombie or scorpion. 
    """
    # Check traps
    if is_trap(superdata, player_position):
        return True
    
    # Check zombies
    if zombie_positions:
        for zombie_info in zombie_positions:
            if player_position == (zombie_info[0], zombie_info[1]):
                return True
    
    # Check scorpions
    if scorpion_positions:
        for scorpion_info in scorpion_positions: 
            if player_position == (scorpion_info[0], scorpion_info[1]):
                return True
    
    return False

def generate_graph(superdata: list, gate_opened: bool = False) -> dict:
    """
    Generate graph from map data to use in pathfinding algorithms.
    Graph edges respect gate states. 
    
    Args:
        superdata: Dictionary containing map_data, gate_pos, key_pos, trap_pos
        gate_opened:  Current state of gate
    
    Returns:
        dict: Graph representation {position: [neighbors]}
    """
    graph = {}
    map_data = superdata["map_data"]

    for col_index, col in enumerate(map_data):
        for row_index, value in enumerate(col):
            position = (row_index + 1, col_index + 1)
            
            # Pass if position is trap
            if is_trap(superdata, position):
                graph[position] = []
                continue

            graph[position] = []
            
            # Check UP
            if is_linked(map_data, position, UP, gate_opened, superdata) and \
               not is_trap(superdata, (position[0], position[1] - 1)):
                graph[position].append((row_index + 1, col_index))
            
            # Check DOWN
            if is_linked(map_data, position, DOWN, gate_opened, superdata) and \
               not is_trap(superdata, (position[0], position[1] + 1)):
                graph[position].append((row_index + 1, col_index + 2))
            
            # Check LEFT
            if is_linked(map_data, position, LEFT, gate_opened, superdata) and \
               not is_trap(superdata, (position[0] - 1, position[1])):
                graph[position].append((row_index, col_index + 1))
            
            # Check RIGHT
            if is_linked(map_data, position, RIGHT, gate_opened, superdata) and \
               not is_trap(superdata, (position[0] + 1, position[1])):
                graph[position].append((row_index + 2, col_index + 1))

    return graph


def BFS(graph: dict, start: tuple) -> set:
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        vertex = queue.popleft()
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited

def DFS(graph: dict, start: tuple) -> set:
    visited = set()
    stack = [start]
    visited.add(start)
    while stack:
        vertex = stack.pop()

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return visited

def try_move(game_map: list, current_pos: tuple, direction: int, delta_x: int, delta_y: int) -> tuple:
    """
    Attempts to move in a specific direction.
    Returns the new coordinate if linked, otherwise returns the current coordinate.
    """
    if is_linked(game_map, current_pos, direction):
        return (current_pos[0] + delta_x, current_pos[1] + delta_y)
    return current_pos

def get_horizontal_direction(zombie_x: int, player_x: int) -> tuple:
    """
    Determines the horizontal direction towards the player.
    Returns: (direction_constant, delta_x, delta_y)
    """
    if zombie_x > player_x: 
        return LEFT, -1, 0  # Move Left
    if zombie_x < player_x: 
        return RIGHT, 1, 0  # Move Right
    
    return None, 0, 0       # Same column

def get_vertical_direction(zombie_y: int, player_y: int) -> tuple:
    """
    Determines the vertical direction towards the player.
    Returns: (direction_constant, delta_x, delta_y)
    """
    if zombie_y > player_y: 
        return UP, 0, -1    # Move Up
    if zombie_y < player_y: 
        return DOWN, 0, 1   # Move Down
    
    return None, 0, 0       # Same row

def generate_next_zombie_positions(map_data: list = [], current_zombie_positions: list = [], current_player_position: tuple = (), show_list: bool = False) -> list:


    def generate_type_0(map_data: list = [], current_zombie_position: tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 0 Zombie (Tank/Dumb Zombie).
        - Speed: 2 steps.
        - Behavior: Prioritizes Vertical movement.
        - Feature: Freezes if blocked vertically (does not pathfind around walls).
        """
        
        # Use a local variable to track position updates through the steps
        zombie_pos = current_zombie_position
        move_list = []

        # Loop for the number of steps (Speed = 2)
        move_dir, dx, dy = get_vertical_direction(zombie_pos[1], current_player_position[1])
        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            # Stop moving immediately if the zombie has caught the player
            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Vertical Alignment Needed
            if z_y != p_y:
                # Determine vertical direction
                if z_y > p_y:
                    move_dir, dx, dy = UP, 0, -1
                else:
                    move_dir, dx, dy = DOWN, 0, 1
                
                # Attempt to move vertically
                new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                if new_pos != zombie_pos and move_dir is not None:
                    move_list.append(move_dir)

                # [FEATURE] Wall Stuck Logic:
                # If the zombie tried to move vertically but hit a wall (position didn't change),
                # it stops its turn immediately. It is not smart enough to try horizontal moves.
                if new_pos == zombie_pos:
                    break

            # CASE 2: Same Row (Horizontal Alignment)
            else:
                # Only move horizontally if already on the same row
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                    if new_pos != zombie_pos and move_dir is not None:
                        move_list.append(move_dir)

            # Update the position for the next iteration of the loop
            zombie_pos = new_pos

        if move_list == [] and move_dir is not None: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
            move_list.append(move_dir)

        if show_list == False:
            return zombie_pos
        else:
            return move_list
        
    def generate_type_1(map_data: list = [], current_zombie_position: tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 1 Zombie.
        - Speed: 2 steps.
        - Behavior: Prioritizes Horizontal movement (Left/Right) first.
        - Feature: Freezes if blocked horizontally (does not pathfind vertically).
        """
        
        zombie_pos = current_zombie_position
        move_list = []

        move_dir, dx, dy = get_horizontal_direction(zombie_pos[0], current_player_position[0])

        
        # Loop for 2 steps
        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            # Stop if caught player
            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Horizontal Alignment Needed (Priority)
            if z_x != p_x:
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                
                # Attempt to move horizontally
                new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                if new_pos != zombie_pos and move_dir is not None:
                    move_list.append(move_dir)
                    
                # [FEATURE] Wall Stuck Logic:
                # If blocked horizontally, stop turn immediately.
                if new_pos == zombie_pos:
                    break

            # CASE 2: Same Column (Vertical Alignment)
            else:
                # Only move vertically if already on the same column
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                    if new_pos != zombie_pos and move_dir is not None:
                        move_list.append(move_dir)

            # Update position for next iteration
            zombie_pos = new_pos

        if move_list == [] and move_dir is not None: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
            move_list.append(move_dir)

        if show_list == False:
            return zombie_pos
        else:
            return move_list
    
    def generate_type_2(map_data: list = [], current_zombie_position: tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 2 Zombie (Smart/Sliding Zombie).
        - Speed: 2 steps.
        - Behavior: Prioritizes Vertical movement.
        - Feature (Smart): If blocked Vertically, it attempts to 'slide' Horizontally 
        instead of freezing. It only freezes if BOTH Vertical and Horizontal paths are blocked.
        """
        
        zombie_pos = current_zombie_position
        move_list = []

        move_dir, dx, dy = get_vertical_direction(zombie_pos[1], current_player_position[1])

        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Vertical Alignment Needed (Priority)
            if z_y != p_y:
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                
                # 1.1 Try moving Vertical
                attempt_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)

                # Check if Vertical move succeeded
                if attempt_pos != zombie_pos:
                    new_pos = attempt_pos
                    if move_dir is not None:
                        move_list.append(move_dir)
                else:
                    # 1.2 [SMART FALLBACK] Blocked Vertically -> Try Horizontal immediately
                    # Instead of breaking, check if we can slide Left/Right
                    h_dir, h_dx, h_dy = get_horizontal_direction(z_x, p_x)
                    
                    if h_dir is not None:
                        new_pos = try_move(map_data, zombie_pos, h_dir, h_dx, h_dy)
                        if new_pos != zombie_pos and h_dir is not None:
                            move_list.append(h_dir)
                    
                    # Note: If new_pos is still equal to zombie_pos here, 
                    # it means both Vertical and Horizontal were blocked (or aligned).
                    # The zombie stands still (does not reverse/turn back).

            # CASE 2: Already on Same Row (Only Horizontal option)
            else:
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                    if new_pos != zombie_pos and move_dir is not None:
                        move_list.append(move_dir)

            # Update position
            zombie_pos = new_pos

        if move_list == [] and move_dir is not None: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
            move_list.append(move_dir)

        if show_list == False:
            return zombie_pos
        else:
            return move_list
    
    def generate_type_3(map_data: list = [], current_zombie_position: tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 3 Zombie (Smart Horizontal Zombie).
        - Speed: 2 steps.
        - Behavior: Prioritizes Horizontal movement (Left/Right).
        - Feature (Smart): If blocked Horizontally, it attempts to 'slide' Vertically.
        """
        
        zombie_pos = current_zombie_position
        move_list = []

        move_dir, dx, dy = get_horizontal_direction(zombie_pos[0], current_player_position[0])

        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            # Stop if caught player
            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Horizontal Alignment Needed (Priority)
            if z_x != p_x:
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                
                # 1.1 Try moving Horizontal
                attempt_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)

                if attempt_pos != zombie_pos:
                    new_pos = attempt_pos # Success
                    if move_dir is not None:
                        move_list.append(move_dir)

                else:
                    # 1.2 [SMART FALLBACK] Blocked Horizontally -> Try Vertical immediately
                    v_dir, v_dx, v_dy = get_vertical_direction(z_y, p_y)
                    
                    if v_dir is not None:
                        new_pos = try_move(map_data, zombie_pos, v_dir, v_dx, v_dy)
                        if new_pos != zombie_pos and v_dir is not None:
                            move_list.append(v_dir)

            # CASE 2: Already on Same Column (Only Vertical option)
            else:
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                    if new_pos != zombie_pos and move_dir is not None:
                        move_list.append(move_dir)

            # Update position for next iteration
            zombie_pos = new_pos

        if move_list == [] and move_dir is not None:#if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
            move_list.append(move_dir)

        if show_list == False:
            return zombie_pos
        else:
            return move_list


    #--------------------------------------------------------#
    #----- Main logic of GENERATE_NEXT_ZOMBIE_POSITIONS -----#
    #--------------------------------------------------------#
    '''
    Type of zombie: 
        0: zombie priotizes moving vertically (UP/DOWN)
        1: zombie priotizes moving horizontally (LEFT/RIGHT)
        2: zombie smarter, priotizes moving up/down first, then left/right
        3: zombie smarter, priotizes moving left/right first, then up/down

    show_list: bool (Apply for all small functions inside)
        If True: return list of movements
        If False: return next positions only
     '''
    
    next_zombie_pos = []

    move_list = [] #use for only one zombie

    for zombie_info in current_zombie_positions:
        current_zombie_position = (zombie_info[0], zombie_info[1])
        zombie_type = zombie_info[2]

        if zombie_type == 0:
            # Choose vertical move first
            next_zombie_pos.append(generate_type_0(map_data, current_zombie_position, current_player_position) + (zombie_type,))
            if show_list:
                move_list += generate_type_0(map_data, current_zombie_position, current_player_position, show_list=show_list)
        elif zombie_type == 1:
            # Choose horizontal move first
            next_zombie_pos.append(generate_type_1(map_data, current_zombie_position, current_player_position) + (zombie_type,))
            if show_list:
                move_list += generate_type_1(map_data, current_zombie_position, current_player_position, show_list=show_list)
        elif zombie_type == 2:
            # Smart vertical prioritization
            next_zombie_pos.append(generate_type_2(map_data, current_zombie_position, current_player_position) + (zombie_type,))
            if show_list:
                move_list += generate_type_2(map_data, current_zombie_position, current_player_position, show_list=show_list)
        elif zombie_type == 3:
            # Smart horizontal prioritization
            next_zombie_pos.append(generate_type_3(map_data, current_zombie_position, current_player_position) + (zombie_type,))
            if show_list:
                move_list += generate_type_3(map_data, current_zombie_position, current_player_position, show_list=show_list)
    if show_list == False:   
        return next_zombie_pos
    else:
        return move_list

def generate_next_scorpion_positions(map_data: list = [], current_scorpion_positions: list = [], current_player_position: tuple = (), show_list: bool = False) -> list:
    """
    Generates the next positions for all scorpions on the map.
    
    Args:
        map_data: The game map representation
        current_scorpion_positions: List of tuples (x, y, intelligence_level)
        current_player_position:  Tuple (x, y) of player's current position
        show_list:  If True, return list of movements; If False, return next positions only
    
    Returns:
        If show_list == False: List of new scorpion positions [(x, y, intelligence_level), ...]
        If show_list == True: List of movement directions for animation
    """
    def generate_type_0(map_data: list = [], current_scorpion_position: tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 0 Scorpion (Dumb Scorpion).
        - Speed: 1 step.
        - Behavior: Prioritizes Vertical movement. 
        - Feature: Freezes if blocked vertically (does not pathfind around walls).
        """
        
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_vertical_direction(scorpion_pos[1], current_player_position[1])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position:
            if show_list == False:
                return scorpion_pos
            else:
                return move_list

        new_pos = scorpion_pos

        # CASE 1: Vertical Alignment Needed
        if s_y != p_y:
            if s_y > p_y: 
                move_dir, dx, dy = UP, 0, -1
            else:
                move_dir, dx, dy = DOWN, 0, 1
            
            new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)
            if new_pos != scorpion_pos and move_dir is not None:
                move_list.append(move_dir)

        # CASE 2: Same Row (Horizontal Alignment)
        else:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            
            if move_dir is not None:
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)
                if new_pos != scorpion_pos and move_dir is not None:
                    move_list. append(move_dir)

        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        if show_list == False:
            return new_pos
        else:
            return move_list
        
    def generate_type_1(map_data: list = [], current_scorpion_position:  tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 1 Scorpion. 
        - Speed: 1 step.
        - Behavior: Prioritizes Horizontal movement (Left/Right) first. 
        - Feature: Freezes if blocked horizontally (does not pathfind vertically).
        """
        
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_horizontal_direction(scorpion_pos[0], current_player_position[0])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position:
            if show_list == False:
                return scorpion_pos
            else:
                return move_list

        new_pos = scorpion_pos

        # CASE 1: Horizontal Alignment Needed (Priority)
        if s_x != p_x:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            
            new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)
            if new_pos != scorpion_pos and move_dir is not None:
                move_list.append(move_dir)

        # CASE 2: Same Column (Vertical Alignment)
        else:
            move_dir, dx, dy = get_vertical_direction(s_y, p_y)
            
            if move_dir is not None:
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)
                if new_pos != scorpion_pos and move_dir is not None:
                    move_list.append(move_dir)

        if move_list == [] and move_dir is not None: 
            move_list.append(move_dir)

        if show_list == False:
            return new_pos
        else:
            return move_list
    
    def generate_type_2(map_data: list = [], current_scorpion_position:  tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 2 Scorpion (Smart Vertical Scorpion).
        - Speed: 1 step. 
        - Behavior: Prioritizes Vertical movement. 
        - Feature (Smart): If blocked Vertically, it attempts to 'slide' Horizontally 
        instead of freezing. It only freezes if BOTH Vertical and Horizontal paths are blocked.
        """
        
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_vertical_direction(scorpion_pos[1], current_player_position[1])


        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position:
            if show_list == False:
                return scorpion_pos
            else:
                return move_list

        new_pos = scorpion_pos

        # CASE 1: Vertical Alignment Needed (Priority)
        if s_y != p_y:
            move_dir, dx, dy = get_vertical_direction(s_y, p_y)
            
            attempt_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)

            if attempt_pos != scorpion_pos:
                new_pos = attempt_pos
                if move_dir is not None: 
                    move_list.append(move_dir)
            else:
                # [SMART FALLBACK] Blocked Vertically -> Try Horizontal immediately
                h_dir, h_dx, h_dy = get_horizontal_direction(s_x, p_x)
                
                if h_dir is not None:
                    new_pos = try_move(map_data, scorpion_pos, h_dir, h_dx, h_dy)
                    if new_pos != scorpion_pos and h_dir is not None:
                        move_list.append(h_dir)

        # CASE 2: Already on Same Row (Only Horizontal option)
        else:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            if move_dir is not None: 
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)
                if new_pos != scorpion_pos and move_dir is not None: 
                    move_list.append(move_dir)

        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        if show_list == False:
            return new_pos
        else:
            return move_list
    
    def generate_type_3(map_data:  list = [], current_scorpion_position: tuple = [], current_player_position: tuple = (), show_list: bool = False) -> tuple:
        """
        Calculates the new position for a Type 3 Scorpion (Smart Horizontal Scorpion).
        - Speed: 1 step.
        - Behavior: Prioritizes Horizontal movement (Left/Right).
        - Feature (Smart): If blocked Horizontally, it attempts to 'slide' Vertically. 
        """
        
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_horizontal_direction(scorpion_pos[0], current_player_position[0])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position:
            if show_list == False:
                return scorpion_pos
            else: 
                return move_list

        new_pos = scorpion_pos

        # CASE 1: Horizontal Alignment Needed (Priority)
        if s_x != p_x:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            
            attempt_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)

            if attempt_pos != scorpion_pos:
                new_pos = attempt_pos
                if move_dir is not None:
                    move_list. append(move_dir)
            else:
                # [SMART FALLBACK] Blocked Horizontally -> Try Vertical immediately
                v_dir, v_dx, v_dy = get_vertical_direction(s_y, p_y)
                
                if v_dir is not None:
                    new_pos = try_move(map_data, scorpion_pos, v_dir, v_dx, v_dy)
                    if new_pos != scorpion_pos and v_dir is not None:
                        move_list.append(v_dir)

        # CASE 2: Already on Same Column (Only Vertical option)
        else:
            move_dir, dx, dy = get_vertical_direction(s_y, p_y)
            if move_dir is not None:
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy)
                if new_pos != scorpion_pos and move_dir is not None:
                    move_list. append(move_dir)

        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        if show_list == False:
            return new_pos
        else:
            return move_list


    #----------------------------------------------------------#
    #----- Main logic of GENERATE_NEXT_SCORPION_POSITIONS -----#
    #----------------------------------------------------------#
    '''
    Type of scorpion: 
        0: scorpion prioritizes moving vertically (UP/DOWN)
        1: scorpion prioritizes moving horizontally (LEFT/RIGHT)
        2: scorpion smarter, prioritizes moving up/down first, then left/right
        3: scorpion smarter, prioritizes moving left/right first, then up/down

    show_list: bool (Apply for all small functions inside)
        If True: return list of movements
        If False: return next positions only
     '''
    
    next_scorpion_pos = []
    move_list = []

    for scorpion_info in current_scorpion_positions:
        current_scorpion_position = (scorpion_info[0], scorpion_info[1])
        intelligence_level = scorpion_info[2]

        if intelligence_level == 0:
            next_scorpion_pos.append(generate_type_0(map_data, current_scorpion_position, current_player_position) + (intelligence_level,))
            if show_list: 
                move_list += generate_type_0(map_data, current_scorpion_position, current_player_position, show_list=show_list)
        elif intelligence_level == 1:
            next_scorpion_pos.append(generate_type_1(map_data, current_scorpion_position, current_player_position) + (intelligence_level,))
            if show_list:
                move_list += generate_type_1(map_data, current_scorpion_position, current_player_position, show_list=show_list)
        elif intelligence_level == 2:
            next_scorpion_pos.append(generate_type_2(map_data, current_scorpion_position, current_player_position) + (intelligence_level,))
            if show_list:
                move_list += generate_type_2(map_data, current_scorpion_position, current_player_position, show_list=show_list)
        elif intelligence_level == 3:
            next_scorpion_pos.append(generate_type_3(map_data, current_scorpion_position, current_player_position) + (intelligence_level,))
            if show_list:
                move_list += generate_type_3(map_data, current_scorpion_position, current_player_position, show_list=show_list)

            
    if show_list == False:    
        return next_scorpion_pos
    else: 
        return move_list

def check_same_pos(next_zombie_positions: list, next_scorpion_positions: list, superdata = None) -> Tuple:
    # Check if two zombie in a same position
    zombie_i = 0
    while zombie_i < len(next_zombie_positions):
        zombie_j = zombie_i + 1
        while zombie_j < len(next_zombie_positions):
            if (next_zombie_positions[zombie_i][0], next_zombie_positions[zombie_i][1]) == (next_zombie_positions[zombie_j][0], next_zombie_positions[zombie_j][1]):
                # If two zombies in same position, keep the one with higher type value
                if next_zombie_positions[zombie_i][2] >= next_zombie_positions[zombie_j][2]:
                    next_zombie_positions.pop(zombie_j)
                else:
                    next_zombie_positions.pop(zombie_i)
                    zombie_i -= 1
                    break
            else:
                zombie_j += 1
        zombie_i += 1

    # Check if two scorpions in a same position
    scorpion_i = 0
    while scorpion_i < len(next_scorpion_positions):
        scorpion_j = scorpion_i + 1
        while scorpion_j < len(next_scorpion_positions):
            if (next_scorpion_positions[scorpion_i][0], next_scorpion_positions[scorpion_i][1]) == (next_scorpion_positions[scorpion_j][0], next_scorpion_positions[scorpion_j][1]):
                # If two scorpions in same position, keep the one with higher intelligence level
                if next_scorpion_positions[scorpion_i][2] >= next_scorpion_positions[scorpion_j][2]:
                    next_scorpion_positions.pop(scorpion_j)
                else:
                    next_scorpion_positions.pop(scorpion_i)
                    scorpion_i -= 1
                    break
            else:
                scorpion_j += 1
        scorpion_i += 1
    
    # check if any zombie is in trap, if yes remove it
    next_zombie_positions = [zombie for zombie in next_zombie_positions if not is_trap(superdata, (zombie[0], zombie[1]))]

    # check if any scorpion is in trap, if yes remove it
    next_scorpion_positions = [scorpion for scorpion in next_scorpion_positions if not is_trap(superdata, (scorpion[0], scorpion[1]))]

    # Check if any zombie and scorpion in same position, if yes remove both
    zombie_i = 0
    while zombie_i < len(next_zombie_positions):
        scorpion_i = 0
        while scorpion_i < len(next_scorpion_positions):
            if (next_zombie_positions[zombie_i][0], next_zombie_positions[zombie_i][1]) == (next_scorpion_positions[scorpion_i][0], next_scorpion_positions[scorpion_i][1]):
                next_zombie_positions.pop(zombie_i)
                next_scorpion_positions.pop(scorpion_i)
                zombie_i -= 1
                break
            else:
                scorpion_i += 1
        zombie_i += 1
    
    return next_zombie_positions, next_scorpion_positions

def Shortest_Path(superdata: dict, start: tuple, goal: tuple, zombie_positions: list = [], scorpion_positions: list = []) -> list:
    """
    Finds shortest path from start to goal while avoiding: 
    - Zombies (move 2 steps per turn)
    - Scorpions (move 1 step per turn)  
    - Traps (static obstacles)
    - Closed gates (can be opened with keys)
    
    Uses BFS with state tracking:  (position, gate_state, zombie_positions, scorpion_positions)
    
    Args:
        superdata: Dictionary containing map_data, gate_pos, key_pos, trap_pos
        start: Starting position (x, y)
        goal: Goal position (x, y)
        zombie_positions: List of zombie positions [(x, y, type), ...]
        scorpion_positions: List of scorpion positions [(x, y, intelligence_level), ...]
    
    Returns:
        list: Shortest path from start to goal as [(x1,y1), (x2,y2), ...], or [] if no path exists
    """
    
    #----- STEP 1: INITIALIZE GRAPH AND VARIABLES -----#
    map_data = superdata["map_data"]
    
    # Extract gate and key positions from superdata
    gate_pos = tuple(superdata. get("gate_pos", [])) if superdata.get("gate_pos") else None
    key_pos = tuple(superdata.get("key_pos", [])) if superdata.get("key_pos") else None
    
    # Initial gate state (assume closed at start, unless player starts on key)
    initial_gate_opened = False
    if key_pos and (start[0], start[1]) == (key_pos[0], key_pos[1]):
        initial_gate_opened = True
    
    # Limit steps to avoid infinite loops in complex maps
    count_steps = 0
    threshold_steps = 1000000
    
    #---------------------------------------------------------------#
    #---------- STEP 2: VALIDATE START AND GOAL POSITIONS ----------#
    #---------------------------------------------------------------#
    
    #----- Step 2.1: Check if start or goal is on trap -----#
    if is_trap(superdata, start) or is_trap(superdata, goal):
        print("Error: Start or goal is on trap position")
        return []
    
    #----- Step 2.2: Check if already at goal -----#
    if start == goal:
        if not is_lose(superdata, start, zombie_positions, scorpion_positions):
            return [start]
        else:
            print("Error: Start equals goal but player dies immediately")
            return []
    
    #-----------------------------------------------------------------------------------#
    #---------------------- STEP 3: INITIALIZE BFS DATA STRUCTURES ---------------------#
    #-----------------------------------------------------------------------------------#
    
    #----- Step 3.1: Initialize visited set with state tuples -----#
    # State = (position, gate_opened, zombie_tuple, scorpion_tuple)
    visited = set()
    
    initial_state = (start, initial_gate_opened, tuple(zombie_positions), tuple(scorpion_positions))
    visited.add(initial_state)
    
    #----- Step 3.2: Initialize path queue -----#
    # Queue elements:  [[path_list], gate_opened, zombie_list, scorpion_list]
    path_queue = deque([[[start], initial_gate_opened, zombie_positions, scorpion_positions]])
    
    #---------------------------------------------------------------------------------------#
    #----- STEP 4: BFS LOOP TO FIND SHORTEST PATH -----#
    #---------------------------------------------------------------------------------------#
    while path_queue and count_steps < threshold_steps: 
        count_steps += 1
        
        #----- Step 4.1: Dequeue current path and state -----#
        current_data = path_queue.popleft()
        player_path = current_data[0]          # List:  [(x1,y1), (x2,y2), ...]
        gate_opened = current_data[1]          # Bool: True/False
        zombie_list = current_data[2]          # List: [(x,y,type),...]
        scorpion_list = current_data[3]        # List: [(x,y,intelligence_level),...]
        
        current_position = player_path[-1]
        
        #----- Step 4.2: Skip if current position is a trap -----#
        if is_trap(superdata, current_position):
            continue
        
        #----- Step 4.3: Check if player is caught by enemies -----#
        player_died = is_lose(superdata, current_position, zombie_list, scorpion_list)
        
        #-----------------------------------------------------------------------------------#
        #----- STEP 5: IF PLAYER IS ALIVE, EXPLORE NEXT POSITIONS -----#
        #-----------------------------------------------------------------------------------#
        if not player_died:
            
            #----- Step 5.1: Generate graph based on current gate state -----#
            # Graph changes when gate opens/closes
            graph = generate_graph(superdata, gate_opened)
            
            #-----------------------------------------------------------------------------------#
            #----- STEP 6: TRY STAYING IN PLACE (IF NOT 4-WAY CONNECTED) -----#
            #-----------------------------------------------------------------------------------#
            if len(graph[current_position]) < 4:
                neighbor = current_position
                cur_path = player_path. copy()
                cur_path. append(neighbor)
                
                #----- Step 6.1: Check if stepping on key -> toggle gate state -----#
                new_gate_opened = gate_opened
                if key_pos and (neighbor[0], neighbor[1]) == (key_pos[0], key_pos[1]):
                    new_gate_opened = not gate_opened
                
                #----- Step 6.2: Generate next positions for enemies after player moves -----#
                new_zombie_positions = generate_next_zombie_positions(map_data, zombie_list, neighbor)
                new_scorpion_positions = generate_next_scorpion_positions(map_data, scorpion_list, neighbor)
                new_zombie_positions, new_scorpion_positions = check_same_pos(new_zombie_positions, new_scorpion_positions, superdata)
                
                #----- Step 6.3: Add to queue if state not visited -----#
                state = (neighbor, new_gate_opened, tuple(new_zombie_positions), tuple(new_scorpion_positions))
                if state not in visited:
                    path_queue.append([cur_path, new_gate_opened, new_zombie_positions, new_scorpion_positions])
                    visited.add(state)
            
            #-----------------------------------------------------------------------------------#
            #----- STEP 7: TRY ALL NEIGHBORING POSITIONS -----#
            #-----------------------------------------------------------------------------------#
            for neighbor in graph[current_position]: 
                
                #----- Step 7.1: Skip if neighbor is a trap -----#
                if is_trap(superdata, neighbor):
                    continue
                
                #----- Step 7.2: Create new path including this neighbor -----#
                cur_path = player_path.copy()
                cur_path.append(neighbor)
                
                #----- Step 7.3: Check if stepping on key -> toggle gate state -----#
                new_gate_opened = gate_opened
                if key_pos and (neighbor[0], neighbor[1]) == (key_pos[0], key_pos[1]):
                    new_gate_opened = not gate_opened
                
                #----- Step 7.4: Generate next positions for enemies after player moves -----#
                new_zombie_positions = generate_next_zombie_positions(map_data, zombie_list, neighbor)
                new_scorpion_positions = generate_next_scorpion_positions(map_data, scorpion_list, neighbor)
                new_zombie_positions, new_scorpion_positions = check_same_pos(new_zombie_positions, new_scorpion_positions, superdata)
                
                #-----------------------------------------------------------------------------#
                #----- STEP 8: CHECK IF REACHED GOAL AND PLAYER SURVIVES -----#
                #-----------------------------------------------------------------------------#
                if neighbor == goal and not is_lose(superdata, neighbor, new_zombie_positions, new_scorpion_positions):
                    print(f"Path found in {count_steps} steps!")
                    return cur_path
                
                #----- Step 8.1: Otherwise, add to queue if state not visited -----#
                state = (neighbor, new_gate_opened, tuple(new_zombie_positions), tuple(new_scorpion_positions))
                if state not in visited:
                    path_queue.append([cur_path, new_gate_opened, new_zombie_positions, new_scorpion_positions])
                    visited.add(state)
        
        #----- Step 4.4: If player died, skip this path (do nothing) -----#
        else:
            continue
    
    #----- STEP 9: NO PATH FOUND -----#
    print(f"No path found after {count_steps} steps")
    return []

if __name__ == "__main__":
    import map_collection as maps
    #------------------ TESTING CODE ------------------#
    map_collection = maps.maps_collection

    print(Shortest_Path(map_collection[0]['map_data'], (2,5), (3,5), [(2,5,3)]))
    # print(is_linked(map_collection[0]['map_data'], (2,2), UP))