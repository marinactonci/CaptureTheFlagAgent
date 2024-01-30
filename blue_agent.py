# Dominik Bedenic & Tonči Marinac

""" 
- The agent employs a comprehensive knowledge base to store critical information, including:
    - last_seen_enemy_position: Records the position where the enemy was last spotted.
    - enemy_flag_position: Stores the position of the enemy flag.
    - own_flag_position: Keeps track of the agent's own flag position.
    - movement_index: Used for efficient exploration of the grid.
    - hit_top and hit_bottom: Flags indicating whether the agent has checked the opposite top or bottom position on the map.
    - world: Represents the agent's visible world, mapped to the actual grid.

- Utilizes the get_enemy_direction method to calculate the direction where the agent last saw the enemy, enhancing accuracy when shooting.

- Implements breadth-first search for pathfinding:
    - Moves one agent from top to bottom and another from bottom to top.
    - If the agents detect the enemy flag in their visible world, they use pathfinding to capture the flag and return to their base.
    - One agent assumes a defensive role by orbiting around the flag when their own flag is visible. If the enemy seizes their flag, the agent shifts to an offensive stance, chasing and attempting to eliminate the enemy.

- Utilizes the detect_object_in_visible_world method to identify objects in the visible world, returning true or false based on the object's presence.

- Maintains distance between agents by assigning specific search patterns:
    - One agent searches from top to bottom.
    - The other agent searches from bottom to top.
"""

import random
from config import *
from collections import deque

