import random

def generate_maze(rows, cols):
    # Fill with walls
    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def in_bounds(x, y):
        return 0 <= x < cols and 0 <= y < rows

    def neighbors(x, y):
        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        return [(x + dx, y + dy) for dx, dy in dirs if in_bounds(x + dx, y + dy)]

    # Initial carving using Prim's
    start_x, start_y = random.randrange(1, cols, 2), random.randrange(1, rows, 2)
    maze[start_y][start_x] = 0
    walls = [(start_x + dx, start_y + dy, start_x, start_y)
             for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]
             if in_bounds(start_x + dx, start_y + dy)]

    while walls:
        wx, wy, px, py = walls.pop(random.randint(0, len(walls) - 1))
        if maze[wy][wx] == 1:
            maze[wy][wx] = 0
            maze[(wy + py) // 2][(wx + px) // 2] = 0
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = wx + dx, wy + dy
                if in_bounds(nx, ny) and maze[ny][nx] == 1:
                    walls.append((nx, ny, wx, wy))

    # 🌟 Add extra connections to reduce dead ends and make loops
    extra_connections = (rows * cols) // 15  # Adjust density here
    for _ in range(extra_connections):
        x = random.randrange(1, cols - 1, 2)
        y = random.randrange(1, rows - 1, 2)

        # Pick a random direction to knock down a wall
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                break  # Add one connection per loop

    # 🟡 Place food randomly on path tiles
    for y in range(rows):
        for x in range(cols):
            if maze[y][x] == 0 and random.random() < 0.3:
                maze[y][x] = 2

    return maze, (start_x, start_y)
