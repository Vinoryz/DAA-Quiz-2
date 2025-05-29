# pacman.py
import pygame
from grid import GRID_SIZE 

class PacMan:
    def __init__(self, start_pos_grid):
        self.grid_x, self.grid_y = start_pos_grid
        self.pixel_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.pixel_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        
        self.target_grid_x, self.target_grid_y = self.grid_x, self.grid_y
        self.pixel_target_x = self.pixel_x
        self.pixel_target_y = self.pixel_y
        
        self.N_FRAMES_PER_CELL = 8 
        self.speed = GRID_SIZE / self.N_FRAMES_PER_CELL
        if self.speed <= 0: self.speed = 1 

        self.current_dx_normalized = 0 
        self.current_dy_normalized = 0 
        self.is_moving = False
        
        self.path = [] 
        self.radius = GRID_SIZE // 2 - 3 
        self.queued_direction = None 

    def set_target_direction(self, dx_grid, dy_grid, current_map):
        if self.is_moving:
            if dx_grid != -self.current_dx_normalized or dy_grid != -self.current_dy_normalized : # Jangan antri reverse langsung
                 self.queued_direction = (dx_grid, dy_grid)
            return False 

        next_potential_grid_x = self.grid_x + dx_grid
        next_potential_grid_y = self.grid_y + dy_grid

        rows = len(current_map)
        cols = len(current_map[0])

        if 0 <= next_potential_grid_x < cols and \
           0 <= next_potential_grid_y < rows and \
           current_map[next_potential_grid_y][next_potential_grid_x] != 1:
            
            self.target_grid_x = next_potential_grid_x
            self.target_grid_y = next_potential_grid_y
            
            self.pixel_target_x = self.target_grid_x * GRID_SIZE + GRID_SIZE // 2
            self.pixel_target_y = self.target_grid_y * GRID_SIZE + GRID_SIZE // 2

            self.current_dx_normalized = dx_grid
            self.current_dy_normalized = dy_grid
            self.is_moving = True
            self.queued_direction = None 
            return True 
        return False

    def _apply_queued_direction(self, current_map):
        if self.queued_direction:
            dx, dy = self.queued_direction
            self.queued_direction = None 
            self.set_target_direction(dx, dy, current_map)


    def update(self, current_map):
        if not self.is_moving:
            self._apply_queued_direction(current_map)
            if not self.is_moving and self.path:
                if self.grid_x == self.target_grid_x and self.grid_y == self.target_grid_y: 
                    if self.path: 
                        next_target_grid_cell = self.path.pop(0)
                        dx_grid = next_target_grid_cell[0] - self.grid_x
                        dy_grid = next_target_grid_cell[1] - self.grid_y
                        self.set_target_direction(dx_grid, dy_grid, current_map)
            
            if not self.is_moving: 
                return False

        if self.is_moving:
            self.pixel_x += self.current_dx_normalized * self.speed
            self.pixel_y += self.current_dy_normalized * self.speed

            target_reached_this_frame = False
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
                
                self._apply_queued_direction(current_map)
                return True 
        
        return False

    def draw(self, win):
        pygame.draw.circle(win, (255, 255, 0), (int(self.pixel_x), int(self.pixel_y)), self.radius)

    def get_bounding_box(self):
        return pygame.Rect(self.pixel_x - self.radius, 
                           self.pixel_y - self.radius, 
                           2 * self.radius, 
                           2 * self.radius)
