import random
import math

class Species:
    def __init__(self, player=None):
        self.players = []  # List of players in the species
        self.best_fitness = 0
        self.champ = None  # Champion of the species
        self.average_fitness = 0
        self.staleness = 0  # How many generations without improvement
        self.rep = None  # Representative genome for the species

        # Coefficients for genome compatibility testing
        self.excess_coeff = 1.5
        self.weight_diff_coeff = 0.8
        self.compatibility_threshold = 1

        # If a player is provided, initialize the species with that player
        if player:
            self.players.append(player)
            self.best_fitness = player.fitness
            self.rep = player.brain.clone()
            self.champ = player.clone_for_replay()

    def same_species(self, genome):
        """Returns whether the parameter genome is in this species based on compatibility."""
        excess_and_disjoint = self.get_excess_disjoint(genome, self.rep)
        average_weight_diff = self.average_weight_diff(genome, self.rep)
        large_genome_normalizer = 1  # You could use the genome size to normalize this

        compatibility = ((self.excess_coeff * excess_and_disjoint / large_genome_normalizer) +
                         (self.weight_diff_coeff * average_weight_diff))
        return self.compatibility_threshold > compatibility

    def add_to_species(self, player):
        """Add a player to the species."""
        self.players.append(player)

    def get_excess_disjoint(self, genome1, genome2):
        """Returns the number of excess and disjoint genes between two genomes."""
        matching_genes = 0
        for gene1 in genome1.genes:
            for gene2 in genome2.genes:
                if gene1.innovationNo == gene2.innovationNo:
                    matching_genes += 1
                    break
        return (len(genome1.genes) + len(genome2.genes) - 2 * matching_genes)

    def average_weight_diff(self, genome1, genome2):
        """Returns the average weight difference between matching genes in two genomes."""
        matching_genes = 0
        total_weight_diff = 0
        for gene1 in genome1.genes:
            for gene2 in genome2.genes:
                if gene1.innovationNo == gene2.innovationNo:
                    matching_genes += 1
                    total_weight_diff += abs(gene1.weight - gene2.weight)
                    break
        if matching_genes == 0:
            return 100  # Avoid division by zero
        return total_weight_diff / matching_genes

    def sort_species(self):
        """Sort the players in the species by fitness."""
        self.players.sort(key=lambda player: player.fitness, reverse=True)

        # If a new best player is found, reset staleness and update best player and representative genome
        if self.players[0].fitness > self.best_fitness:
            self.staleness = 0
            self.best_fitness = self.players[0].fitness
            self.rep = self.players[0].brain.clone()
            self.champ = self.players[0].clone_for_replay()
        else:
            self.staleness += 1

    def set_average(self):
        """Calculate and set the average fitness for the species."""
        total_fitness = sum(player.fitness for player in self.players)
        self.average_fitness = total_fitness / len(self.players)

    def give_me_baby(self, innovation_history):
        """Create a baby player through crossover or cloning."""
        if random.random() < 0.25:  # 25% chance to clone a random player
            baby = self.select_player().clone()
        else:  # 75% chance to create a baby via crossover
            parent1 = self.select_player()
            parent2 = self.select_player()

            if parent1.fitness < parent2.fitness:
                baby = parent2.crossover(parent1)
            else:
                baby = parent1.crossover(parent2)

        baby.brain.mutate(innovation_history)
        return baby

    def select_player(self):
        """Select a player from the species based on fitness."""
        fitness_sum = sum(player.fitness for player in self.players)
        rand = random.uniform(0, fitness_sum)
        running_sum = 0

        for player in self.players:
            running_sum += player.fitness
            if running_sum > rand:
                return player

        return self.players[0]  # Fallback in case of rounding errors

    def cull(self):
        """Kill the bottom half of the species."""
        if len(self.players) > 2:
            self.players = self.players[:len(self.players) // 2]

    def fitness_sharing(self):
        """Applies fitness sharing by dividing each player's fitness by the number of players in the species."""
        for player in self.players:
            player.fitness /= len(self.players)
