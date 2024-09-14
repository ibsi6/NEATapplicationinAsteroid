import random
import math
import pygame
from pygame.math import Vector2
from Genome import Genome  
from Bullet import Bullet  
from Asteroid import Asteroid  


class Player:
    def __init__(self, seed=None):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.pos = Vector2(screen_width // 2, screen_height // 2)
        self.vel = Vector2()
        self.acc = Vector2()

        self.score = 0
        self.shoot_count = 0
        self.rotation = 0
        self.spin = 0
        self.max_speed = 10
        self.boosting = False
        self.bullets = []
        self.asteroids = []
        self.asteroid_count = 1000
        self.lives = 0
        self.dead = False
        self.immortal_count = 0
        self.boost_count = 10

        # Neural network (AI)
        self.brain = Genome(33, 4)
        self.vision = [0.0] * 33
        self.decision = [0.0] * 4
        self.replay = seed is not None
        self.seed_used = seed if seed else random.randint(0, 1000000000)
        self.seeds_used = []
        self.up_to_seed_no = 0
        self.fitness = 0
        self.unadjusted_fitness = 0
        self.shots_fired = 4
        self.shots_hit = 1
        self.lifespan = 0
        self.can_shoot = True
        self.best_score = 0

        random.seed(self.seed_used)

        # Initialize asteroids
        self.generate_asteroids()

    def generate_asteroids(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        for _ in range(4):
            rand_x = random.uniform(0, screen_width)
            rand_y = random.uniform(0, screen_height)
            asteroid = Asteroid(rand_x, rand_y, random.uniform(-1, 1), random.uniform(-1, 1), 3)
            self.asteroids.append(asteroid)

        # Create a fifth asteroid aimed at the player
        rand_x = random.uniform(0, screen_width)
        rand_y = -50 + random.choice([0, screen_height + 100])
        self.asteroids.append(Asteroid(rand_x, rand_y, self.pos.x - rand_x, self.pos.y - rand_y, 3))

    def move(self):
        if not self.dead:
            self.check_timers()
            self.rotate_player()

            if self.boosting:
                self.boost()
            else:
                self.boost_off()

            # Only normalize the velocity if its length is greater than 0
            if self.vel.length() > 0:
                self.vel = self.vel.normalize() * min(self.vel.length(), self.max_speed)

            self.vel *= 0.99  # Apply friction
            self.pos += self.vel  # Update position

            # Get screen width and height
            screen_width, screen_height = pygame.display.get_surface().get_size()

            # Move bullets
            for bullet in self.bullets:
                bullet.move(screen_width, screen_height)  # Pass screen size to bullet.move()

            # Move asteroids
            for asteroid in self.asteroids:
                asteroid.move(screen_width, screen_height)

            # Wrap around the screen
            if self.is_out_of_bounds(self.pos):
                self.wrap_position()


    def show(self):
        # Define the screen size, assuming a standard resolution (you can modify this as needed)
        screen_width, screen_height = pygame.display.get_surface().get_size()
        screen = pygame.display.get_surface()

        # Draw the player
        if not self.dead:
            if self.immortal_count > 0:
                # Optional: add logic to flash the player if they're immortal (e.g., after losing a life)
                if (self.immortal_count // 5) % 2 == 0:
                    return  # Skip drawing the player to make it flash
            # Draw the player as a triangle
            pygame.draw.polygon(screen, (255, 255, 255), self.get_player_vertices())

        # Draw bullets
        for bullet in self.bullets:
            bullet.show(screen)

        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.show(screen)

    def get_player_vertices(self):
        """ Returns the vertices of the player's ship (triangle) for rendering. """
        size = 12
        points = [
            (self.pos.x + math.cos(self.rotation) * 2 * size, self.pos.y + math.sin(self.rotation) * 2 * size),  # Front point
            (self.pos.x + math.cos(self.rotation + math.pi * 0.8) * size, self.pos.y + math.sin(self.rotation + math.pi * 0.8) * size),  # Back-left point
            (self.pos.x + math.cos(self.rotation - math.pi * 0.8) * size, self.pos.y + math.sin(self.rotation - math.pi * 0.8) * size)   # Back-right point
        ]
        return points

    def check_timers(self):
        self.lifespan += 1
        self.shoot_count -= 1
        self.asteroid_count -= 1

        if self.asteroid_count <= 0:
            if self.replay:
                random.seed(self.seeds_used[self.up_to_seed_no])
                self.up_to_seed_no += 1
            else:
                seed = random.randint(0, 1000000)
                self.seeds_used.append(seed)
                random.seed(seed)

            screen_width, screen_height = pygame.display.get_surface().get_size()
            rand_x = random.uniform(0, screen_width)
            rand_y = -50 + random.choice([0, screen_height + 100])
            asteroid = Asteroid(rand_x, rand_y, self.pos.x - rand_x, self.pos.y - rand_y, 3)
            self.asteroids.append(asteroid)
            self.asteroid_count = 1000

        if self.shoot_count <= 0:
            self.can_shoot = True

    def boost(self):
        self.acc = Vector2(math.cos(self.rotation), math.sin(self.rotation)) * 0.5

    def boost_off(self):
        self.acc = Vector2()

    def rotate_player(self):
        self.rotation += self.spin

    def is_out_of_bounds(self, pos):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        return pos.x < -50 or pos.x > screen_width + 50 or pos.y < -50 or pos.y > screen_height + 50

    def wrap_position(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        if self.pos.x < -50:
            self.pos.x = screen_width + 50
        elif self.pos.x > screen_width + 50:
            self.pos.x = -50

        if self.pos.y < -50:
            self.pos.y = screen_height + 50
        elif self.pos.y > screen_height + 50:
            self.pos.y = -50

    def shoot(self):
        if self.shoot_count <= 0:
            bullet = Bullet(self.pos.x, self.pos.y, self.rotation, self.vel.length())
            self.bullets.append(bullet)
            self.shoot_count = 50
            self.can_shoot = False
            self.shots_fired += 1

    def check_positions(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        # Check if bullets hit asteroids
        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if asteroid.check_if_hit(bullet.pos, screen_width, screen_height):  # Pass screen size
                    self.shots_hit += 1
                    self.bullets.remove(bullet)
                    self.score += 1
                    break

        # Check if player hit by asteroid
        if self.immortal_count <= 0:
            for asteroid in self.asteroids:
                if asteroid.check_if_hit_player(self.pos, screen_width, screen_height):  # Pass screen size
                    self.player_hit()

    def player_hit(self):
        if self.lives == 0:
            self.dead = True
        else:
            self.lives -= 1
            self.immortal_count = 100
            self.reset_position()

    def reset_position(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        self.pos = Vector2(screen_width / 2, screen_height / 2)
        self.vel = Vector2()
        self.acc = Vector2()
        self.bullets = []
        self.rotation = 0

    def calculate_fitness(self):
        hit_rate = self.shots_hit / self.shots_fired
        self.fitness = (self.score + 1) * 10
        self.fitness *= self.lifespan
        self.fitness *= hit_rate * hit_rate
        self.unadjusted_fitness = self.fitness

    def clone(self):
        clone_player = Player()
        clone_player.brain = self.brain.clone()
        clone_player.fitness = self.fitness
        clone_player.brain.generate_network()
        return clone_player

    def clone_for_replay(self):
        clone_player = Player(self.seed_used)
        clone_player.brain = self.brain.clone()
        clone_player.fitness = self.fitness
        clone_player.best_score = self.score
        clone_player.seeds_used = self.seeds_used[:]
        clone_player.brain.generate_network()
        return clone_player

    def crossover(self, parent2):
        child_player = Player()
        child_player.brain = self.brain.crossover(parent2.brain)
        child_player.brain.generate_network()
        return child_player

    def look(self):
        self.vision = [0.0] * 33
        for i in range(16):
            angle = self.rotation + i * (math.pi / 8)
            direction = Vector2(math.cos(angle), math.sin(angle)) * 10
            self.look_in_direction(direction, i)

        if self.can_shoot and self.vision[0] != 0:
            self.vision[32] = 1
        else:
            self.vision[32] = 0

    def look_in_direction(self, direction, vision_pos):
        position = self.pos + direction
        distance = 1  # Initialize distance to 1 to avoid zero division
        looped = Vector2(0, 0)

        screen_width, screen_height = pygame.display.get_surface().get_size()

        while distance < 60:
            for asteroid in self.asteroids:
                if asteroid.look_for_hit(position, screen_width, screen_height):  # Pass screen size
                    self.vision[vision_pos] = 1 / distance  # No zero division

                    asteroid_hit = asteroid.get_asteroid(position, screen_width, screen_height)  # Pass screen size
                    towards_player = (self.pos - asteroid_hit.pos - looped).normalize()
                    red_shift = asteroid_hit.vel.dot(towards_player)
                    self.vision[vision_pos + 1] = red_shift

            position += direction
            distance += 1  # Increment the distance

            # Loop the position
            if position.x < -50:
                position.x += screen_width + 100
                looped.x += screen_width + 100
            elif position.x > screen_width + 50:
                position.x -= screen_width + 100
                looped.x -= screen_width + 100

            if position.y < -50:
                position.y += screen_height + 100
                looped.y += screen_height + 100
            elif position.y > screen_height + 50:
                position.y -= screen_height + 100
                looped.y -= screen_height + 100


    def update(self):
        # Remove bullets that have expired (i.e., bullets that have 'off' set to True)
        self.bullets = [bullet for bullet in self.bullets if not bullet.off]

        # Move everything (player, bullets, asteroids)
        self.move()

        # Check if anything has been shot or hit
        self.check_positions()

    def think(self):
        self.decision = self.brain.feed_forward(self.vision)

        if self.decision[0] > 0.8:
            self.boosting = True
        else:
            self.boosting = False

        if self.decision[1] > 0.8:
            self.spin = -0.08
        elif self.decision[2] > 0.8:
            self.spin = 0.08
        else:
            self.spin = 0

        if self.decision[3] > 0.8:
            self.shoot()
