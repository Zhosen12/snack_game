import random
import pygame
from pygame.locals import *
import sys
from collections import deque
import time

pygame.init()

GAME_BOX_SIZE = (501, 501)
SCREEN_SIZE = (500, 541)
CELL_SIZE = (20, 20)
CELLS = (int(GAME_BOX_SIZE[0] // CELL_SIZE[0]), int(GAME_BOX_SIZE[1] // CELL_SIZE[0]))
LINE_WIDTH = 1
BACKGROUND_COLOR = (40, 40, 60)
LINE_COLOR = (10, 10, 10)
FOOD_COLOR = (206, 120, 69)
SNACK_HEAD_COLOR = (42, 109, 213)
SNACK_BODY_COLOR = (255, 255, 255)

TURN_UP = (0, -1)
TURN_DOWN = (0, 1)
TURN_LEFT = (-1, 0)
TURN_RIGHT = (1, 0)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('贪吃蛇')
FONT = pygame.font.SysFont('JetBrains Mono', 25)

sleep = 0.4
game_mode = 'init'
gameover = False
start = True


def draw_background():
    screen.fill(BACKGROUND_COLOR)

    # draw vertical lines
    for x in range(0, GAME_BOX_SIZE[0], CELL_SIZE[0]):
        start_pos = (x, 0)
        end_pos = (x, GAME_BOX_SIZE[1])
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, LINE_WIDTH)

    # draw horizontal lines
    for y in range(0, GAME_BOX_SIZE[1], CELL_SIZE[0]):
        start_pos = (0, y)
        end_pos = (GAME_BOX_SIZE[0], y)
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, LINE_WIDTH)


def draw_cell(cell_pos: tuple, color: tuple, width=0):
    pix_pos = cell_to_pix(cell_pos)
    pygame.draw.rect(screen, color, pix_pos + CELL_SIZE, width)


def recover_snack_end(cell_pos: tuple, color: tuple, width=0):
    pix_pos = cell_to_pix(cell_pos)
    pygame.draw.rect(screen, LINE_COLOR, pix_pos + CELL_SIZE, width)
    modified_pos = pix_pos[0] + 1, pix_pos[1] + 1
    pygame.draw.rect(screen, color, modified_pos + (19, 19), width)


def recover_background(snack, food):
    draw_background()
    snack.draw_snack()
    food.draw_food()


def cell_to_pix(cell_pos):
    return cell_pos[0] * CELL_SIZE[0], cell_pos[1] * CELL_SIZE[0]


def key_event(key, snack, food):
    global game_mode, gameover
    if key == K_RETURN:
        if game_mode == 'init':
            draw_background()
            food.generate_food(snack)
            snack.draw_snack()
            game_mode = 'playing'
        elif game_mode == 'playing':
            screen.blit(FONT.render(f'GAME STOP !', True, FOOD_COLOR), (190, 220))
            game_mode = 'stop'
        elif game_mode == 'stop':
            recover_background(snack, food)
            game_mode = 'playing'
        if gameover:
            snack.restart()
            food.generate_food(snack)
            gameover = False
    elif key in (K_w, K_UP) and snack.next_pos != TURN_DOWN and snack.turn:
        snack.next_pos = TURN_UP
        snack.turn = False
    elif key in (K_a, K_LEFT) and snack.next_pos != TURN_RIGHT and snack.turn:
        snack.next_pos = TURN_LEFT
        snack.turn = False
    elif key in (K_s, K_DOWN) and snack.next_pos != TURN_UP and snack.turn:
        snack.next_pos = TURN_DOWN
        snack.turn = False
    elif key in (K_d, K_RIGHT) and snack.next_pos != TURN_LEFT and snack.turn:
        snack.next_pos = TURN_RIGHT
        snack.turn = False


def show_mes(length, score, speed=1):
    pygame.draw.rect(screen, BACKGROUND_COLOR, (1, 501, 501, 40))
    screen.blit(FONT.render(f'LENGTH:{length}', True, FOOD_COLOR), (10, 508))
    # screen.blit(FONT.render(f'SCORE:{score}', True, FOOD_COLOR), (180, 508))
    # screen.blit(FONT.render(f'SPEED:{speed}', True, FOOD_COLOR), (380, 508))


def game_over():
    global game_mode, gameover
    screen.blit(FONT.render(f'GAME IS OVER', True, FOOD_COLOR), (20, 200))
    screen.blit(FONT.render(f'Enter to next game.', True, FOOD_COLOR), (20, 250))
    game_mode = 'stop'
    gameover = True


class GameOver(Exception): pass


class Food:
    def __init__(self):
        self.score = None
        self.pos = None

    def generate_food(self, snack=None):
        while True:
            self.pos = random.randint(0, CELLS[0] - 1), random.randint(0, CELLS[1] - 1)
            if self.pos not in snack.body and self.pos != snack.head:
                break
        self.score = 1
        draw_cell(self.pos, FOOD_COLOR)

    def draw_food(self):
        draw_cell(self.pos, FOOD_COLOR)


class Snack:
    def __init__(self):
        self.turn = True
        self.next_pos = TURN_UP
        self.head = (13, 12)
        self.body = deque([(13, 13), (13, 14)])
        self.draw_snack()

    def restart(self):
        self.turn = True
        self.next_pos = TURN_UP
        self.head = (13, 12)
        self.body = deque([(13, 13), (13, 14)])
        draw_background()
        self.draw_snack()

    def draw_snack(self):
        draw_cell(self.head, SNACK_HEAD_COLOR)
        for i in self.body:
            draw_cell(i, SNACK_BODY_COLOR)

    def move(self, food: Food):
        self.body.appendleft(self.head)
        self.head = self.head[0] + self.next_pos[0], self.head[1] + self.next_pos[1]
        try:
            if self.head != food.pos:  # not eat food
                recover_snack_end(self.body.pop(), BACKGROUND_COLOR)
            else:  # ate food
                food.generate_food(self)

            if (self.head in self.body) or not (0 <= self.head[0] < 25 and 0 <= self.head[1] < 25):  # head crash body
                # or run out of world
                raise GameOver()
            self.draw_snack()
        except GameOver:
            game_over()
        self.turn = True


def main():
    draw_background()
    food = Food()
    snack = Snack()
    last_time = time.time()

    screen.blit(FONT.render('Enter to START/STOP.', True, FOOD_COLOR), (20, 20))
    screen.blit(FONT.render('Use WASD/direction key to play.', True, FOOD_COLOR), (20, 60))

    while True:
        # 循环获取事件，监听事件状态
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                key_event(event.key, snack, food)
        show_mes(len(snack.body) + 1, 9999)
        if time.time() - last_time > sleep and game_mode == 'playing':
            snack.move(food)
            last_time = time.time()
        pygame.display.update()


if __name__ == '__main__':
    main()
