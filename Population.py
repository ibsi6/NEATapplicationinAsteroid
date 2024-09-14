import random
from Player import Player
from Species import Species
from connectionHistory import ConnectionHistory 

class Population:
    def __init__(self, size):
        self.pop = [Player() for _ in range(size)]  # List of players
        for player in self.pop:
            player.brain.generate_network()  # Generate the neural network for each player

        self.best_player = None  # The best player ever
        self.best_score = 0  # Score of the best player ever
        self.gen = 1  # Start generation count from 1, not 100
        self.innovation_history = []  # List of connection histories
        self.gen_players = []  # Players of the current generation
        self.species = []  # List of species


    def update_alive(self, show_best=False):
        for i, player in enumerate(self.pop):
            if not player.dead:
                player.look()  # Get inputs for brain
                player.think()  # Use outputs from the neural network
                player.update()  # Move the player based on neural network output
                player.show()  # Show only this player's movements
                break  # Stop after showing the first alive player

    def done(self):
        return all(player.dead for player in self.pop)

    def set_best_player(self):
        temp_best = self.species[0].players[0]  # Best player in the best species

        self.gen_players.append(temp_best)

        # If the best player of this generation is better than the global best, update the global best
        if temp_best.score > self.best_score:
            print(f"Old best: {self.best_score}, New best: {temp_best.score}")
            self.best_score = temp_best.score
            self.best_player = temp_best.clone_for_replay()

    def natural_selection(self):
        self.speciate()  # Separate population into species
        self.calculate_fitness()  # Calculate the fitness of each player
        self.sort_species()  # Sort the species by fitness
        self.cull_species()  # Cull the bottom half of each species
        self.set_best_player()  # Save the best player of this generation
        self.kill_stale_species()  # Remove species that haven't improved in 15 generations
        self.kill_bad_species()  # Remove bad species that can't reproduce

        average_sum = self.get_avg_fitness_sum()
        children = []

        # Breed new children from each species
        for s in self.species:
            children.append(s.players[0].clone())  # Champion without mutation
            num_children = int(s.average_fitness / average_sum * len(self.pop)) - 1
            for _ in range(num_children):
                children.append(s.give_me_baby(self.innovation_history))

        # If not enough children, get from the best species
        while len(children) < len(self.pop):
            children.append(self.species[0].give_me_baby(self.innovation_history))

        self.pop = children  # Replace the population with the new generation
        self.gen += 1  # Increment the generation count after each natural selection
        print(f"Generation {self.gen}, Mutations {len(self.innovation_history)}, Species: {len(self.species)}")


        # Generate networks for each child
        for player in self.pop:
            player.brain.generate_network()

    def speciate(self):
        for s in self.species:
            s.players.clear()  # Clear players for each species

        for player in self.pop:
            species_found = False
            for s in self.species:
                if s.same_species(player.brain):
                    s.add_to_species(player)
                    species_found = True
                    break

            if not species_found:  # Create a new species if no match is found
                self.species.append(Species(player))

    def calculate_fitness(self):
        for player in self.pop:
            player.calculate_fitness()

    def sort_species(self):
        for s in self.species:
            s.sort_species()  # Sort players within each species by fitness

        # Sort species by the fitness of their best player
        self.species.sort(key=lambda s: s.best_fitness, reverse=True)

    def kill_stale_species(self):
        self.species = [s for s in self.species if s.staleness < 15]  # Remove stale species

    def kill_bad_species(self):
        average_sum = self.get_avg_fitness_sum()
        self.species = [s for s in self.species if s.average_fitness / average_sum * len(self.pop) >= 1]

    def get_avg_fitness_sum(self):
        return sum(s.average_fitness for s in self.species)

    def cull_species(self):
        for s in self.species:
            s.cull()  # Kill the bottom half of each species
            s.fitness_sharing()  # Apply fitness sharing
            s.set_average()  # Reset average fitness after culling
