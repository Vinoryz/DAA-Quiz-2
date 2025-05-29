# algorithms.py
from collections import deque

def bfs(start, is_target, grid):
    visited = set()
    queue = deque([(start, [])])

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if is_target(x, y):
            return path + [(x, y)], visited

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                if grid[ny][nx] != 1 and (nx, ny) not in visited:
                    # Append new node (nx, ny) to path, not current node (x,y)
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return [], visited

def dfs(start, is_target, grid):
    visited = set()
    stack = [(start, [])]

    while stack:
        (x, y), path = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if is_target(x, y):
            return path + [(x, y)], visited

        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                if grid[ny][nx] != 1 and (nx, ny) not in visited:
                    stack.append(((nx, ny), path + [(nx, ny)]))

    return [], visited
