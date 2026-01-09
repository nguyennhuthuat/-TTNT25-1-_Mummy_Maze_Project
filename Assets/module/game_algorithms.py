from collections import deque

from click import Tuple
from . utils import is_linked
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
        superdata:  Dictionary containing map_data, gate_pos, key_pos, trap_pos
        gate_opened:   Current state of gate
    
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
    visited. add(start)
    while stack:
        vertex = stack. pop()

        for neighbor in graph[vertex]: 
            if neighbor not in visited: 
                visited.add(neighbor)
                stack.append(neighbor)
    return visited

def try_move(game_map: list, current_pos: tuple, direction: str, delta_x: int, delta_y:  int, 
             gate_opened: bool = False, superdata: dict = None) -> tuple:
    """
    Attempts to move in a specific direction considering walls and gates.
    Returns the new coordinate if linked, otherwise returns the current coordinate.
    
    Args:
        game_map: Map data matrix
        current_pos: Current position (x, y) in 1-indexed coordinates
        direction: Direction constant (UP/DOWN/LEFT/RIGHT)
        delta_x: Change in x coordinate
        delta_y: Change in y coordinate
        gate_opened:  Whether gate is currently opened
        superdata: Full map data including gate_pos, key_pos, trap_pos
    
    Returns:
        tuple: New position if move is valid, otherwise current position
    """
    if is_linked(game_map, current_pos, direction, gate_opened, superdata):
        return (current_pos[0] + delta_x, current_pos[1] + delta_y)
    return current_pos

