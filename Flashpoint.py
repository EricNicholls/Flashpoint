import pygame
from random import randrange

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 162, 0)
RED = (252, 36, 3)
GREEN = (0, 224, 120)
PINK = (240, 20, 247)
BLUE = (13, 13, 168)


NUM_ROWS = 6
NUM_COLS = 8

class Tile:
    STATE_NOTHING = 0
    STATE_SMOKE = 1
    STATE_FIRE = 2
    STATE_HASMAT = 3
    STATE_PERSON = 4
    def __init__(self):
        self.state = 0
        self.hotSpot = False

    def apply_fire(self):
        n = self.state
        if n == self.STATE_NOTHING:
            n = self.STATE_FIRE
            b = False
        elif n == self.STATE_FIRE:
            b = True

        self.state = n
        return b

    def set_hotspot(self):
        self.hotSpot = True
    def get_hotspot(self):
        return self.hotSpot

    def set_hasmat(self):
        if self.state != self.STATE_NOTHING:
            return False
        self.state = self.STATE_HASMAT
        return True

    def set_person(self):
        if self.state != self.STATE_NOTHING:
            return False
        self.state = self.STATE_PERSON
        return True

    def get_state(self):
        return self.state

        # @return: False if fire is blocked, True if continues forward

class Wall:
    state = -1

    STATE_NONE = 0
    STATE_WALL = 1
    STATE_WALL_1 = 2
    STATE_WALL_2 = 3
    STATE_DOOR = 4
    STATE_BOD = 5

    def __init__(self, wall=False):
        # @params
        # wall: bool
        if wall:
            self.state = self.STATE_WALL
        else:
            self.state = self.STATE_NONE

    def get_state(self):
        return self.state

    def set_wall(self):
        if self.state != self.STATE_NONE:
            raise ValueError('Cant create wall unless object in state 0 - none (current state ={})'.format(self.state))
        self.state = self.STATE_WALL

    def set_door(self):
        if self.state != self.STATE_WALL:
            raise ValueError('Cant create door unless object in state 1 - wall (current state ={})'.format(self.state))
        self.state = self.STATE_DOOR

    def apply_fire(self):
        n = self.state
        b = None
        if n == self.STATE_NONE:
            b = True
        elif n == self.STATE_WALL:
            n = self.STATE_WALL_1
            b = False
        elif n == self.STATE_WALL_1:
            n = self.STATE_WALL_2
            b = False
        elif n == self.STATE_WALL_2:
            b = True    # same as state 0
        elif n == self.STATE_DOOR:
            n = self.STATE_BOD
            b = True
        elif n == self.STATE_BOD:
            b = False

        self.state = n
        return b
        # @return: False if fire is blocked, True if continues forward


