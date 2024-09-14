import pygame
import sys
from Population import Population

# Initialize pygame
pygame.init()

# Define constants for the screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create a Pygame display surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid NEAT Evolution")

font = pygame.font.Font(None, 36)

def main():
    clock = pygame.time.Clock()
    population_size = 100  # Define your population size
    population = Population(population_size)
    
    speed_multiplier = 1  # Default speed, you can increase this to speed up the game
    max_speed = 10  # Max speed multiplier allowed
    min_speed = 1   # Min speed multiplier allowed

    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill the screen with black before drawing anything

        # Event loop for closing the window and controlling speed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Increase speed
                    speed_multiplier = min(max_speed, speed_multiplier + 1)
                elif event.key == pygame.K_DOWN:  # Decrease speed
                    speed_multiplier = max(min_speed, speed_multiplier - 1)

        # Update the game state multiple times according to speed_multiplier
        for _ in range(speed_multiplier):
            population.update_alive()

        # Show the player's movement and evolution (only the first player alive is shown)
        population.pop[0].show()

        # Display the generation count and population count
        generation_text = f"Generation: {population.gen}"
        population_count_text = f"Current Population: {len(population.pop)}"
        speed_text = f"Speed: {speed_multiplier}x"

        # Render the texts
        generation_surface = font.render(generation_text, True, (255, 255, 255))
        population_count_surface = font.render(population_count_text, True, (255, 255, 255))
        speed_surface = font.render(speed_text, True, (255, 255, 255))

        screen.blit(generation_surface, (10, 10))
        screen.blit(population_count_surface, (10, 50))
        screen.blit(speed_surface, (10, 90))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate to 60 FPS
        clock.tick(60)



if __name__ == "__main__":
    main()
