import streamlit as st
import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
COLS, ROWS = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),   # I
    (0, 0, 255),     # J
    (255, 165, 0),   # L
    (255, 255, 0),   # O
    (0, 255, 0),     # S
    (128, 0, 128),   # T
    (255, 0, 0)      # Z
]

# Tetromino shapes with all rotations
SHAPES = [
    [[[1, 1, 1, 1]],
     [[1],
      [1],
      [1],
      [1]]],

    [[[1, 0, 0],
      [1, 1, 1]],
     [[1, 1],
      [1, 0],
      [1, 0]],
     [[1, 1, 1],
      [0, 0, 1]],
     [[0, 1],
      [0, 1],
      [1, 1]]],

    [[[0, 0, 1],
      [1, 1, 1]],
     [[1, 0],
      [1, 0],
      [1, 1]],
     [[1, 1, 1],
      [1, 0, 0]],
     [[1, 1],
      [0, 1],
      [0, 1]]],

    [[[1, 1],
      [1, 1]]],

    [[[0, 1, 1],
      [1, 1, 0]],
     [[1, 0],
      [1, 1],
      [0, 1]]],

    [[[0, 1, 0],
      [1, 1, 1]],
     [[1, 0],
      [1, 1],
      [1, 0]],
     [[1, 1, 1],
      [0, 1, 0]],
     [[0, 1],
      [1, 1],
      [0, 1]]],

    [[[1, 1, 0],
      [0, 1, 1]],
     [[0, 1],
      [1, 1],
      [1, 0]]]
]

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def get_cells(self):
        cells = []
        shape = self.image()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    cells.append((self.x + j, self.y + i))
        return cells

def convert_shape_format(piece):
    return piece.get_cells()

def valid_space(piece, grid):
    for x, y in convert_shape_format(piece):
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True

def check_lost(positions):
    return any(y < 1 for (x, y) in positions)

def draw_grid(grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(screen, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for i in range(ROWS):
        pygame.draw.line(screen, GRAY, (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE))
    for j in range(COLS):
        pygame.draw.line(screen, GRAY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, HEIGHT))

def clear_rows(grid, locked):
    cleared = 0
    for i in range(len(grid)-1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            del_row = i
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if cleared > 0:
        for key in sorted(locked, key=lambda k: k[1])[::-1]:
            x, y = key
            if y < del_row:
                locked[(x, y + cleared)] = locked.pop((x, y))
    return cleared

def get_new_piece():
    return Piece(COLS // 2 - 2, 0, random.choice(SHAPES))

def draw_window(grid, score):
    screen.fill(BLACK)
    draw_grid(grid)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))
    screen.blit(label, (10, 10))
    pygame.display.update()

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        for x, y in convert_shape_format(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in convert_shape_format(current_piece):
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = get_new_piece()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(grid, score)

        if check_lost(locked_positions):
            run = False

    pygame.quit()

main()
