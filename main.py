import pygame
import random
import copy
from collections import deque
from grid import draw_grid, GRID_SIZE, ROWS, COLS
from pacman import PacMan
from algorithms import bfs, dfs
from ghost import Ghost, GHOST_COLORS, get_ghost_spawn_points
from maze_generator import generate_maze

pygame.init()
WIDTH, HEIGHT = GRID_SIZE * COLS, GRID_SIZE * ROWS
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Algo Master")

FPS = 60
game_clock = pygame.time.Clock()

# --- Game States ---
STATE_START_SCREEN = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_WIN_SCREEN = 3
current_game_state = STATE_START_SCREEN

# --- Score Variables ---
current_score = 0
high_score = 0
HIGH_SCORE_FILE = "highscore.txt"

# --- Font Initialization ---
try:
    FONT_TITLE = pygame.font.SysFont('arial', 60, bold=True)
    FONT_BUTTON = pygame.font.SysFont('arial', 35)
    FONT_SCORE = pygame.font.SysFont('arial', 28)
    FONT_SMALL = pygame.font.SysFont('arial', 20)
except pygame.error:
    FONT_TITLE = pygame.font.Font(None, 70)
    FONT_BUTTON = pygame.font.Font(None, 45)
    FONT_SCORE = pygame.font.Font(None, 38)
    FONT_SMALL = pygame.font.Font(None, 28)

# --- Game Elements ---
pacman = None
ghosts = []
game_MAP = []
game_START_POS = (0, 0)
mode = "manual"
visited_path_nodes = set()
targeted_food_coord = None

NUM_GHOSTS = 5
win_buttons = {"next_level": None, "menu": None}

# --- Helper Functions ---

def load_high_score():
    global high_score
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            content = f.read().strip()
            if content:
                high_score = int(content)
            else:
                high_score = 0
    except (FileNotFoundError, ValueError):
        high_score = 0

def save_high_score():
    global high_score
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(high_score))
    except IOError:
        print(f"Error: Gagal menyimpan skor tertinggi ke {HIGH_SCORE_FILE}")

load_high_score()

def draw_text_button(surface, text, position, font, text_color=(255, 255, 255), rect_color=None, rect_padding=(15, 8), center_align=True):
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    if center_align:
        text_rect.center = position
    else:
        text_rect.topleft = position

    button_rect_inflated = text_rect.inflate(rect_padding[0] * 2, rect_padding[1] * 2)
    if rect_color:
        pygame.draw.rect(surface, rect_color, button_rect_inflated, border_radius=5)

    surface.blit(text_surface, text_rect)
    return button_rect_inflated

