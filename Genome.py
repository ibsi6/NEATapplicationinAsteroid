import random
import math
import pygame
from pygame.math import Vector2
from Node import Node  
from connectionGene import ConnectionGene


class Genome:
    def __init__(self, inputs, outputs, is_crossover=False):
        self.genes = []  # List of connectionGene
        self.nodes = []  # List of Node
        self.inputs = inputs
        self.outputs = outputs
        self.layers = 2
        self.nextNode = 0
        self.biasNode = None
        self.network = []  # List of Node, the network to process feedforward

        if not is_crossover:
            self._initialize_nodes_and_genes()

    def _initialize_nodes_and_genes(self):
        localNextConnectionNumber = 0

        # Create input nodes
        for i in range(self.inputs):
            node = Node(i)
            node.layer = 0
            self.nodes.append(node)
            self.nextNode += 1

        # Create output nodes
        for i in range(self.outputs):
            node = Node(i + self.inputs)
            node.layer = 1
            self.nodes.append(node)
            self.nextNode += 1

        # Add bias node
        bias_node = Node(self.nextNode)
        bias_node.layer = 0
        self.nodes.append(bias_node)
        self.biasNode = self.nextNode
        self.nextNode += 1

        # Connect inputs to outputs
        for i in range(self.inputs):
            for j in range(self.outputs):
                self.genes.append(
                    ConnectionGene(self.nodes[i], self.nodes[self.inputs + j], random.uniform(-1, 1), localNextConnectionNumber)
                )
                localNextConnectionNumber += 1

        # Connect bias to outputs
        for i in range(self.outputs):
            self.genes.append(
                ConnectionGene(self.nodes[self.biasNode], self.nodes[self.inputs + i], random.uniform(-1, 1), localNextConnectionNumber)
            )
            localNextConnectionNumber += 1

    def get_node(self, node_number):
        for node in self.nodes:
            if node.number == node_number:
                return node
        return None

    def connect_nodes(self):
        for node in self.nodes:
            node.output_connections.clear()

        for gene in self.genes:
            gene.from_node.output_connections.append(gene)

    def feed_forward(self, input_values):
        # Set input values to input nodes
        for i in range(self.inputs):
            self.nodes[i].output_value = input_values[i]

        # Bias node output is always 1
        self.nodes[self.biasNode].output_value = 1

        # Engage each node in the network (feedforward)
        for node in self.network:
            node.engage()

        # Collect outputs
        output_values = [self.nodes[self.inputs + i].output_value for i in range(self.outputs)]

        # Reset nodes for next feedforward
        for node in self.nodes:
            node.inputSum = 0

        return output_values

    def generate_network(self):
        self.connect_nodes()
        self.network = []
        # Add nodes layer by layer
        for l in range(self.layers):
            for node in self.nodes:
                if node.layer == l:
                    self.network.append(node)

    def add_node(self, innovation_history):
        random_connection = random.randint(0, len(self.genes) - 1)

        while self.genes[random_connection].from_node == self.nodes[self.biasNode]:  # Don't disconnect bias
            random_connection = random.randint(0, len(self.genes) - 1)

        # Disable this connection
        self.genes[random_connection].enabled = False

        # Create new node
        new_node = Node(self.nextNode)
        self.nodes.append(new_node)
        self.nextNode += 1

        # Create new connections
        connection_innovation = self.get_innovation_number(innovation_history, self.genes[random_connection].from_node, new_node)
        self.genes.append(connectionGene(self.genes[random_connection].from_node, new_node, 1, connection_innovation))

        connection_innovation = self.get_innovation_number(innovation_history, new_node, self.genes[random_connection].toNode)
        self.genes.append(connectionGene(new_node, self.genes[random_connection].toNode, self.genes[random_connection].weight, connection_innovation))

        new_node.layer = self.genes[random_connection].from_node.layer + 1

        # Connect bias to new node
        connection_innovation = self.get_innovation_number(innovation_history, self.nodes[self.biasNode], new_node)
        self.genes.append(connectionGene(self.nodes[self.biasNode], new_node, 0, connection_innovation))

        # Check if layers need to be adjusted
        if new_node.layer == self.genes[random_connection].toNode.layer:
            for node in self.nodes:
                if node.layer >= new_node.layer:
                    node.layer += 1
            self.layers += 1

        self.connect_nodes()

    def get_innovation_number(self, innovation_history, from_node, to_node):
        is_new = True
        connection_innovation_number = nextConnectionNo

        for history in innovation_history:
            if history.matches(self, from_node, to_node):
                is_new = False
                connection_innovation_number = history.innovation_number
                break

        if is_new:
            inno_numbers = [gene.innovationNo for gene in self.genes]
            innovation_history.append(connectionHistory(from_node.number, to_node.number, connection_innovation_number, inno_numbers))
            nextConnectionNo += 1

        return connection_innovation_number

    def add_connection(self, innovation_history):
        if self.fully_connected():
            print("Connection failed: fully connected")
            return

        random_node1 = random.randint(0, len(self.nodes) - 1)
        random_node2 = random.randint(0, len(self.nodes) - 1)

        while self.nodes[random_node1].layer == self.nodes[random_node2].layer or self.nodes[random_node1].is_connected_to(self.nodes[random_node2]):
            random_node1 = random.randint(0, len(self.nodes) - 1)
            random_node2 = random.randint(0, len(self.nodes) - 1)

        # Ensure the first random node is before the second in layers
        if self.nodes[random_node1].layer > self.nodes[random_node2].layer:
            random_node1, random_node2 = random_node2, random_node1

        connection_innovation_number = self.get_innovation_number(innovation_history, self.nodes[random_node1], self.nodes[random_node2])
        self.genes.append(connectionGene(self.nodes[random_node1], self.nodes[random_node2], random.uniform(-1, 1), connection_innovation_number))

        self.connect_nodes()

    def fully_connected(self):
        max_connections = 0
        nodes_in_layers = [0] * self.layers

        # Count nodes in each layer
        for node in self.nodes:
            nodes_in_layers[node.layer] += 1

        # Calculate max possible connections
        for i in range(self.layers - 1):
            nodes_in_front = sum(nodes_in_layers[j] for j in range(i + 1, self.layers))
            max_connections += nodes_in_layers[i] * nodes_in_front

        return max_connections == len(self.genes)

    def mutate(self, innovation_history):
        if random.random() < 0.8:  # 80% chance to mutate weights
            for gene in self.genes:
                gene.mutate_weight()

        if random.random() < 0.05:  # 5% chance to add connection
            self.add_connection(innovation_history)

        if random.random() < 0.03:  # 3% chance to add node
            self.add_node(innovation_history)

    def clone(self):
        clone_genome = Genome(self.inputs, self.outputs, True)
        clone_genome.layers = self.layers
        clone_genome.nextNode = self.nextNode
        clone_genome.biasNode = self.biasNode

        for node in self.nodes:
            clone_genome.nodes.append(node.clone())

        for gene in self.genes:
            from_node = clone_genome.get_node(gene.from_node.number)
            to_node = clone_genome.get_node(gene.toNode.number)
            clone_genome.genes.append(gene.clone(from_node, to_node))

        clone_genome.connect_nodes()
        return clone_genome

    def print_genome(self):
        print("Genome Layers:", self.layers)
        print("Bias Node:", self.biasNode)
        print("Nodes:", [node.number for node in self.nodes])
        print("Genes:")
        for gene in self.genes:
            print(f"Gene {gene.innovationNo}, From Node {gene.from_node.number}, To Node {gene.toNode.number}, Weight: {gene.weight}, Enabled: {gene.enabled}")

