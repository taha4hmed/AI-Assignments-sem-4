import math
import random

class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0
        self.untried_actions = state.get_legal_moves()

def mcts(root_state, iterations):
    root_node = Node(root_state)

    for _ in range(iterations):
        node = selection(root_node)
        
        if not node.state.is_terminal()[0]:
            node = expansion(node)
            
        reward = simulation(node.state)
        backpropagation(node, reward)

    best_child = max(root_node.children, key=lambda c: c.visits)
    return best_child.action

def selection(node):
    while node.untried_actions == [] and node.children != []:
        node = max(node.children, key=ucb1)
    return node

def ucb1(node):
    if node.visits == 0:
        return float('inf')
    return (node.value / node.visits) + math.sqrt(2 * math.log(node.parent.visits) / node.visits)

def expansion(node):
    action = random.choice(node.untried_actions)
    node.untried_actions.remove(action)
    next_state = node.state.make_move(action)
    child_node = Node(next_state, parent=node, action=action)
    node.children.append(child_node)
    return child_node

def simulation(state):
    current_state = state
    while not current_state.is_terminal()[0]:
        action = random.choice(current_state.get_legal_moves())
        current_state = current_state.make_move(action)
    return current_state.is_terminal()[1]

def backpropagation(node, reward):
    while node is not None:
        node.visits += 1
        node.value += reward
        node = node.parent