class Game:
    def __init__(self):
        self.tiles = []
        self.vert_walls = []
        self.horz_walls = []

        self.__setup_game__()

    def __setup_game__(self):
        # initialize tiles, and 2 empty arrays for vert and horz walls

        for i in range(NUM_ROWS):
            a = []
            for j in range(NUM_COLS):
                a.append(Tile())
            self.tiles.append(a)

        for i in range(NUM_ROWS):
            a = []
            for j in range(NUM_COLS + 1):
                a.append(Wall())
            self.vert_walls.append(a)

        for i in range(NUM_ROWS + 1):
            a = []
            for j in range(NUM_COLS):
                a.append(Wall())
            self.horz_walls.append(a)

        # initialize perimeter of walls
        for i in range(NUM_COLS):
            self.horz_walls[0][i].set_wall()
            self.horz_walls[NUM_ROWS][i].set_wall()

        for i in range(NUM_ROWS):
            self.vert_walls[i][0].set_wall()
            self.vert_walls[i][NUM_COLS].set_wall()

        # horz walls
        for i in range(2, 8):
            self.horz_walls[2][i].set_wall()
        for i in range(8):
            self.horz_walls[4][i].set_wall()

        # vert walls
        self.vert_walls[0][3].set_wall()
        self.vert_walls[1][3].set_wall()
        self.vert_walls[0][5].set_wall()
        self.vert_walls[1][5].set_wall()
        self.vert_walls[2][2].set_wall()
        self.vert_walls[3][2].set_wall()
        self.vert_walls[2][6].set_wall()
        self.vert_walls[3][6].set_wall()
        self.vert_walls[4][5].set_wall()
        self.vert_walls[5][5].set_wall()
        self.vert_walls[4][7].set_wall()
        self.vert_walls[5][7].set_wall()

        # explosions
        for i in range(3):
            b = False
            while not b:
                rr = randrange(6)
                rc = randrange(8)
                b = self.setup_explosion(rr, rc)

        # people
        for i in range(3):
            b = False
            while not b:
                rr = randrange(6)
                rc = randrange(8)
                b = self.tiles[rr][rc].set_person()

        # hasmat
        for i in range(3):
            b = False
            while not b:
                rr = randrange(6)
                rc = randrange(8)
                b = self.tiles[rr][rc].set_hasmat()

    def setup_explosion(self, r, c):
        if self.tiles[r][c].state == 2:
            return False    # in setup, explosions can't occur where fire exists

        self.explosion(r, c)
        return True

    def explosion(self, r, c):
        self.tiles[r][c].apply_fire()
        self.tiles[r][c].set_hotspot()

        # for each direction, find wall, then find tile, then wall, etc., until False is returned

        # right
        i = 1
        while True:
            b = self.vert_walls[r][c+i].apply_fire()
            if not b:
                break
            b = self.tiles[r][c+i].apply_fire()
            if not b:
                break
            i += 1

        # left
        i = 0
        while True:
            b = self.vert_walls[r][c-i].apply_fire()
            if not b:
                break
            i += 1
            b = self.tiles[r][c-i].apply_fire()
            if not b:
                break

        # up
        i = 0
        while True:
            b = self.horz_walls[r-i][c].apply_fire()
            if not b:
                break
            i += 1
            b = self.tiles[r-i][c].apply_fire()
            if not b:
                break

        # down
        i = 1
        while True:
            b = self.horz_walls[r+i][c].apply_fire()
            if not b:
                break
            b = self.tiles[r+i][c].apply_fire()
            if not b:
                break
            i += 1


        # print(r,c)
        # print("l", self.vert_walls[r][c].get_state())
        # print("r", self.vert_walls[r][c+1].get_state())
        # print("u", self.horz_walls[r][c].get_state())
        # print("d", self.horz_walls[r+1][c].get_state())

    def draw_board(self):
        global screen, SQ_SZ
        pygame.font.init()

        buffer = 6

        # tiles
        for i in range(NUM_COLS):
            for j in range(NUM_ROWS):
                pygame.draw.rect(screen, GREEN, (i * SQ_SZ +buffer/2, j * SQ_SZ +buffer/2, SQ_SZ - buffer, SQ_SZ - buffer))
                t = self.tiles[j][i]
                if t.get_hotspot():
                    x = int(i * SQ_SZ + SQ_SZ / 6)
                    y = int(j * SQ_SZ + SQ_SZ / 6)
                    pygame.draw.circle(screen, ORANGE, (x, y), 10)
                st = t.get_state()
                if st == 2:     # fire
                    x = int(i * SQ_SZ + SQ_SZ / 2)
                    y = int(j * SQ_SZ + SQ_SZ / 2)
                    pygame.draw.circle(screen, RED, (x, y), 15)

                elif st == 3:   # hasmat
                    x = int(i * SQ_SZ + SQ_SZ / 2)
                    y = int(j * SQ_SZ + SQ_SZ / 2)
                    pygame.draw.circle(screen, BLUE, (x, y), 15)

                elif st == 4:   # person
                    x = int(i * SQ_SZ + SQ_SZ / 2)
                    y = int(j * SQ_SZ + SQ_SZ / 2)
                    pygame.draw.circle(screen, WHITE, (x, y), 15)


        # vert walls
        for i in range(NUM_COLS + 1):
            for j in range(NUM_ROWS):
                st = self.vert_walls[j][i].get_state()
                # print(j,i, ":", st)
                if st == 1 or st == 2 or st == 3:   # wall
                    rec = (i*SQ_SZ - buffer, j*SQ_SZ, 10, SQ_SZ)
                    pygame.draw.rect(screen, BLACK, rec)

                if st == 2:     # 1 counter
                    m = 1.8
                    rec = (i * SQ_SZ -7.5*m, j * SQ_SZ + SQ_SZ/2-buffer*m, 15*m, 4*m)
                    pygame.draw.rect(screen, BLACK, rec)

                if st == 3:     # 2 counter
                    m = 1.8
                    rec = (i * SQ_SZ - 7.5 * m, j * SQ_SZ + SQ_SZ/3, 15 * m, 4 * m)
                    pygame.draw.rect(screen, BLACK, rec)
                    rec2 = (i * SQ_SZ - 7.5 * m, j * SQ_SZ + 2*SQ_SZ/3, 15 * m, 4 * m)
                    pygame.draw.rect(screen, BLACK, rec2)

        # horz walls
        for i in range(NUM_COLS):
            for j in range(NUM_ROWS + 1):
                st = self.horz_walls[j][i].get_state()
                if st == 1 or st == 2 or st == 3:
                    rec = (i * SQ_SZ, j * SQ_SZ - buffer, SQ_SZ, 10)
                    pygame.draw.rect(screen, BLACK, rec)
                if st == 2:     # 1 counter
                    m = 1.8
                    rec = (i * SQ_SZ + SQ_SZ/2-buffer*m, j * SQ_SZ  -7.5*m, 4*m, 15*m)
                    pygame.draw.rect(screen, BLACK, rec)
                if st == 3:     # 2 counter
                    m = 1.8
                    rec = (i * SQ_SZ + SQ_SZ/3, j * SQ_SZ  -7.5*m, 4 * m, 15 * m)
                    pygame.draw.rect(screen, BLACK, rec)
                    rec2 = (i * SQ_SZ + 2*SQ_SZ/3, j * SQ_SZ  -7.5*m, 4 * m, 15 * m)
                    pygame.draw.rect(screen, BLACK, rec2)
        pygame.display.update()


if __name__== "__main__":

    # screen setup
    SQ_SZ = 100
    wid = NUM_COLS * SQ_SZ
    hgt = NUM_ROWS * SQ_SZ
    size = (wid, hgt)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Flashpoint')
    screen.fill(WHITE)

    # Start Game
    game = Game()
    game.draw_board()

    pygame.time.wait(20000)
