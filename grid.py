# grid.py
import pygame

GRID_SIZE = 20
ROWS, COLS = 24, 32
WIDTH = GRID_SIZE * COLS
HEIGHT = GRID_SIZE * ROWS

def draw_grid(win, visited, game_map, target_food=None):
    for y, row in enumerate(game_map):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE)

            if tile == 1:
                pygame.draw.rect(win, (0,0,255), rect)
            elif tile == 2:
                color = (255,0,0) if (x,y) in visited else (255,255,0)
                pygame.draw.circle(win, color, rect.center, 5)
            else:
                pygame.draw.rect(win, (30,30,30), rect)

            if target_food == (x,y):
                pygame.draw.rect(win, (0,255,0), rect, 3)  # Highlight target food

