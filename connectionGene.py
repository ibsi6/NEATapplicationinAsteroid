import random

class ConnectionGene:
    def __init__(self, from_node, to_node, weight, innovation_no):
        self.from_node = from_node  # The node where the connection starts
        self.to_node = to_node  # The node where the connection ends
        self.weight = weight  # The weight of the connection
        self.enabled = True  # Whether this connection is enabled
        self.innovation_no = innovation_no  # The innovation number to track genome changes

    def mutate_weight(self):
        """Mutates the weight of the connection."""
        if random.random() < 0.1:  # 10% chance to completely change the weight
            self.weight = random.uniform(-1, 1)
        else:  # Slightly adjust the weight
            self.weight += random.gauss(0, 1) / 50
            # Clamp the weight between -1 and 1
            self.weight = max(min(self.weight, 1), -1)

    def clone(self, from_node, to_node):
        """Returns a copy of this connectionGene with the same weight and innovation number."""
        clone = ConnectionGene(from_node, to_node, self.weight, self.innovation_no)
        clone.enabled = self.enabled
        return clone