class Agent:
    
    def __init__(self, color, index):
        self.color = color 
        self.index = index 
        self.last_seen_enemy_position = None
        self.enemy_flag_position = None
        self.own_flag_position = None
        self.world = [[ASCII_TILES["unknown"] for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.movement_index = 0
        self.hit_top = False
        self.hit_bottom = False

    def update(self, visible_world, position, can_shoot, holding_flag):
        self.get_last_seen_enemy_position(visible_world, position)
        self.get_enemy_flag_position(visible_world, position)
        self.get_own_flag_position(visible_world, position)
        self.update_visible_world(visible_world, position)

        action, direction = self.agent_logic(visible_world, position, can_shoot, holding_flag)

        return action, direction
    

    def agent_logic(self, visible_world, position, can_shoot, holding_flag):
        enemy_in_sight = False

        if self.color == "blue":
            enemy_agent = ASCII_TILES["red_agent"]
            enemy_agent_f = ASCII_TILES["red_agent_f"]
            own_flag = ASCII_TILES["blue_flag"]
            enemy_flag = ASCII_TILES["red_flag"]
        elif self.color == "red":
            enemy_agent = ASCII_TILES["blue_agent"]
            enemy_agent_f = ASCII_TILES["blue_agent_f"]
            own_flag = ASCII_TILES["red_flag"]
            enemy_flag = ASCII_TILES["blue_flag"]

        for y in range(len(visible_world)):
            for x in range(len(visible_world[0])):
                if visible_world[y][x] in (enemy_agent, enemy_agent_f):
                    enemy_in_sight = True
                    break
            if enemy_in_sight:
                break

        if (enemy_in_sight and can_shoot):
            direction = self.get_enemy_direction(position)
            action = "shoot"
        else:
            action = "move"
            if (holding_flag):
                direction = self.move_towards_position(self.own_flag_position, position)
            else:
                if (self.enemy_flag_position and self.detect_object_in_visible_world(visible_world, enemy_flag)):
                    direction = self.move_towards_position(self.enemy_flag_position, position)
                else:
                    if (self.color == "blue"):
                        if (self.index == 0):
                            if (self.hit_top == False):
                                direction = self.move_towards_position((WIDTH-1, 1), position)
                            if (position == (WIDTH-1, 1) or self.world[1][WIDTH-1] == ASCII_TILES["wall"]):
                                self.hit_top = True
                            if (self.hit_top and self.hit_bottom == False):
                                direction = self.move_towards_position((WIDTH-1, HEIGHT-1), position)
                                if (position == (WIDTH-1, HEIGHT-1) or self.world[HEIGHT-1][WIDTH-1] == ASCII_TILES["wall"]):
                                    self.hit_bottom = True
                            if (self.hit_bottom and self.hit_top):
                                direction = self.move_towards_position(self.own_flag_position, position)
                        if (self.index == 1):
                            if (self.hit_bottom == False):
                                direction = self.move_towards_position((WIDTH-1, HEIGHT-1), position)
                                if (position == (WIDTH-1, HEIGHT-1) or self.world[HEIGHT-1][WIDTH-1] == ASCII_TILES["wall"]):
                                    self.hit_bottom = True
                            if (self.hit_bottom and self.hit_top == False):
                                direction = self.move_towards_position((WIDTH-1, 1), position)
                                if (position == (WIDTH-1, 1) or self.world[1][WIDTH-1] == ASCII_TILES["wall"]):
                                    self.hit_top = True
                            if (self.hit_top and self.hit_bottom):
                                direction = self.move_towards_position(self.own_flag_position, position)
                        if (self.index == 2):
                            if (self.detect_object_in_visible_world(visible_world, own_flag)):
                                direction = self.orbit_own_flag(position)
                            else:
                                if (self.hit_bottom == False):
                                    direction = self.move_towards_position((WIDTH-1, HEIGHT-1), position)
                                    if (position == (WIDTH-1, HEIGHT-1) or self.world[HEIGHT-1][WIDTH-1] == ASCII_TILES["wall"]):
                                        self.hit_bottom = True
                                if (self.hit_bottom and self.hit_top == False):
                                    direction = self.move_towards_position((WIDTH-1, 1), position)
                                    if (position == (WIDTH-1, 1) or self.world[1][WIDTH-1] == ASCII_TILES["wall"]):
                                        self.hit_top = True
                                if (self.hit_top and self.hit_bottom):
                                    direction = self.move_towards_position(self.own_flag_position, position)
                    else:
                        if (self.index == 0):
                            if (self.hit_top == False):
                                direction = self.move_towards_position((3, 3), position)
                            if (position == (3, 3) or self.world[3][3] == ASCII_TILES["wall"]):
                                self.hit_top = True
                            if (self.hit_top and self.hit_bottom == False):
                                direction = self.move_towards_position((1, HEIGHT-1), position)
                                if (position == (1, HEIGHT-1) or self.world[HEIGHT-1][1] == ASCII_TILES["wall"]):
                                    self.hit_bottom = True
                            if (self.hit_bottom and self.hit_top):
                                direction = self.move_towards_position(self.own_flag_position, position)
                        if (self.index == 1):
                            if (self.hit_bottom == False):
                                direction = self.move_towards_position((1, HEIGHT-1), position)
                                if (position == (1, HEIGHT-1) or self.world[HEIGHT-1][1] == ASCII_TILES["wall"]):
                                    self.hit_bottom = True
                            if (self.hit_bottom and self.hit_top == False):
                                direction = self.move_towards_position((3, 3), position)
                                if (position == (3, 3) or self.world[3][3] == ASCII_TILES["wall"]):
                                    self.hit_top = True
                            if (self.hit_top and self.hit_bottom):
                                direction = self.move_towards_position(self.own_flag_position, position)
                        if (self.index == 2):
                            if (self.detect_object_in_visible_world(visible_world, own_flag)):
                                direction = self.orbit_own_flag(position)
                            else:
                                if (self.hit_bottom == False):
                                    direction = self.move_towards_position((1, HEIGHT-1), position)
                                    if (position == (1, HEIGHT-1) or self.world[HEIGHT-1][1] == ASCII_TILES["wall"]):
                                        self.hit_bottom = True
                                if (self.hit_bottom and self.hit_top == False):
                                    direction = self.move_towards_position((3, 3), position)
                                    if (position == (3, 3) or self.world[3][3] == ASCII_TILES["wall"]):
                                        self.hit_top = True
                                if (self.hit_top and self.hit_bottom):
                                    direction = self.move_towards_position(self.own_flag_position, position)

        return action, direction
    
    def detect_object_in_visible_world(self, visible_world, object):
        for y in range(len(visible_world)):
            for x in range(len(visible_world[0])):
                if visible_world[y][x] == object:
                    return True
        return False
    
    def orbit_own_flag(self, position):
        own_flag_x, own_flag_y = self.own_flag_position
        orbit_positions = [
            (own_flag_x + 1, own_flag_y),  # Right
            (own_flag_x - 1, own_flag_y),  # Left
            (own_flag_x, own_flag_y + 1),  # Down
            (own_flag_x, own_flag_y - 1),  # Up
            (own_flag_x + 1, own_flag_y + 1),  # Diagonal down-right
            (own_flag_x - 1, own_flag_y - 1),  # Diagonal up-left
            (own_flag_x + 1, own_flag_y - 1),  # Diagonal up-right
            (own_flag_x - 1, own_flag_y + 1),  # Diagonal down-left
        ]

        if (position == orbit_positions[0]):
            return "up"
        elif (position == orbit_positions[1]):
            return "down"
        elif (position == orbit_positions[2]):
            return "right"
        elif (position == orbit_positions[3]):
            return "left"
        elif (position == orbit_positions[4]):
            return "up"
        elif (position == orbit_positions[5]):
            return "down"
        elif (position == orbit_positions[6]):
            return "left"
        elif (position == orbit_positions[7]):
            return "right"
        else:
            return self.move_towards_position(orbit_positions[0], position)
        

    def update_visible_world(self, visible_world, position):
        for y in range(len(visible_world)):
            for x in range(len(visible_world[0])):
                if visible_world[y][x] != ASCII_TILES["unknown"]:
                    self.world[position[1] + (y - 4)][position[0] + (x - 4)] = visible_world[y][x]
        

    def get_last_seen_enemy_position(self, visible_world, position):
        if self.color == "blue":
            enemy_agent = ASCII_TILES["red_agent"]
            enemy_agent_f = ASCII_TILES["red_agent_f"]
        else:
            enemy_agent = ASCII_TILES["blue_agent"]
            enemy_agent_f = ASCII_TILES["blue_agent_f"]

        for y in range(len(visible_world)):
            for x in range(len(visible_world[0])):
                if visible_world[y][x] in (enemy_agent, enemy_agent_f):
                    local_last_seen_enemy_position = (x, y)
                    self.last_seen_enemy_position = (position[0] + (local_last_seen_enemy_position[0] - 4, local_last_seen_enemy_position[1] - 4)[0], position[1] + (local_last_seen_enemy_position[0] - 4, local_last_seen_enemy_position[1] - 4)[1])
                    break
    

    def get_enemy_flag_position(self, visible_world, position):
        if self.color == "blue":
            enemy_flag = ASCII_TILES["red_flag"]
        else:
            enemy_flag = ASCII_TILES["blue_flag"]

        for y in range(len(visible_world)):
            for x in range(len(visible_world[0])):
                if visible_world[y][x] == enemy_flag:
                    local_enemy_flag_position = (x, y)
                    self.enemy_flag_position = (position[0] + (local_enemy_flag_position[0] - 4, local_enemy_flag_position[1] - 4)[0], position[1] + (local_enemy_flag_position[0] - 4, local_enemy_flag_position[1] - 4)[1])
                    break
        

    def get_own_flag_position(self, visible_world, position):
            if self.color == "blue":
                own_flag = ASCII_TILES["blue_flag"]
            else:
                own_flag = ASCII_TILES["red_flag"]

            for y in range(len(visible_world)):
                for x in range(len(visible_world[0])):
                    if visible_world[y][x] == own_flag:
                        local_own_flag_position = (x, y)
                        self.own_flag_position = (position[0] + (local_own_flag_position[0] - 4, local_own_flag_position[1] - 4)[0], position[1] + (local_own_flag_position[0] - 4, local_own_flag_position[1] - 4)[1])
                        break


    def move_towards_position(self, target, position):
        current_x, current_y = position
        path = self.breadth_first_search((current_x, current_y), target)

        if path:
            next_x, next_y = path[0]
            if next_x > current_x:
                return "right"
            elif next_x < current_x:
                return "left"
            elif next_y > current_y:
                return "down"
            elif next_y < current_y:
                return "up"


    def breadth_first_search(self, start, goal):
        queue = deque([(start, [])])
        visited = set()

        while queue:
            current, path = queue.popleft()
            x, y = current

            if current == goal:
                return path

            if 0 <= x < WIDTH and 0 <= y < HEIGHT and self.world[y][x] != ASCII_TILES["wall"] and current not in visited:
                visited.add(current)
                queue.extend([(neighbor, path + [neighbor]) for neighbor in self.get_neighbors(current)])

        return []


    def get_neighbors(self, position):
        x, y = position
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]


    def get_enemy_direction(self, position):
        enemy_x, enemy_y = self.last_seen_enemy_position

        if position[0] < enemy_x:
            return "right"
        elif position[0] > enemy_x:
            return "left"
        elif position[1] < enemy_y:
            return "down"
        elif position[1] > enemy_y:
            return "up"
        else:
            return random.choice(["left", "right", "up", "down"])


    def terminate(self, reason):
        if reason == "died":
            print(self.color, self.index, "died")

            