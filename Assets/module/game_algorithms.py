from collections import deque
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

def is_linked(map_data: list, direction: list, facing_direction: str) -> bool: #check if have walls on the way
        
    x = direction[0]
    y = direction[1]
    if facing_direction == UP: #up
        return (y-1 > 0) and (map_data[y-1][x-1] not in ['t', 'tl','tr','b*','l*','r*']) and (map_data[y-2][x-1] not in ['b','bl','br','t*','l*','r*'])
    if facing_direction == DOWN: #down
        return (y+1 <= len(map_data[0])) and (map_data[y-1][x-1] not in ['b','bl','br','t*','l*','r*']) and (map_data[y][x-1] not in ['t', 'tl','tr','b*','l*','r*'])
    if facing_direction == LEFT: #left
        return (x-1 > 0) and (map_data[y-1][x-1] not in ['l', 'tl','bl','b*','t*','r*']) and (map_data[y-1][x-2] not in ['r','br','tr','t*','l*','b*'])
    if facing_direction == RIGHT: #right
        return (x+1 <= len(map_data[0])) and (map_data[y-1][x-1] not in ['r','br','tr','t*','l*','b*']) and (map_data[y-1][x] not in ['l', 'tl','bl','b*','t*','r*'])
    return True

def generate_graph(map_data: list) -> dict: #Generate graph from map data to use in pathfinding algorithms

    graph = {}

    for col_index, col in enumerate(map_data):
        for row_index, value in enumerate(col):  #row_index is x, col_index is y
            position = (row_index + 1, col_index + 1)
            graph[position] = []
            if is_linked(map_data, position, UP):
                graph[position].append((row_index + 1, col_index ))  # Up
            if is_linked(map_data, position, DOWN):
                graph[position].append((row_index + 1, col_index + 2))  # Down
            if is_linked(map_data, position, LEFT):
                graph[position].append((row_index , col_index + 1))  # Left
            if is_linked(map_data, position, RIGHT):
                graph[position].append((row_index + 2, col_index + 1))  # Right
    
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

def is_lose(zombie_list: list, player_position: tuple) -> bool:
    for zombie_info in zombie_list:
        zombie_position = (zombie_info[0], zombie_info[1])
        if player_position == zombie_position:
            return True
    return False

def generate_next_zombie_positions(map_data: list = [], current_zombie_positions: list = [], current_player_position: tuple = (), show_list: bool = False) -> list:

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
                if new_pos != zombie_pos:
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
                    if new_pos != zombie_pos:
                        move_list.append(move_dir)

            # Update the position for the next iteration of the loop
            zombie_pos = new_pos

        if move_list == []: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
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
                if new_pos != zombie_pos:
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
                    if new_pos != zombie_pos:
                        move_list.append(move_dir)

            # Update position for next iteration
            zombie_pos = new_pos

        if move_list == []: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
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
                    move_list.append(move_dir)
                else:
                    # 1.2 [SMART FALLBACK] Blocked Vertically -> Try Horizontal immediately
                    # Instead of breaking, check if we can slide Left/Right
                    h_dir, h_dx, h_dy = get_horizontal_direction(z_x, p_x)
                    
                    if h_dir is not None:
                        new_pos = try_move(map_data, zombie_pos, h_dir, h_dx, h_dy)
                        if new_pos != zombie_pos:
                            move_list.append(move_dir)
                    
                    # Note: If new_pos is still equal to zombie_pos here, 
                    # it means both Vertical and Horizontal were blocked (or aligned).
                    # The zombie stands still (does not reverse/turn back).

            # CASE 2: Already on Same Row (Only Horizontal option)
            else:
                move_dir, dx, dy = get_horizontal_direction(z_x, p_x)
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                    if new_pos != zombie_pos:
                        move_list.append(move_dir)

            # Update position
            zombie_pos = new_pos

        if move_list == []: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
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
                    move_list.append(move_dir)

                else:
                    # 1.2 [SMART FALLBACK] Blocked Horizontally -> Try Vertical immediately
                    v_dir, v_dx, v_dy = get_vertical_direction(z_y, p_y)
                    
                    if v_dir is not None:
                        new_pos = try_move(map_data, zombie_pos, v_dir, v_dx, v_dy)
                        if new_pos != zombie_pos:
                            move_list.append(move_dir)

            # CASE 2: Already on Same Column (Only Vertical option)
            else:
                move_dir, dx, dy = get_vertical_direction(z_y, p_y)
                if move_dir is not None:
                    new_pos = try_move(map_data, zombie_pos, move_dir, dx, dy)
                    if new_pos != zombie_pos:
                        move_list.append(move_dir)

            # Update position for next iteration
            zombie_pos = new_pos

        if move_list == []: #if zombie can't move -> chèn hướng để có hiệu ứng chạy tại chỗ
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
        print("Current Zombie Info:", zombie_info)
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
                print(generate_type_3(map_data, current_zombie_position, current_player_position, show_list=show_list))
        else: print(zombie_type)
    if show_list == False:
        return next_zombie_pos
    else:
        return move_list

