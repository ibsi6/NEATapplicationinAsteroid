import math
import pygame
from pygame.math import Vector2



class Asteroid:
    def __init__(self, posX, posY, velX, velY, sizeNo):
        self.pos = Vector2(posX, posY)
        self.vel = Vector2(velX, velY)
        self.size = sizeNo
        self.split = False
        self.chunks = []
        self.sizeHit = None

        # Set radius and velocity based on size
        if sizeNo == 1:
            self.radius = 15
            self.vel = self.vel.normalize() * 1.25
        elif sizeNo == 2:
            self.radius = 30
            self.vel = self.vel.normalize()
        elif sizeNo == 3:
            self.radius = 60
            self.vel = self.vel.normalize() * 0.75

    def show(self, screen):
        if self.split:
            for asteroid in self.chunks:
                asteroid.show(screen)
        else:
            pygame.draw.polygon(screen, (255, 255, 255), self.get_polygon_vertices())

    def get_polygon_vertices(self, npoints=12):
        vertices = []
        angle_step = 2 * math.pi / npoints
        for i in range(npoints):
            angle = i * angle_step
            x = self.pos.x + math.cos(angle) * self.radius
            y = self.pos.y + math.sin(angle) * self.radius
            vertices.append((x, y))
        return vertices

    def move(self, width, height):
        if self.split:
            for asteroid in self.chunks:
                asteroid.move(width, height)
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

    def check_if_hit(self, bullet_pos, width, height):
        if self.split:
            return any(asteroid.check_if_hit(bullet_pos, width, height) for asteroid in self.chunks)
        else:
            if self.pos.distance_to(bullet_pos) < self.radius:
                self.is_hit()
                return True

            # Check for overlapping edges and bullet position near the edge
            if self.is_near_edge(width, height):
                overlap_pos = self.get_overlap_position(width, height)
                if overlap_pos.distance_to(bullet_pos) < self.radius:
                    self.is_hit()
                    return True
            return False

    def is_near_edge(self, width, height):
        return (self.pos.x < -50 + self.radius or self.pos.x > width + 50 - self.radius or
                self.pos.y < -50 + self.radius or self.pos.y > height + 50 - self.radius)

    def get_overlap_position(self, width, height):
        overlap_pos = self.pos.copy()
        if self.pos.x < -50 + self.radius:
            overlap_pos.x += width + 100
        if self.pos.x > width + 50 - self.radius:
            overlap_pos.x -= width + 100
        if self.pos.y < -50 + self.radius:
            overlap_pos.y += height + 100
        if self.pos.y > height + 50 - self.radius:
            overlap_pos.y -= height + 100
        return overlap_pos

    def is_hit(self):
        self.split = True
        if self.size == 1:
            return  # No splitting for the smallest asteroids

        # Create two smaller asteroids with slightly different velocities
        vel1 = self.vel.rotate(-17.18)  # equivalent to -0.3 radians
        vel2 = self.vel.rotate(28.65)  # equivalent to 0.5 radians
        self.chunks.append(Asteroid(self.pos.x, self.pos.y, vel1.x, vel1.y, self.size - 1))
        self.chunks.append(Asteroid(self.pos.x, self.pos.y, vel2.x, vel2.y, self.size - 1))

    def check_if_hit_player(self, player_pos, width, height):
        if self.split:
            return any(asteroid.check_if_hit_player(player_pos, width, height) for asteroid in self.chunks)
        else:
            if self.pos.distance_to(player_pos) < self.radius + 15:
                self.is_hit()
                return True

            if self.is_near_edge(width, height):
                overlap_pos = self.get_overlap_position(width, height)
                if overlap_pos.distance_to(player_pos) < self.radius:
                    self.is_hit()
                    return True
            return False

    def look_for_hit(self, bullet_pos, width, height):
        if self.split:
            return any(asteroid.look_for_hit(bullet_pos, width, height) for asteroid in self.chunks)
        else:
            if self.pos.distance_to(bullet_pos) < self.radius:
                self.sizeHit = self.size
                return True

            if self.is_near_edge(width, height):
                overlap_pos = self.get_overlap_position(width, height)
                if overlap_pos.distance_to(bullet_pos) < self.radius:
                    return True
            return False

    def get_asteroid(self, bullet_pos, width, height):
        if self.split:
            for asteroid in self.chunks:
                result = asteroid.get_asteroid(bullet_pos, width, height)
                if result:
                    return result
            return None
        else:
            if self.pos.distance_to(bullet_pos) < self.radius:
                return self
            if self.is_near_edge(width, height):
                overlap_pos = self.get_overlap_position(width, height)
                if overlap_pos.distance_to(bullet_pos) < self.radius:
                    return self
            return None
