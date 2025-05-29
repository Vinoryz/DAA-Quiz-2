# ghost.py
import pygame
import random
from grid import GRID_SIZE

GHOST_COLORS = [
    (255, 0, 0), (255, 184, 222), (0, 255, 255), (255, 184, 82),
    (100, 100, 255), (200, 0, 200)
]

class Ghost:
    def __init__(self, start_pos_grid, color):
        self.grid_x, self.grid_y = start_pos_grid
        self.pixel_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.pixel_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        
        self.target_grid_x, self.target_grid_y = self.grid_x, self.grid_y
        self.pixel_target_x = self.pixel_x
        self.pixel_target_y = self.pixel_y
        
        self.N_FRAMES_PER_CELL = 9 
        self.speed = GRID_SIZE / self.N_FRAMES_PER_CELL 
        if self.speed <= 0: self.speed = 1

        self.current_dx_normalized = 0
        self.current_dy_normalized = 0
        self.is_moving = False
        self.color = color
        self.radius = GRID_SIZE // 2 - 4 
        self.prev_move_delta_grid = None 

    def _set_target_from_delta(self, dx_grid, dy_grid):
        self.target_grid_x = self.grid_x + dx_grid
        self.target_grid_y = self.grid_y + dy_grid
        
        self.pixel_target_x = self.target_grid_x * GRID_SIZE + GRID_SIZE // 2
        self.pixel_target_y = self.target_grid_y * GRID_SIZE + GRID_SIZE // 2

        self.current_dx_normalized = dx_grid
        self.current_dy_normalized = dy_grid
        self.is_moving = True
        self.prev_move_delta_grid = (dx_grid, dy_grid) 


    def _choose_next_grid_move(self, current_map, pacman_pos_grid=None):
        possible_next_deltas = [] 

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] 
        random.shuffle(directions) 

        rows = len(current_map)
        cols = len(current_map[0])

        for dx, dy in directions:
            next_g_x, next_g_y = self.grid_x + dx, self.grid_y + dy
            if 0 <= next_g_x < cols and 0 <= next_g_y < rows and \
               current_map[next_g_y][next_g_x] != 1:
                possible_next_deltas.append((dx, dy))
        
        if not possible_next_deltas:
            return None

        if len(possible_next_deltas) > 1 and self.prev_move_delta_grid:
            reverse_move = (-self.prev_move_delta_grid[0], -self.prev_move_delta_grid[1])
            
            if reverse_move in possible_next_deltas:
                filtered_moves = [move for move in possible_next_deltas if move != reverse_move]
                if filtered_moves: 
                    return random.choice(filtered_moves)

        return random.choice(possible_next_deltas)


    def update(self, current_map, pacman_pos_grid=None): 
        if not self.is_moving:
            chosen_delta = self._choose_next_grid_move(current_map, pacman_pos_grid)
            if chosen_delta:
                self._set_target_from_delta(chosen_delta[0], chosen_delta[1])
            else: 
                return

        if self.is_moving:
            self.pixel_x += self.current_dx_normalized * self.speed
            self.pixel_y += self.current_dy_normalized * self.speed
            
            # Check X-axis
            if self.current_dx_normalized > 0 and self.pixel_x >= self.pixel_target_x:
                self.pixel_x = self.pixel_target_x
            elif self.current_dx_normalized < 0 and self.pixel_x <= self.pixel_target_x:
                self.pixel_x = self.pixel_target_x
            
            # Check Y-axis
            if self.current_dy_normalized > 0 and self.pixel_y >= self.pixel_target_y:
                self.pixel_y = self.pixel_target_y
            elif self.current_dy_normalized < 0 and self.pixel_y <= self.pixel_target_y:
                self.pixel_y = self.pixel_target_y

            if self.pixel_x == self.pixel_target_x and self.pixel_y == self.pixel_target_y:
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
                self.is_moving = False

    def draw(self, win):
        # Ghost Body
        body_rect_center_x = int(self.pixel_x)
        body_rect_center_y = int(self.pixel_y) - self.radius // 3 
        
        pygame.draw.circle(win, self.color, (body_rect_center_x, body_rect_center_y), self.radius)

        num_spikes = 3
        spike_width = (2 * self.radius) / (num_spikes * 2 -1) 
        spike_height = self.radius / 1.5

        for i in range(num_spikes):
            base_x_left = self.pixel_x - self.radius + (i * 2 * spike_width)
            base_x_right = base_x_left + spike_width
            tip_x = base_x_left + spike_width / 2
            
            base_y = self.pixel_y + self.radius / 2.5 
            tip_y = base_y + spike_height

            pygame.draw.polygon(win, self.color, [
                (base_x_left, base_y), (base_x_right, base_y), (tip_x, tip_y)
            ])
        
        eye_radius = self.radius // 4
        eye_offset_x = self.radius // 3
        eye_y = body_rect_center_y - self.radius // 5

        pygame.draw.circle(win, (255,255,255), (body_rect_center_x - eye_offset_x, eye_y), eye_radius)
        pygame.draw.circle(win, (255,255,255), (body_rect_center_x + eye_offset_x, eye_y), eye_radius)
        
        pupil_radius = eye_radius // 2
        pupil_look_dx = self.current_dx_normalized * pupil_radius * 0.5
        pupil_look_dy = self.current_dy_normalized * pupil_radius * 0.5
        
        pygame.draw.circle(win, (0,0,0), (int(body_rect_center_x - eye_offset_x + pupil_look_dx), int(eye_y + pupil_look_dy)), pupil_radius)
        pygame.draw.circle(win, (0,0,0), (int(body_rect_center_x + eye_offset_x + pupil_look_dx), int(eye_y + pupil_look_dy)), pupil_radius)


    def get_bounding_box(self):
        effective_radius = self.radius * 0.8 
        return pygame.Rect(self.pixel_x - effective_radius, 
                           self.pixel_y - effective_radius, 
                           2 * effective_radius, 
                           2 * effective_radius)