def get_horizontal_direction(zombie_x: int, player_x: int) -> tuple:
    """
    Determines the horizontal direction towards the player.
    Returns:  (direction_constant, delta_x, delta_y)
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

#==============================================================================
#                         ZOMBIE MOVEMENT SYSTEM
#==============================================================================

def generate_next_zombie_positions(
    map_data: list = [], 
    current_zombie_positions: list = [], 
    current_player_position: tuple = (), 
    gate_opened: bool = False, 
    superdata: dict = None, 
    show_list: bool = False
) -> list:
    """
    Generate next positions for all zombies considering walls, gates, and player position.
    
    Args:
        map_data: Map data matrix
        current_zombie_positions:  List of zombie tuples [(x, y, type), ...]
        current_player_position: Player position (x, y)
        gate_opened: Current state of gate (True = open, False = closed)
        superdata: Full map data including gate_pos, key_pos, trap_pos
        show_list:  If True, return movement directions; if False, return positions
    
    Returns:
        List of next zombie positions or movement directions
    
    Zombie Types:
        Type 0: Vertical priority, dumb (freezes if blocked vertically)
        Type 1: Horizontal priority, dumb (freezes if blocked horizontally)
        Type 2: Vertical priority, smart (tries horizontal if blocked vertically)
        Type 3: Horizontal priority, smart (tries vertical if blocked horizontally)
    """

    def generate_type_0(
        map_data: list, 
        current_zombie_position: tuple, 
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 0 Zombie:  Vertical Priority, Dumb AI
        - Speed: 2 steps per turn
        - Behavior: Prioritizes vertical movement (UP/DOWN)
        - Weakness: Freezes if blocked vertically, won't try horizontal
        """
        zombie_pos = current_zombie_position
        move_list = []
        
        # Determine initial direction
        move_dir, dx, dy = get_vertical_direction(zombie_pos[1], current_player_position[1])
        
        # Move up to 2 steps
        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            # Stop if caught player
            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Vertical Alignment Needed (Priority)
            if z_y != p_y: 
                # Determine vertical direction
                if z_y > p_y: 
                    move_dir, dx, dy = UP, 0, -1
                else:
                    move_dir, dx, dy = DOWN, 0, 1
                
                # Attempt vertical move (gate affects this!)
                new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)
                if new_pos != zombie_pos and move_dir is not None: 
                    move_list.append(move_dir)

                # [DUMB AI] Freeze if blocked vertically
                if new_pos == zombie_pos:
                    break

            # CASE 2: Same Row - Move Horizontally
            else:
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                
                if move_dir is not None: 
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)
                    if new_pos != zombie_pos: 
                        move_list.append(move_dir)

            zombie_pos = new_pos

        # Add idle animation if can't move
        if move_list == [] and move_dir is not None:
            move_list. append(move_dir)

        return move_list if show_list else zombie_pos
        
    def generate_type_1(
        map_data: list,
        current_zombie_position:  tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 1 Zombie: Horizontal Priority, Dumb AI
        - Speed: 2 steps per turn
        - Behavior:  Prioritizes horizontal movement (LEFT/RIGHT)
        - Weakness:  Freezes if blocked horizontally, won't try vertical
        """
        zombie_pos = current_zombie_position
        move_list = []

        # Determine initial direction
        move_dir, dx, dy = get_horizontal_direction(zombie_pos[0], current_player_position[0])
        
        # Move up to 2 steps
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
                
                # Attempt horizontal move
                new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)
                if new_pos != zombie_pos and move_dir is not None: 
                    move_list.append(move_dir)
                    
                # [DUMB AI] Freeze if blocked horizontally
                if new_pos == zombie_pos:
                    break

            # CASE 2: Same Column - Move Vertically
            else:
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                
                if move_dir is not None: 
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)
                    if new_pos != zombie_pos:
                        move_list.append(move_dir)

            zombie_pos = new_pos

        # Add idle animation if can't move
        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        return move_list if show_list else zombie_pos
    
    def generate_type_2(
        map_data: list,
        current_zombie_position: tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 2 Zombie:  Vertical Priority, Smart AI
        - Speed: 2 steps per turn
        - Behavior: Prioritizes vertical movement (UP/DOWN)
        - Intelligence: If blocked vertically, tries horizontal (sliding)
        """
        zombie_pos = current_zombie_position
        move_list = []

        # Determine initial direction
        move_dir, dx, dy = get_vertical_direction(zombie_pos[1], current_player_position[1])

        # Move up to 2 steps
        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Vertical Alignment Needed (Priority)
            if z_y != p_y:
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                
                # Try vertical move first (gate may block this!)
                attempt_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)

                if attempt_pos != zombie_pos:
                    # Vertical move succeeded
                    new_pos = attempt_pos
                    if move_dir is not None: 
                        move_list.append(move_dir)
                else:
                    # [SMART AI] Blocked vertically -> Try horizontal slide
                    h_dir, h_dx, h_dy = get_horizontal_direction(z_x, p_x)
                    
                    if h_dir is not None:
                        new_pos = try_move(map_data, zombie_pos, h_dir, h_dx, h_dy, gate_opened, superdata)
                        if new_pos != zombie_pos:
                            move_list.append(h_dir)

            # CASE 2: Same Row - Move Horizontally
            else: 
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                if move_dir is not None: 
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)
                    if new_pos != zombie_pos:
                        move_list.append(move_dir)

            zombie_pos = new_pos

        # Add idle animation if can't move
        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        return move_list if show_list else zombie_pos
    
    def generate_type_3(
        map_data:  list,
        current_zombie_position: tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 3 Zombie:  Horizontal Priority, Smart AI
        - Speed: 2 steps per turn
        - Behavior:  Prioritizes horizontal movement (LEFT/RIGHT)
        - Intelligence: If blocked horizontally, tries vertical (sliding)
        """
        zombie_pos = current_zombie_position
        move_list = []

        # Determine initial direction
        move_dir, dx, dy = get_horizontal_direction(zombie_pos[0], current_player_position[0])

        # Move up to 2 steps
        for _ in range(2):
            z_x, z_y = zombie_pos
            p_x, p_y = current_player_position

            if zombie_pos == current_player_position:
                break

            new_pos = zombie_pos

            # CASE 1: Horizontal Alignment Needed (Priority)
            if z_x != p_x:
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                
                # Try horizontal move first
                attempt_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)

                if attempt_pos != zombie_pos:
                    # Horizontal move succeeded
                    new_pos = attempt_pos
                    if move_dir is not None:
                        move_list. append(move_dir)
                else:
                    # [SMART AI] Blocked horizontally -> Try vertical slide
                    v_dir, v_dx, v_dy = get_vertical_direction(z_y, p_y)
                    
                    if v_dir is not None:
                        new_pos = try_move(map_data, zombie_pos, v_dir, v_dx, v_dy, gate_opened, superdata)
                        if new_pos != zombie_pos: 
                            move_list.append(v_dir)

            # CASE 2: Same Column - Move Vertically
            else: 
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy, gate_opened, superdata)
                    if new_pos != zombie_pos: 
                        move_list.append(move_dir)

            zombie_pos = new_pos

        # Add idle animation if can't move
        if move_list == [] and move_dir is not None: 
            move_list.append(move_dir)

        return move_list if show_list else zombie_pos

    #--------------------------------------------------------#
    #----- Main Logic:  Process All Zombies -----#
    #--------------------------------------------------------#
    
    next_zombie_pos = []
    move_list = []

    for zombie_info in current_zombie_positions: 
        current_zombie_position = (zombie_info[0], zombie_info[1])
        zombie_type = zombie_info[2]

        # Dispatch to appropriate AI type
        if zombie_type == 0:
            result = generate_type_0(map_data, current_zombie_position, current_player_position, gate_opened, superdata, show_list)
        elif zombie_type == 1:
            result = generate_type_1(map_data, current_zombie_position, current_player_position, gate_opened, superdata, show_list)
        elif zombie_type == 2:
            result = generate_type_2(map_data, current_zombie_position, current_player_position, gate_opened, superdata, show_list)
        elif zombie_type == 3:
            result = generate_type_3(map_data, current_zombie_position, current_player_position, gate_opened, superdata, show_list)
        else:
            continue  # Invalid zombie type
        
        if show_list:
            move_list += result
        else:
            next_zombie_pos. append(result + (zombie_type,))
    
    return move_list if show_list else next_zombie_pos


#==============================================================================
#                        SCORPION MOVEMENT SYSTEM
#==============================================================================

def generate_next_scorpion_positions(
    map_data: list = [], 
    current_scorpion_positions: list = [], 
    current_player_position: tuple = (),
    gate_opened: bool = False,
    superdata:  dict = None,
    show_list: bool = False
) -> list:
    """
    Generate next positions for all scorpions considering walls, gates, and player position. 
    
    Args:
        map_data: Map data matrix
        current_scorpion_positions: List of scorpion tuples [(x, y, intelligence_level), ...]
        current_player_position: Player position (x, y)
        gate_opened:  Current state of gate (True = open, False = closed)
        superdata: Full map data including gate_pos, key_pos, trap_pos
        show_list: If True, return movement directions; if False, return positions
    
    Returns:
        List of next scorpion positions or movement directions
    
    Scorpion Types: 
        Type 0: Vertical priority, dumb (freezes if blocked vertically)
        Type 1: Horizontal priority, dumb (freezes if blocked horizontally)
        Type 2: Vertical priority, smart (tries horizontal if blocked vertically)
        Type 3: Horizontal priority, smart (tries vertical if blocked horizontally)
    """
    
    def generate_type_0(
        map_data: list,
        current_scorpion_position: tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 0 Scorpion: Vertical Priority, Dumb AI
        - Speed: 1 step per turn
        - Behavior: Prioritizes vertical movement (UP/DOWN)
        - Weakness: Freezes if blocked vertically
        """
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_vertical_direction(scorpion_pos[1], current_player_position[1])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position:
            return move_list if show_list else scorpion_pos

        new_pos = scorpion_pos

        # CASE 1: Vertical Alignment Needed
        if s_y != p_y:
            if s_y > p_y: 
                move_dir, dx, dy = UP, 0, -1
            else:
                move_dir, dx, dy = DOWN, 0, 1
            
            new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)
            if new_pos != scorpion_pos and move_dir is not None: 
                move_list.append(move_dir)

        # CASE 2: Same Row (Horizontal Alignment)
        else:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            
            if move_dir is not None:
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)
                if new_pos != scorpion_pos:
                    move_list. append(move_dir)

        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        return move_list if show_list else new_pos
        
    def generate_type_1(
        map_data: list,
        current_scorpion_position: tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 1 Scorpion: Horizontal Priority, Dumb AI
        - Speed:  1 step per turn
        - Behavior: Prioritizes horizontal movement (LEFT/RIGHT)
        - Weakness: Freezes if blocked horizontally
        """
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_horizontal_direction(scorpion_pos[0], current_player_position[0])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position:
            return move_list if show_list else scorpion_pos

        new_pos = scorpion_pos

        # CASE 1: Horizontal Alignment Needed (Priority)
        if s_x != p_x:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            
            new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)
            if new_pos != scorpion_pos and move_dir is not None: 
                move_list.append(move_dir)

        # CASE 2: Same Column (Vertical Alignment)
        else:
            move_dir, dx, dy = get_vertical_direction(s_y, p_y)
            
            if move_dir is not None:
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)
                if new_pos != scorpion_pos:
                    move_list.append(move_dir)

        if move_list == [] and move_dir is not None: 
            move_list.append(move_dir)

        return move_list if show_list else new_pos
    
    def generate_type_2(
        map_data: list,
        current_scorpion_position: tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata:  dict,
        show_list:  bool = False
    ) -> tuple:
        """
        Type 2 Scorpion:  Vertical Priority, Smart AI
        - Speed: 1 step per turn
        - Behavior: Prioritizes vertical movement (UP/DOWN)
        - Intelligence: If blocked vertically, tries horizontal
        """
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_vertical_direction(scorpion_pos[1], current_player_position[1])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position: 
            return move_list if show_list else scorpion_pos

        new_pos = scorpion_pos

        # CASE 1: Vertical Alignment Needed (Priority)
        if s_y != p_y:
            move_dir, dx, dy = get_vertical_direction(s_y, p_y)
            
            attempt_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)

            if attempt_pos != scorpion_pos:
                new_pos = attempt_pos
                if move_dir is not None: 
                    move_list.append(move_dir)
            else:
                # [SMART AI] Blocked Vertically -> Try Horizontal
                h_dir, h_dx, h_dy = get_horizontal_direction(s_x, p_x)
                
                if h_dir is not None: 
                    new_pos = try_move(map_data, scorpion_pos, h_dir, h_dx, h_dy, gate_opened, superdata)
                    if new_pos != scorpion_pos:
                        move_list.append(h_dir)

        # CASE 2: Same Row (Horizontal only)
        else:
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            if move_dir is not None: 
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)
                if new_pos != scorpion_pos: 
                    move_list.append(move_dir)

        if move_list == [] and move_dir is not None:
            move_list.append(move_dir)

        return move_list if show_list else new_pos
    
    def generate_type_3(
        map_data: list,
        current_scorpion_position: tuple,
        current_player_position: tuple,
        gate_opened: bool,
        superdata: dict,
        show_list: bool = False
    ) -> tuple:
        """
        Type 3 Scorpion: Horizontal Priority, Smart AI
        - Speed: 1 step per turn
        - Behavior: Prioritizes horizontal movement (LEFT/RIGHT)
        - Intelligence: If blocked horizontally, tries vertical
        """
        scorpion_pos = current_scorpion_position
        move_list = []
        
        move_dir, dx, dy = get_horizontal_direction(scorpion_pos[0], current_player_position[0])

        s_x, s_y = scorpion_pos
        p_x, p_y = current_player_position

        if scorpion_pos == current_player_position: 
            return move_list if show_list else scorpion_pos

        new_pos = scorpion_pos

        # CASE 1: Horizontal Alignment Needed (Priority)
        if s_x != p_x: 
            move_dir, dx, dy = get_horizontal_direction(s_x, p_x)
            
            attempt_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)

            if attempt_pos != scorpion_pos:
                new_pos = attempt_pos
                if move_dir is not None: 
                    move_list.append(move_dir)
            else:
                # [SMART AI] Blocked Horizontally -> Try Vertical
                v_dir, v_dx, v_dy = get_vertical_direction(s_y, p_y)
                
                if v_dir is not None:
                    new_pos = try_move(map_data, scorpion_pos, v_dir, v_dx, v_dy, gate_opened, superdata)
                    if new_pos != scorpion_pos: 
                        move_list.append(v_dir)

        # CASE 2: Same Column (Vertical only)
        else:
            move_dir, dx, dy = get_vertical_direction(s_y, p_y)
            if move_dir is not None:
                new_pos = try_move(map_data, scorpion_pos, move_dir, dx, dy, gate_opened, superdata)
                if new_pos != scorpion_pos:
                    move_list.append(move_dir)

        if move_list == [] and move_dir is not None: 
            move_list.append(move_dir)

        return move_list if show_list else new_pos

    #----------------------------------------------------------#
    #----- Main Logic: Process All Scorpions -----#
    #----------------------------------------------------------#
    
    next_scorpion_pos = []
    move_list = []

    for scorpion_info in current_scorpion_positions:
        current_scorpion_position = (scorpion_info[0], scorpion_info[1])
        intelligence_level = scorpion_info[2]

        # Dispatch to appropriate AI type
        if intelligence_level == 0:
            result = generate_type_0(map_data, current_scorpion_position, current_player_position, gate_opened, superdata, show_list)
        elif intelligence_level == 1:
            result = generate_type_1(map_data, current_scorpion_position, current_player_position, gate_opened, superdata, show_list)
        elif intelligence_level == 2:
            result = generate_type_2(map_data, current_scorpion_position, current_player_position, gate_opened, superdata, show_list)
        elif intelligence_level == 3:
            result = generate_type_3(map_data, current_scorpion_position, current_player_position, gate_opened, superdata, show_list)
        else:
            continue  # Invalid scorpion type

        if show_list:
            move_list += result
        else:
            next_scorpion_pos.append(result + (intelligence_level,))
            
    return move_list if show_list else next_scorpion_pos


def check_same_pos(next_zombie_positions: list, next_scorpion_positions: list, superdata = None) -> Tuple: 
    # Check if two zombie in a same position
    zombie_i = 0
    while zombie_i < len(next_zombie_positions):
        zombie_j = zombie_i + 1
        while zombie_j < len(next_zombie_positions):
            if (next_zombie_positions[zombie_i][0], next_zombie_positions[zombie_i][1]) == (next_zombie_positions[zombie_j][0], next_zombie_positions[zombie_j][1]):
                # If two zombies in same position, keep the one with higher type value
                if next_zombie_positions[zombie_i][2] >= next_zombie_positions[zombie_j][2]:
                    next_zombie_positions. pop(zombie_j)
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
                    next_scorpion_positions. pop(scorpion_j)
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

def Shortest_Path(superdata:  dict, start: tuple, goal: tuple, zombie_positions: list = [], scorpion_positions: list = []) -> list:
    """
    Finds OPTIMAL shortest path from start to goal using BFS with state-space search.
    
    ╔═════════════════════════════════════════════════════════���════════════════╗
    ║                     GAME MECHANICS & OPTIMIZATIONS                       ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    
    1.  GATE SYSTEM:
       ✓ Gates block vertical movement (UP/DOWN) when closed
       ✓ Gates do NOT block horizontal movement (LEFT/RIGHT)  
       ✓ Gates start CLOSED by default
       ✓ Gate state:  CLOSED (False) or OPEN (True)
    
    2. KEY SYSTEM (TOGGLE SWITCH):
       ✓ Key is placed at a specific position on the map
       ✓ When player steps on key position → Gate TOGGLES state
       ✓ CLOSED → OPEN or OPEN → CLOSED
       ✓ Player can toggle gate multiple times by revisiting key
    
    3. OPTIMIZATION STRATEGY:
       ✓ Penalize unnecessary key toggles
       ✓ Prioritize paths that minimize key touches
       ✓ Use path length + key_toggle_penalty for comparison
    
    4. STATE SPACE: 
       ✓ State = (position, gate_opened, zombie_positions, scorpion_positions)
       ✓ Each unique state is visited only once (prevents infinite loops)
       ✓ BFS with priority explores optimal paths first
    """
    
    #══════════════════════════════════════════════════════════════════════════
    #                         STEP 1: INITIALIZATION
    #══════════════════════════════════════════════════════════════════════════
    
    map_data = superdata["map_data"]
    
    # Extract game object positions
    gate_pos = superdata. get("gate_pos", [])
    key_pos = superdata.get("key_pos", [])
    
    # Convert to tuples for hashability
    gate_pos = tuple(gate_pos) if gate_pos and gate_pos != [] else None
    key_pos = tuple(key_pos) if key_pos and key_pos != [] else None
    
    # Initial gate state:  CLOSED by default
    initial_gate_opened = False
    
    # Special case: Player starts ON the key → Gate toggles immediately
    if key_pos and (start[0], start[1]) == (key_pos[0], key_pos[1]):
        initial_gate_opened = True
        print(f"🔑 Player starts on key at {key_pos} → Gate toggles to OPEN")
    
    # Performance limit
    count_steps = 0
    MAX_ITERATIONS = 1000000
    
    #══════════════════════════════════════════════════════════════════════════
    #                         STEP 2: INPUT VALIDATION
    #══════════════════════════════════════════════════════════════════════════
    
    if is_trap(superdata, start):
        print(f"❌ Start position {start} is on a trap!")
        return []
    
    if is_trap(superdata, goal):
        print(f"❌ Goal position {goal} is on a trap!")
        return []
    
    if start == goal:
        if not is_lose(superdata, start, zombie_positions, scorpion_positions):
            return [start]
        else: 
            print(f"❌ Start equals goal but player dies immediately")
            return []
    
    #═════════════════���════════════════════════════════════════════════════════
    #                    STEP 3: BFS DATA STRUCTURES  
    #══════════════════════════════════════════════════════════════════════════
    
    visited = set()
    
    initial_state = (
        start,
        initial_gate_opened,
        tuple(zombie_positions),
        tuple(scorpion_positions)
    )
    visited.add(initial_state)
    
    # Enhanced queue:  [path, gate_opened, zombie_list, scorpion_list, key_toggle_count]
    queue = deque([[
        [start],              # path
        initial_gate_opened,  # gate_opened
        zombie_positions,     # zombie_list
        scorpion_positions,   # scorpion_list
        1 if initial_gate_opened else 0  # key_toggle_count
    ]])
    
    # Track best solution
    best_solution = None
    best_score = float('inf')  # Lower is better:  path_length + key_toggles * PENALTY
    
    # Optimization parameters
    KEY_TOGGLE_PENALTY = 100  # Heavily penalize unnecessary key toggles
    
    # Statistics tracking
    max_path_length = 0
    states_explored = 0
    
    #══════════════════════════════════════════════════════════════════════════
    #                    STEP 4: BFS MAIN LOOP
    #══════════════════════════════════════════════════════════════════════════
    
    while queue and count_steps < MAX_ITERATIONS: 
        count_steps += 1
        states_explored += 1
        
        # Dequeue current state
        current_data = queue.popleft()
        path = current_data[0]
        gate_opened = current_data[1]
        zombie_list = current_data[2]
        scorpion_list = current_data[3]
        key_toggle_count = current_data[4]
        
        current_pos = path[-1]
        
        # Track longest path for debugging
        if len(path) > max_path_length:
            max_path_length = len(path)
        
        # Skip traps
        if is_trap(superdata, current_pos):
            continue
        
        # Skip if player dies
        if is_lose(superdata, current_pos, zombie_list, scorpion_list):
            continue
        
        # ✨ OPTIMIZATION: Skip if current path is already worse than best solution
        current_score = len(path) + key_toggle_count * KEY_TOGGLE_PENALTY
        if current_score >= best_score:
            continue
        
        #──────────────────────────────────────────────────────────────────────
        #              STEP 5: GENERATE GRAPH BASED ON GATE STATE
        #──────────────────────────────────────────────────────────────────────
        
        # Graph changes dynamically based on gate state! 
        graph = generate_graph(superdata, gate_opened)
        
        # Get reachable neighbors
        neighbors = graph.get(current_pos, [])
        
        # Optimization: Allow "wait" move if not fully connected
        if len(neighbors) < 4:
            neighbors = [current_pos] + neighbors
        
        #──────────────────────────────────────────────────────────────────────
        #              STEP 6: EXPLORE EACH NEIGHBOR
        #──────────────────────────────────────────────────────────────────────
        
        for neighbor in neighbors: 
            
            # Skip traps
            if is_trap(superdata, neighbor):
                continue
            
            # Build new path
            new_path = path + [neighbor]
            
            #╔══════════════════════════════════════════════════════════════╗
            #║             KEY MECHANIC: TOGGLE SWITCH (OPTIMIZED)          ║
            #╚══════════════════════════════════════════════════════════════╝
            
            new_gate_opened = gate_opened  # Inherit current state
            new_key_toggle_count = key_toggle_count
            
            # Check if stepping on key position
            if key_pos and (neighbor[0], neighbor[1]) == (key_pos[0], key_pos[1]):
                # TOGGLE gate state every time player touches key
                new_gate_opened = not gate_opened
                new_key_toggle_count += 1
                
                # Debug output (only for first few steps)
                if count_steps <= 50:
                    old_state = "OPEN" if gate_opened else "CLOSED"
                    new_state = "OPEN" if new_gate_opened else "CLOSED"
                    print(f"🔑 Step {len(new_path)}: Key touched at {neighbor} → Gate:  {old_state} → {new_state}")
            
            #──────────────────────────────────────────────────────────────────
            #              ENEMY MOVEMENT SIMULATION
            #──────────────────────────────────────────────────────────────────
            
            # Enemies see the NEW gate state (after toggle)
            new_zombie_positions = generate_next_zombie_positions(
                map_data=map_data,
                current_zombie_positions=zombie_list,
                current_player_position=neighbor,
                gate_opened=new_gate_opened,
                superdata=superdata
            )
            
            new_scorpion_positions = generate_next_scorpion_positions(
                map_data=map_data,
                current_scorpion_positions=scorpion_list,
                current_player_position=neighbor,
                gate_opened=new_gate_opened,
                superdata=superdata
            )
            
            # Handle enemy collisions and trap deaths
            new_zombie_positions, new_scorpion_positions = check_same_pos(
                new_zombie_positions,
                new_scorpion_positions,
                superdata
            )
            
            #──────────────────────────────────────────────────────────────────
            #              GOAL CHECK (WITH OPTIMIZATION)
            #──────────────────────────────────────────────────────────────────
            
            if neighbor == goal:
                if not is_lose(superdata, neighbor, new_zombie_positions, new_scorpion_positions):
                    # Calculate solution score
                    solution_score = len(new_path) + new_key_toggle_count * KEY_TOGGLE_PENALTY
                    
                    # Update best solution if this is better
                    if solution_score < best_score:
                        best_solution = new_path
                        best_score = solution_score
                        
                        print(f"")
                        print(f"╔═══════════════════════════════════════════════════════════════╗")
                        print(f"║          ✅ BETTER PATH FOUND!  (Score: {solution_score})              ║")
                        print(f"╚═══════════════════════════════════════════════════════════════╝")
                        print(f"  • Path length:       {len(new_path)} steps")
                        print(f"  • Key toggles:      {new_key_toggle_count} times")
                        print(f"  • Final gate state: {'OPEN' if new_gate_opened else 'CLOSED'}")
                        print(f"")
                    
                    # Continue searching for even better paths
                    continue
            
            #──────────────────────────────────────────────────────────────────
            #              STATE TRACKING
            #─────────────────────────────────────────────���────────────────────
            
            new_state = (
                neighbor,
                new_gate_opened,
                tuple(new_zombie_positions),
                tuple(new_scorpion_positions)
            )
            
            if new_state not in visited:
                visited.add(new_state)
                queue. append([
                    new_path,
                    new_gate_opened,
                    new_zombie_positions,
                    new_scorpion_positions,
                    new_key_toggle_count
                ])
    
    #══════════════════════════════════════════════════════════════════════════
    #                    STEP 7: RETURN BEST SOLUTION
    #══════════════════════════════════════════════════════════════════════════
    
    if best_solution:
        # Count actual key touches in best path
        key_touches = 0
        if key_pos:
            for pos in best_solution:
                if (pos[0], pos[1]) == (key_pos[0], key_pos[1]):
                    key_touches += 1
        
        print(f"")
        print(f"╔═══════════════════════════════════════════════════════════════╗")
        print(f"║              ✅ OPTIMAL PATH FOUND - SUCCESS!                  ║")
        print(f"╚══════════════════════════════════════════════════════════════��╝")
        print(f"")
        print(f"  📊 Statistics:")
        print(f"     • BFS iterations:       {count_steps: ,}")
        print(f"     • States explored:    {states_explored:,}")
        print(f"     • Optimal path length: {len(best_solution)} steps")
        print(f"     • Key touched:        {key_touches} time(s)")
        print(f"     • Solution score:     {best_score}")
        print(f"")
        print(f"╔═══════════════════════════════════════════════════════════════╗")
        
        return best_solution
    
    #══════════════════════════════════════════════════════════════════════════
    #                    NO PATH FOUND
    #══════════════════════════════════════════════════════════════════════════
    
    print(f"")
    print(f"╔═══════════════════════════════════════════════════════════════╗")
    print(f"║              ❌ NO PATH FOUND - FAILURE                       ║")
    print(f"╚═══════════════════════════════════════════════════════════════╝")
    print(f"")
    print(f"  📊 Statistics:")
    print(f"     • BFS iterations:       {count_steps:,}")
    print(f"     • States explored:    {states_explored:,}")
    print(f"     • States in visited:  {len(visited):,}")
    print(f"     • Max path length:    {max_path_length}")
    print(f"")
    print(f"  🎮 Map Info:")
    print(f"     • Start:      {start}")
    print(f"     • Goal:     {goal}")
    print(f"     • Key pos:  {key_pos}")
    print(f"     • Gate pos: {gate_pos}")
    print(f"     • Zombies:  {len(zombie_positions)}")
    print(f"     • Scorpions: {len(scorpion_positions)}")
    print(f"")
    print(f"╔═══════════════════════════════════════════════════════════════╝")
    
    return []

if __name__ == "__main__": 
    import map_collection as maps
    #------------------ TESTING CODE ------------------#
    map_collection = maps.maps_collection

    print(Shortest_Path(map_collection[0]['map_data'], (2,5), (3,5), [(2,5,3)]))