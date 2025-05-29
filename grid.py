# grid.py
import pygame

GRID_SIZE = 40
ROWS, COLS = 15, 30

def draw_grid(win, visited_nodes, current_map_to_draw, current_targeted_food_coord):
    """Menggambar grid menggunakan peta yang diberikan dan menandai makanan target."""
    for y, row in enumerate(current_map_to_draw):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if tile == 1: 
                pygame.draw.rect(win, (0, 0, 200), rect) 
            elif tile == 2: 
                if current_targeted_food_coord == (x, y):
                    pygame.draw.circle(win, (255, 0, 0), rect.center, 7)
                else:
                    pygame.draw.circle(win, (255, 255, 0), rect.center, 5)
            