# --- Screen Drawing Functions ---
def draw_start_screen(surface):
    global high_score
    surface.fill((10, 10, 30))
    logo_text_surf = FONT_TITLE.render("PAC-MAN ALGO MASTER", True, (255, 255, 0))
    logo_rect = logo_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4 - 20))
    surface.blit(logo_text_surf, logo_rect)

    start_btn_rect = draw_text_button(surface, "START GAME (Enter)", (WIDTH // 2, HEIGHT // 2 - 20), FONT_BUTTON,
                                     rect_color=(0, 100, 0))
    quit_btn_rect = draw_text_button(surface, "QUIT (Esc)", (WIDTH // 2, HEIGHT // 2 + 50), FONT_BUTTON,
                                    rect_color=(100, 0, 0))

    hs_text_surf = FONT_SCORE.render(f"Highest Score: {high_score}", True, (255, 255, 0))
    hs_rect = hs_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130))
    surface.blit(hs_text_surf, hs_rect)

    controls_surf = FONT_SMALL.render("Controls: Arrow Keys/WASD | Q: BFS | E: DFS | N: Next Level | M: Menu", True,
                                     (180, 180, 180))
    controls_rect = controls_surf.get_rect(center=(WIDTH // 2, HEIGHT - 60))
    surface.blit(controls_surf, controls_rect)
    return start_btn_rect, quit_btn_rect

def draw_game_over_screen(surface):
    global current_score, high_score
    surface.fill((30, 10, 10))
    go_text_surf = FONT_TITLE.render("GAME OVER", True, (255, 60, 60))
    go_rect = go_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    surface.blit(go_text_surf, go_rect)

    score_surf = FONT_SCORE.render(f"Your Score: {current_score}", True, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(score_surf, score_rect)

    hs_surf = FONT_SCORE.render(f"Highest Score: {high_score}", True, (255, 255, 0))
    hs_rect = hs_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 0))
    surface.blit(hs_surf, hs_rect)

    restart_btn_rect = draw_text_button(surface, "Play Again (R)", (WIDTH // 2, HEIGHT // 2 + 70), FONT_BUTTON,
                                       rect_color=(0, 80, 0))
    menu_btn_rect = draw_text_button(surface, "Main Menu (M)", (WIDTH // 2, HEIGHT // 2 + 140), FONT_BUTTON,
                                    rect_color=(80, 80, 0))
    return restart_btn_rect, menu_btn_rect

def draw_playing_hud(surface):
    global current_score, high_score
    score_text_surf = FONT_SCORE.render(f"Score: {current_score}", True, (255, 255, 255))
    surface.blit(score_text_surf, (15, 10))

    hs_text_surf = FONT_SCORE.render(f"High: {high_score}", True, (255, 255, 0))
    hs_rect = hs_text_surf.get_rect(topright=(WIDTH - 15, 10))
    surface.blit(hs_text_surf, hs_rect)

def draw_win_screen(surface):
    surface.fill((10, 30, 10))
    win_text_surf = FONT_TITLE.render("YOU WIN!", True, (0, 255, 0))
    win_rect = win_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    surface.blit(win_text_surf, win_rect)

    restart_btn_rect = draw_text_button(surface, "Next Level (More Ghosts)", (WIDTH // 2, HEIGHT // 2 - 10), FONT_BUTTON,
                                       rect_color=(0, 120, 0))
    menu_btn_rect = draw_text_button(surface, "Main Menu", (WIDTH // 2, HEIGHT // 2 + 60), FONT_BUTTON,
                                    rect_color=(80, 80, 0))

    return restart_btn_rect, menu_btn_rect

def is_food_left(game_map):
    for row in game_map:
        if 2 in row:
            return True
    return False

# --- BFS distance map from ghost positions ---
def bfs_distance_map(start_pos, maze):
    rows, cols = len(maze), len(maze[0])
    dist = [[-1]*cols for _ in range(rows)]
    queue = deque()
    sx, sy = start_pos
    dist[sy][sx] = 0
    queue.append((sx, sy))

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if maze[ny][nx] != 1 and dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    queue.append((nx, ny))
    return dist

# --- Combined ghost distance map ---
def combined_ghost_distance_map(ghosts, maze):
    rows, cols = len(maze), len(maze[0])
    combined = [[float('inf')] * cols for _ in range(rows)]

    for ghost in ghosts:
        gx, gy = ghost.get_grid_position()
        dist_map = bfs_distance_map((gx, gy), maze)
        for y in range(rows):
            for x in range(cols):
                if dist_map[y][x] != -1:
                    combined[y][x] = min(combined[y][x], dist_map[y][x])
    return combined

# --- Predictive pathfinding: safest path to food ---
def is_food_safe(food_pos, ghosts):
    x, y = food_pos
    neighbors = [(x-2, y), (x+2, y), (x, y-2), (x, y+2)]
    for ghost in ghosts:
        gx, gy = ghost.get_grid_position()
        if (gx, gy) in neighbors:
            return False
    return True

def find_safest_food_path(start_grid_pos):
    global mode, game_MAP, ghosts
    algo_func = bfs if mode == "bfs" else dfs

    map_with_ghosts = copy.deepcopy(game_MAP)
    for ghost in ghosts:
        gx, gy = ghost.get_grid_position()
        map_with_ghosts[gy][gx] = 1

    ghost_dist_map = combined_ghost_distance_map(ghosts, game_MAP)

    rows, cols = len(game_MAP), len(game_MAP[0])
    food_positions = [(x, y) for y in range(rows) for x in range(cols) if game_MAP[y][x] == 2]

    best_path = []
    best_safety_score = -1

    for food_pos in food_positions:
        if not is_food_safe(food_pos, ghosts):
            continue  # skip unsafe food

        path, _ = algo_func(start_grid_pos, lambda x,y: (x,y) == food_pos, map_with_ghosts)
        if not path:
            continue

        safety_score = min(ghost_dist_map[y][x] for x,y in path)
        if safety_score > best_safety_score:
            best_safety_score = safety_score
            best_path = path

    return best_path

def initialize_game_elements():
    global pacman, ghosts, game_MAP, game_START_POS, visited_path_nodes, mode, current_score, targeted_food_coord, NUM_GHOSTS

    print("Initializing game elements...")
    game_MAP, game_START_POS = generate_maze(ROWS, COLS)

    # Ensure the start position is not a food tile
    start_x, start_y = game_START_POS
    if game_MAP[start_y][start_x] == 2:
        game_MAP[start_y][start_x] = 0

    pacman = PacMan(game_START_POS)

    ghosts.clear()
    ghost_spawn_positions = get_ghost_spawn_points(game_MAP, NUM_GHOSTS, game_START_POS)
    for i in range(NUM_GHOSTS):
        grid_pos = ghost_spawn_positions[i]
        color_idx = i % len(GHOST_COLORS)
        ghosts.append(Ghost(grid_pos, GHOST_COLORS[color_idx]))

    visited_path_nodes.clear()
    mode = "manual"
    current_score = 0
    targeted_food_coord = None


def game_controller():
    global current_game_state, run_game_flag, high_score, current_score
    global pacman, ghosts, game_MAP, mode, visited_path_nodes, targeted_food_coord, NUM_GHOSTS, win_buttons

    run_game_flag = True
    start_screen_buttons = {"start": None, "quit": None}
    game_over_buttons = {"restart": None, "menu": None}
    win_buttons = {"next_level": None, "menu": None}

    initialize_game_elements()
    current_game_state = STATE_START_SCREEN

    while run_game_flag:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_game_flag = False

            if current_game_state == STATE_START_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_screen_buttons["start"] and start_screen_buttons["start"].collidepoint(mouse_pos):
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif start_screen_buttons["quit"] and start_screen_buttons["quit"].collidepoint(mouse_pos):
                        run_game_flag = False
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        run_game_flag = False

            elif current_game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    dx_m, dy_m = 0, 0
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        dx_m = -1
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        dx_m = 1
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        dy_m = -1
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        dy_m = 1

                    if dx_m != 0 or dy_m != 0:
                        mode = "manual"
                        pacman.path = []
                        targeted_food_coord = None
                        pacman.set_target_direction(dx_m, dy_m, game_MAP)

                    elif event.key == pygame.K_q:  # BFS
                        mode = "bfs"
                        pacman.path = []
                        path_full = find_safest_food_path((pacman.grid_x, pacman.grid_y))
                        if path_full:
                            pacman.path = path_full[1:]
                            targeted_food_coord = path_full[-1]
                        else:
                            targeted_food_coord = None
                    elif event.key == pygame.K_e:  # DFS
                        mode = "dfs"
                        pacman.path = []
                        path_full = find_safest_food_path((pacman.grid_x, pacman.grid_y))
                        if path_full:
                            pacman.path = path_full[1:]
                            targeted_food_coord = path_full[-1]
                        else:
                            targeted_food_coord = None

            elif current_game_state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_over_buttons["restart"] and game_over_buttons["restart"].collidepoint(mouse_pos):
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif game_over_buttons["menu"] and game_over_buttons["menu"].collidepoint(mouse_pos):
                        current_game_state = STATE_START_SCREEN
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif event.key in [pygame.K_m, pygame.K_ESCAPE]:
                        current_game_state = STATE_START_SCREEN

            elif current_game_state == STATE_WIN_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if win_buttons["next_level"] and win_buttons["next_level"].collidepoint(mouse_pos):
                        NUM_GHOSTS += 1
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif win_buttons["menu"] and win_buttons["menu"].collidepoint(mouse_pos):
                        current_game_state = STATE_START_SCREEN
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        NUM_GHOSTS += 1
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif event.key == pygame.K_m:
                        current_game_state = STATE_START_SCREEN

        # --- Game Logic Update ---
        if current_game_state == STATE_PLAYING:
            pacman_reached_cell = pacman.update(game_MAP)
            for ghost in ghosts:
                ghost.update(game_MAP, (pacman.grid_x, pacman.grid_y))

            # Check collision with ghosts
            pacman_bb = pacman.get_bounding_box()
            for ghost in ghosts:
                if pacman_bb.colliderect(ghost.get_bounding_box()):
                    if current_score > high_score:
                        high_score = current_score
                        save_high_score()
                    current_game_state = STATE_GAME_OVER
                    targeted_food_coord = None
                    break
            if current_game_state == STATE_GAME_OVER:
                continue

            # Recalculate BFS/DFS path when Pac-Man reaches a new cell or path is empty
            if mode in ["bfs", "dfs"] and (not pacman.path or pacman_reached_cell):
                # Create a deep copy of the map and mark ghosts as walls
                map_with_ghosts = copy.deepcopy(game_MAP)
                for ghost in ghosts:
                    gx, gy = ghost.get_grid_position()
                    map_with_ghosts[gy][gx] = 1

                algo_func = bfs if mode == "bfs" else dfs
                path_full, visited_cells = algo_func(
                    (pacman.grid_x, pacman.grid_y),
                    lambda x, y: map_with_ghosts[y][x] == 2,
                    map_with_ghosts
                )

                visited_path_nodes.clear()
                visited_path_nodes.update(visited_cells)

                if path_full:
                    pacman.path = path_full[1:]
                    targeted_food_coord = path_full[-1]
                else:
                    pacman.path = []
                    targeted_food_coord = None

            # Eating food and scoring
            if pacman_reached_cell:
                cx, cy = pacman.grid_x, pacman.grid_y
                if game_MAP[cy][cx] == 2:
                    game_MAP[cy][cx] = 0
                    current_score += 10
                    if targeted_food_coord == (cx, cy):
                        targeted_food_coord = None

                    # Check win condition
                    if not is_food_left(game_MAP):
                        current_game_state = STATE_WIN_SCREEN

        # --- Drawing ---
        WIN.fill((10, 10, 10))
        if current_game_state == STATE_START_SCREEN:
            btn_s, btn_q = draw_start_screen(WIN)
            start_screen_buttons["start"], start_screen_buttons["quit"] = btn_s, btn_q
        elif current_game_state == STATE_PLAYING:
            draw_grid(WIN, visited_path_nodes, game_MAP, targeted_food_coord)
            if pacman:
                pacman.draw(WIN)
            for ghost in ghosts:
                ghost.draw(WIN)
            draw_playing_hud(WIN)
        elif current_game_state == STATE_GAME_OVER:
            btn_r, btn_m = draw_game_over_screen(WIN)
            game_over_buttons["restart"], game_over_buttons["menu"] = btn_r, btn_m
        elif current_game_state == STATE_WIN_SCREEN:
            btn_n, btn_m = draw_win_screen(WIN)
            win_buttons["next_level"], win_buttons["menu"] = btn_n, btn_m

        pygame.display.update()
        game_clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game_controller()
