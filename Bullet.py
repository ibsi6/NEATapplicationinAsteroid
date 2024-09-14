import pygame
from pygame.math import Vector2
import math

class Bullet:
    def __init__(self, x, y, r, player_speed):
        self.pos = Vector2(x, y)
        self.vel = Vector2(1, 0).rotate(math.degrees(r)) * (10 + player_speed)  # PVector.fromAngle equivalent
        self.speed = 10
        self.off = False
        self.lifespan = 60

    def move(self, width, height):
        self.lifespan -= 1
        if self.lifespan < 0:
            self.off = True
        else:
            self.pos += self.vel
            if self.is_out_of_bounds(width, height):
                self.wrap_around_screen(width, height)

    def is_out_of_bounds(self, width, height):
        return self.pos.x < -50 or self.pos.x > width + 50 or self.pos.y < -50 or self.pos.y > height + 50

    def wrap_around_screen(self, width, height):
        if self.pos.x < -50:
            self.pos.x = width + 50
        elif self.pos.x > width + 50:
            self.pos.x = -50

        if self.pos.y < -50:
            self.pos.y = height + 50
        elif self.pos.y > height + 50:
            self.pos.y = -50

    def show(self, screen):
        if not self.off:
            pygame.draw.ellipse(screen, (255, 255, 255), (self.pos.x, self.pos.y, 3, 3))

