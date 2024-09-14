from Genome import Genome
from Node import Node

class ConnectionHistory:
    def __init__(self, from_node, to_node, innovation_number, innovation_numbers):
        self.from_node = from_node  # ID of the starting node of the connection
        self.to_node = to_node  # ID of the ending node of the connection
        self.innovation_number = innovation_number  # Innovation number of this connection
        self.innovation_numbers = innovation_numbers[:]  # Copy of the list of innovation numbers for the genome

    def matches(self, genome, from_node, to_node):
        """
        Returns whether the genome matches the original genome and the connection is between the same nodes.
        """
        if len(genome.genes) == len(self.innovation_numbers):  # Check if the number of connections is the same
            if from_node.number == self.from_node and to_node.number == self.to_node:
                # Check if all innovation numbers match
                for gene in genome.genes:
                    if gene.innovation_no not in self.innovation_numbers:
                        return False
                return True
        return False
