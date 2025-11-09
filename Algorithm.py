from collections import deque
import maps

UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

def is_linked(map_data, direction, facing_direction): #check if have walls on the way
        
    x = direction[0]
    y = direction[1]
    if facing_direction == UP:
        return (y-1 > 0) and (map_data[y-1][x-1] not in ['t', 'tl','tr','b*','l*','r*']) and (map_data[y-2][x-1] not in ['b','bl','br','t*','l*','r*'])
    if facing_direction == DOWN:
        return (y+1 <= len(map_data[0])) and (map_data[y-1][x-1] not in ['b','bl','br','t*','l*','r*']) and (map_data[y][x-1] not in ['t', 'tl','tr','b*','l*','r*'])
    if facing_direction == LEFT:
        return (x-1 > 0) and (map_data[y-1][x-1] not in ['l', 'tl','bl','b*','t*','r*']) and (map_data[y-1][x-2] not in ['r','br','tr','t*','l*','b*'])
    if facing_direction == RIGHT:
        return (x+1 <= len(map_data[0])) and (map_data[y-1][x-1] not in ['r','br','tr','t*','l*','b*']) and (map_data[y-1][x] not in ['l', 'tl','bl','b*','t*','r*'])
    return True

def generate_graph(map_data):

    graph = {}

    for col_index, col in enumerate(map_data):
        for row_index, value in enumerate(col):
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

def BFS(graph, start):
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

def DFS(graph, start):
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

def Shortest_Path(map_data,zombie_position, start, goal): #include zombie position
    graph = generate_graph(map_data)
    if start == goal:
        return [start]
    
    visited = set()
    visited.add(start)
    path = deque([[start],[zombie_position]])

    while path:
        current_path = path.popleft()
        if current_path[0][len(current_path[0]) - 1] != current_path[1]:
            print(current_path[0][len(current_path[0]) - 1], current_path[1][0])

            for neighbor in graph[current_path[0][len(current_path[0]) - 1]]:
                for face in [UP,DOWN,LEFT,RIGHT]:
                    if is_linked(map_data, current_path[1][0], face):
                        if neighbor == goal:
                            return [current_path + [neighbor], [current_path[1][0]]]
                        else:
                            if neighbor not in visited:
                                visited.add(neighbor)
                                path.append(current_path + [neighbor])

map_collection = maps.maps_collection
print(generate_graph(map_collection[0]['map_data']))