def Shortest_Path(map_data: list, zombie_positions: list, start: tuple, goal: tuple) -> list: #include zombie position

    #----- STEP 1: INITIALIZE GRAPH AND VARIABLES  -----#
    graph = generate_graph(map_data) #generate graph from map data to use in pathfinding algorithms

    if start == goal: # check if start is goal
        return [start] if is_lose(zombie_positions, start) == False else []
    
    visited = set()
    visited.add(start)
    path = deque([[[start],zombie_positions]]) ## [[ [path], [zombie positions] ],[],[],...]

    #-------------------------------------#
    #----- BFS TO FIND SHORTEST PATH -----#
    #-------------------------------------#
    while path:
        current_path = path.popleft() # current_path = [ [path], [zombie positions] ]
        player_path = current_path[0]  # [ (x1,y1), (x2,y2), ... ]
        zombie_list = current_path[1] #[(x,y,k),...] k: type of zombie (0,1,2,3); (x,y): position of zombie

        #-------------------------------------------------------#
        #----- STEP 2: CHECK IF PLAYER IS CAUGHT BY ZOMBIE -----#
        #-------------------------------------------------------#
        player_died = is_lose(zombie_list, player_path[-1])
        
        #----- Step 2.1: if player is not caught by any zombie -----#
        if not player_died:  

            #-------------------------------------------------------------------------------#
            #----- STEP 3: GENERATE NEXT POSSIBLE POSITIONS FOR EACH ZOMBIE AND PLAYER -----#
            #-------------------------------------------------------------------------------#

            #----- Step 3.1: Generate next position for zombie for each type of zombie -----#
            # new_zombie_positions = generate_next_zombie_positions(map_data, zombie_list)

            #----- Step 3.2: Generate next possible positions for player -----#
            for neighbor in graph[player_path[-1]]: # neighbor is the next possible position of player

                if neighbor == goal:
                    #----- STEP 4: RETURN PATH IF GOAL IS REACHED -----#
                    return player_path + [neighbor], generate_next_zombie_positions(map_data, zombie_list, neighbor)
                
                else:

                    #----- STEP 5: ADD NEW POSITION TO PATH QUEUE -----#
                    path.append([player_path + [neighbor], generate_next_zombie_positions(map_data, zombie_list, neighbor)])

        else: None # Do nothing if player is caught by zombie in this case

    return [] # No path found


if __name__ == "__main__":
    import map_collection as maps
    #------------------ TESTING CODE ------------------#
    map_collection = maps.maps_collection

    print(Shortest_Path(map_collection[0]['map_data'], [(2,5,3)], (3,5), (5,5)))
    # print(is_linked(map_collection[0]['map_data'], (2,2), UP))