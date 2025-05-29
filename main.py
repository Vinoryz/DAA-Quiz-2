# main.py
import pygame
import random
from grid import draw_grid, GRID_SIZE, ROWS, COLS
from pacman import PacMan
from algorithms import bfs, dfs 
from ghost import Ghost, GHOST_COLORS 
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

# --- Game Elements (akan diinisialisasi) ---
pacman = None
ghosts = []
game_MAP = [] 
game_START_POS = (0,0) 
mode = "manual" 
visited_path_nodes = set() 
targeted_food_coord = None 

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

def draw_text_button(surface, text, position, font, text_color=(255,255,255), rect_color=None, rect_padding=(15,8), center_align=True):
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    if center_align:
        text_rect.center = position
    else:
        text_rect.topleft = position
    
    button_rect_inflated = text_rect.inflate(rect_padding[0]*2, rect_padding[1]*2)
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

    start_btn_rect = draw_text_button(surface, "START GAME (Enter)", (WIDTH // 2, HEIGHT // 2 - 20), FONT_BUTTON, rect_color=(0,100,0))
    quit_btn_rect = draw_text_button(surface, "QUIT (Esc)", (WIDTH // 2, HEIGHT // 2 + 50), FONT_BUTTON, rect_color=(100,0,0))
    
    hs_text_surf = FONT_SCORE.render(f"Highest Score: {high_score}", True, (255, 255, 0))
    hs_rect = hs_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130))
    surface.blit(hs_text_surf, hs_rect)

    controls_surf = FONT_SMALL.render("Controls: Arrow Keys/WASD | Q: BFS | E: DFS", True, (180,180,180))
    controls_rect = controls_surf.get_rect(center=(WIDTH // 2, HEIGHT - 60))
    surface.blit(controls_surf, controls_rect)
    return start_btn_rect, quit_btn_rect

def draw_game_over_screen(surface):
    global current_score, high_score
    surface.fill((30, 10, 10))
    go_text_surf = FONT_TITLE.render("GAME OVER", True, (255, 60, 60))
    go_rect = go_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    surface.blit(go_text_surf, go_rect)

    score_surf = FONT_SCORE.render(f"Your Score: {current_score}", True, (255,255,255))
    score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(score_surf, score_rect)

    hs_surf = FONT_SCORE.render(f"Highest Score: {high_score}", True, (255,255,0))
    hs_rect = hs_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 0))
    surface.blit(hs_surf, hs_rect)
    
    restart_btn_rect = draw_text_button(surface, "Play Again (R)", (WIDTH // 2, HEIGHT // 2 + 70), FONT_BUTTON, rect_color=(0,80,0))
    menu_btn_rect = draw_text_button(surface, "Main Menu (M)", (WIDTH // 2, HEIGHT // 2 + 140), FONT_BUTTON, rect_color=(80,80,0))
    return restart_btn_rect, menu_btn_rect

def draw_playing_hud(surface):
    global current_score, high_score
    score_text_surf = FONT_SCORE.render(f"Score: {current_score}", True, (255,255,255))
    surface.blit(score_text_surf, (15, 10))

    hs_text_surf = FONT_SCORE.render(f"High: {high_score}", True, (255,255,0))
    hs_rect = hs_text_surf.get_rect(topright=(WIDTH - 15, 10))
    surface.blit(hs_text_surf, hs_rect)

# --- Game Logic Functions ---
NUM_GHOSTS = 5

def get_ghost_spawn_points(current_game_map, num_ghosts, pacman_grid_pos):
    possible_points = []
    for r_idx, row_val in enumerate(current_game_map):
        for c_idx, tile_val in enumerate(row_val):
            if tile_val == 0 and (c_idx, r_idx) != pacman_grid_pos:
                possible_points.append((c_idx, r_idx))
    random.shuffle(possible_points)
    spawn_points = possible_points[:min(num_ghosts, len(possible_points))]
    while len(spawn_points) < num_ghosts:
        if possible_points: spawn_points.append(random.choice(possible_points))
        else: spawn_points.append(pacman_grid_pos)
    return spawn_points

def initialize_game_elements():
    global pacman, ghosts, game_MAP, game_START_POS, visited_path_nodes, mode, current_score, targeted_food_coord
    
    print("Initializing game elements...")
    game_MAP, game_START_POS = generate_maze(ROWS, COLS) 
    
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

def find_nearest_food_path(start_grid_pos):
    global mode, visited_path_nodes, game_MAP 
    algo_func = None
    if mode == "bfs": algo_func = bfs
    elif mode == "dfs": algo_func = dfs
    
    if algo_func:
        path_to_food, visited_cells = algo_func(start_grid_pos, 
                                                lambda x, y: game_MAP[y][x] == 2, 
                                                game_MAP)
        return path_to_food 
    return []


# --- Main Game Controller ---
def game_controller():
    global current_game_state, run_game_flag, high_score, current_score, pacman, ghosts, game_MAP, mode, visited_path_nodes, targeted_food_coord

    run_game_flag = True
    start_screen_buttons = {"start": None, "quit": None}
    game_over_buttons = {"restart": None, "menu": None}

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
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        initialize_game_elements()
                        current_game_state = STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        run_game_flag = False
            
            elif current_game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    dx_m, dy_m = 0,0
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a: dx_m = -1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: dx_m = 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_w: dy_m = -1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s: dy_m = 1
                    
                    if dx_m != 0 or dy_m != 0: 
                        mode = "manual"
                        pacman.path = []
                        targeted_food_coord = None 
                        pacman.set_target_direction(dx_m, dy_m, game_MAP)

                    elif event.key == pygame.K_q: # BFS
                        mode = "bfs"
                        pacman.path = []
                        path_full = find_nearest_food_path((pacman.grid_x, pacman.grid_y))
                        if path_full: 
                            pacman.path = path_full[1:] 
                            targeted_food_coord = path_full[-1] # << SET TARGET FOOD
                        else:
                            targeted_food_coord = None 
                    elif event.key == pygame.K_e: # DFS
                        mode = "dfs"
                        pacman.path = []
                        path_full = find_nearest_food_path((pacman.grid_x, pacman.grid_y))
                        if path_full: 
                            pacman.path = path_full[1:]
                            targeted_food_coord = path_full[-1] # << SET TARGET FOOD
                        else:
                            targeted_food_coord = None 


            elif current_game_state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_over_buttons["restart"] and game_over_buttons["restart"].collidepoint(mouse_pos):
                        initialize_game_elements(); current_game_state = STATE_PLAYING
                    elif game_over_buttons["menu"] and game_over_buttons["menu"].collidepoint(mouse_pos):
                        current_game_state = STATE_START_SCREEN
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: initialize_game_elements(); current_game_state = STATE_PLAYING
                    elif event.key == pygame.K_m or event.key == pygame.K_ESCAPE: current_game_state = STATE_START_SCREEN
        
        # --- Game Logic Update ---
        if current_game_state == STATE_PLAYING:
            pacman_reached_cell = pacman.update(game_MAP)
            for ghost in ghosts: ghost.update(game_MAP, (pacman.grid_x, pacman.grid_y))

            pacman_bb = pacman.get_bounding_box()
            for ghost in ghosts:
                if pacman_bb.colliderect(ghost.get_bounding_box()):
                    if current_score > high_score:
                        high_score = current_score
                        save_high_score()
                    current_game_state = STATE_GAME_OVER
                    targeted_food_coord = None 
                    break 
            if current_game_state == STATE_GAME_OVER: continue 
            
            if pacman_reached_cell:
                current_cell_x, current_cell_y = pacman.grid_x, pacman.grid_y
                if game_MAP[current_cell_y][current_cell_x] == 2:
                    game_MAP[current_cell_y][current_cell_x] = 0 
                    current_score += 10
                    
                    if targeted_food_coord == (current_cell_x, current_cell_y): # Jika makanan target dimakan
                        targeted_food_coord = None
                        # print("Targeted food eaten") # Debug
                    
                    if mode in ["bfs", "dfs"] and not pacman.is_moving and not pacman.path:
                        path_full = find_nearest_food_path((pacman.grid_x, pacman.grid_y))
                        if path_full: 
                            pacman.path = path_full[1:]
                            targeted_food_coord = path_full[-1] # << SET TARGET FOOD BARU
                        else: 
                            # print("No more food or path!") # Debug
                            targeted_food_coord = None 
        
        # --- Drawing ---
        WIN.fill((10,10,10)) 
        if current_game_state == STATE_START_SCREEN:
            btn_s, btn_q = draw_start_screen(WIN)
            start_screen_buttons["start"], start_screen_buttons["quit"] = btn_s, btn_q
        elif current_game_state == STATE_PLAYING:
            draw_grid(WIN, visited_path_nodes, game_MAP, targeted_food_coord) 
            if pacman: pacman.draw(WIN) 
            for ghost in ghosts: ghost.draw(WIN)
            draw_playing_hud(WIN)
        elif current_game_state == STATE_GAME_OVER:
            btn_r, btn_m = draw_game_over_screen(WIN)
            game_over_buttons["restart"], game_over_buttons["menu"] = btn_r, btn_m
            
        pygame.display.update()
        game_clock.tick(FPS)
        
    pygame.quit()

if __name__ == "__main__":
    game_controller()
