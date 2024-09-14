import math

class Node:
    def __init__(self, number):
        self.number = number
        self.input_sum = 0  # current sum, before activation
        self.output_value = 0  # after activation function is applied
        self.output_connections = []  # list of connections (connectionGene)
        self.layer = 0

    # The node sends its output to the inputs of the nodes it's connected to
    def engage(self):
        if self.layer != 0:  # No sigmoid for the input and bias layers
            self.output_value = self.sigmoid(self.input_sum)

        for connection in self.output_connections:
            if connection.enabled:
                connection.to_node.input_sum += connection.weight * self.output_value

    # Sigmoid activation function
    @staticmethod
    def sigmoid(x):
        # Clamp the input value to avoid overflow errors
        x = max(-60, min(60, x))  # Limit x to be between -60 and 60
        return 1 / (1 + math.exp(-4.9 * x))

    # Returns whether this node is connected to the parameter node
    def is_connected_to(self, node):
        if self.layer == node.layer:  # Nodes in the same layer cannot be connected
            return False

        # If the node is in a layer before this one, check if there's a connection to this node
        if node.layer < self.layer:
            for connection in node.output_connections:
                if connection.to_node == self:
                    return True
        else:  # If the node is in a layer after this one, check for outgoing connections
            for connection in self.output_connections:
                if connection.to_node == node:
                    return True

        return False

    # Returns a copy of this node
    def clone(self):
        clone = Node(self.number)
        clone.layer = self.layer
        return clone
