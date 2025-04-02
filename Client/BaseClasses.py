import math
import random
from hashlib import scrypt
from time import time

import pygame as pg

IP = "192.168.1.224"
PORT = "8000"


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return Vector2(self.x + other[0], self.y + other[1])

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


    def dot(self, other):
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        return None

    def __len__(self):
        return abs(self)

    def normalize(self):
        magnitude = abs(self)
        if magnitude > 0:
            return self / magnitude

    def direction(self):
        if self.y == 0 and self.x == 0:
            return 0
        angle_rad = math.atan2(self.y, self.x)
        angle_deg = math.degrees(angle_rad)
        return (90 - angle_deg) % 360

    def tup(self):
        return self.x, self.y

    def to_list(self):
        return [self.x, self.y]

    def __bool__(self):
        return True
    def __round__(self, n=None):
        self.round(n)
        return self
    def round(self, *args):
        self.x = round(self.x, *args)
        self.y = round(self.y, *args)
    def __eq__(self, other):
        return abs(self.x - other.x) < 10 ** -8 and abs(self.y - other.y) < 10 ** -8

    @staticmethod
    def from_dir_mag(direction: float, magnitude: float):
        # compass direction
        direction /= 180 / math.pi
        if magnitude < 0:
            direction -= math.pi
            magnitude *= -1
        x = math.sin(direction) * magnitude
        y = math.cos(direction) * magnitude
        if abs(x) < 10 ** -8:
            x = 0
        if abs(y) < 10 ** -8:
            y = 0
        return Vector2(x, y)


class Boundary:
    def __init__(self, max_x, min_x, max_y, min_y):
        self.max_x = max_x
        self.min_x = min_x
        self.max_y = max_y
        self.min_y = min_y
        assert self.max_x > self.min_x
        assert self.max_y > self.min_y

    def __len__(self):
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)

    def contains(self, point: Vector2):
        if not isinstance(point, Vector2):
            raise ValueError("Input must be a Vector2 instance")
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y

    def clamp(self, point: Vector2):
        if not isinstance(point, Vector2):
            raise ValueError("Input must be a Vector2 instance")
        # sourcery to clamp, i love auto complete
        return Vector2(max(self.min_x, min(self.max_x, point.x)), max(self.min_y, min(self.max_y, point.y)))

    def get_width(self):
        return self.max_x - self.min_x

    def get_height(self):
        return self.max_y - self.min_y

    def get_center(self):
        return Vector2((self.max_x + self.min_x) / 2, (self.max_y + self.min_y) / 2)

    def __contains__(self, item: Vector2):
        return self.contains(item)

    def boundary_to_outside_point(self, point: Vector2):
        if not isinstance(point, Vector2):
            raise ValueError("Input must be a Vector2 instance")
        x = 0
        y = 0
        if point.x < self.min_x:
            x = point.x - self.min_x
        if point.x > self.max_x:
            x = point.x - self.max_x
        if point.y < self.min_y:
            y = point.y - self.min_y
        if point.y > self.max_y:
            y = point.y - self.max_y
        return Vector2(x, y)

    def get_random_point_inside(self):
        x = random.uniform(self.min_x, self.max_x)
        y = random.uniform(self.min_y, self.max_y)
        return Vector2(x, y)


basic_boundary = Boundary(1000, -1000, 1000, -1000)


def display_text(size: int, text: str, screen: pg.Surface, colour: list[int, int, int] | tuple[int, int, int],
                 font: str = "Arial", *,
                 top_left_pos: Vector2 = None, center_pos: Vector2 = None, background: list[int, int, int] = None):
    font = pg.font.SysFont(font, size)
    text = font.render(text, True, colour)
    if center_pos is not None:
        pos = (round(center_pos.x - (text.get_rect().width / 2)), round(center_pos.y - (text.get_rect().height / 2)))
    elif top_left_pos is not None:
        pos = (top_left_pos.x, top_left_pos.y)
    else:
        pos = (0, 0)
    pos = (round(pos[0]), round(pos[1]))
    if background is not None:
        width = text.get_rect().width
        height = text.get_rect().height
        pg.draw.rect(screen, background, (pos[0], pos[1], width, height))
    screen.blit(text, pos)


def display_multi_line_text(size: int, text: str, screen: pg.Surface,
                            colour: list[int, int, int] | tuple[int, int, int], font: str = "Arial", *,
                            top_left_pos: Vector2 = None, center_pos: Vector2 = None):
    lines = text.split("\n")
    if center_pos:
        big_line = lines[0]
        for line in lines:
            if len(line) > len(big_line):
                big_line = line
        font = pg.font.SysFont(font, size)
        text = font.render(big_line, True, colour)
        pos = (center_pos.x - (text.get_rect().width / 2),
               center_pos.y - (text.get_rect().height / 2) - (len(lines) * size / 2))
    elif top_left_pos:
        pos = (top_left_pos.x, top_left_pos.y)
    else:
        pos = (0, 0)
    for z, line in enumerate(lines):
        display_text(size, line, screen, colour, font, top_left_pos=Vector2(round(pos[0]), round(pos[1] + size * z)))


def gen_token(private):
    correct_time = math.floor(time())
    salt = str(correct_time).encode()
    key = str(private).encode()
    hash_one = scrypt(key, salt=salt, n=16384, r=8, p=1, dklen=32)
    return int.from_bytes(hash_one)


# Test cases for Vector2 class and dir_to_vector2 function
if __name__ == '__main__':
    vectors = [Vector2(0, 0), Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, -1), Vector2(-1, -1),
               Vector2(-1, 0)]
    expected = [0, 0, 45, 90, 180, 225, 270]
    for i in range(0, len(vectors)):
        print("Vector: " + str(vectors[i]) + " expected: " + str(expected[i]) + " got: " + str(vectors[i].direction()))
    vectors = [(0, 1), (0, 0), (90, 1), (180, 1), (270, 1), (360, 1), (-90, 1), (-270, 1)]
    expected = [(0, 1), (0, 0), (1, 0), (0, -1), (-1, 0), (0, 1), (-1, 0), (1, 0)]
    for i in range(0, len(vectors)):
        print("Dir,Mag : " + str(vectors[i]) + " expected: " + str(expected[i]) + " got: " + str(
            Vector2.from_dir_mag(*vectors[i])))
