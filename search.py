from durak import TransferDurak
import random
import time
import math

###################################################################
#        			       Node Class		      	              #
###################################################################

class Node:
    def __init__(self, action, parent, player : int):
        """
        Docstring for __init__
        
        :param self: Description
        :param action: the action used to reach this node from the parent
        :param parent: the parent node
        :param player: the number of the player who took the action leading to this state
        :type player: int
        """
        self.parent = parent
        self.action = action
        self.children = []
        self.player = player

        self.N : float = 0.0
        self.U : float = 0.0

    def UCB1(self) -> float:
        """
        Upper confidence bound for trees used in selecting nodes during MCTS.
        
        :param self: Description
        :return: Description
        :rtype: float
        """
        if self.N == 0.0:
            return float('inf')
        C = math.sqrt(2)
        return self.U / self.N + C * math.sqrt(math.log(self.parent.N) / self.N)

###################################################################
#               Monte Carlo Tree Search Functions                 #
###################################################################

def selectNode(root: Node, state : TransferDurak) -> tuple[Node, TransferDurak]:
    # choose the root if its terminal
	if state.isTerminal():
		return root, state

    # stop if node not fully expanded
	possible_actions = state.actions()
	if len(root.children) < len(possible_actions):
		return root, state

	# recursively select best UCB child
	best_child = max(root.children, key = lambda c: c.UCB1())
	state.transition(best_child.action)
	return selectNode(best_child, state)


def backprop(leaf: Node, loser : int):
	"""
	Backpropagates the win all the way up the Monte Carlo search tree.
	
	:param leaf: The leaf node we simulated the win from.
	:type leaf: Node
	:param loser: The loser resulting from playout.
	:type losert: int
	"""
	if loser == leaf.player: # penalize losses
		leaf.U -= 1
	if loser != leaf.player : # reward wins
		leaf.U += 1
	leaf.N += 1 # add to total visits
	if leaf.parent is not None: # recusrively update along branch of tree until reaching the root
		backprop(leaf.parent, loser)
		

def updateSearchTree(root: Node, s: TransferDurak):
	"""
	Performs one update step of Monte Carlo tree search.
	
	:param root: The root of the Monte Carlo search tree.
	:type root: Node
	:param s: The state corresponding to the root of the Monte Carlo Search tree.
	:type s: State
	"""
	# select node
	node, state = selectNode(root, TransferDurak(s))

	# generate a new child (or skip if we selected a terminal node)
	if not state.isTerminal():
		visited_actions = {c.action for c in node.children}
		unvisited_actions = [a for a in state.actions() if a not in visited_actions]
		a = random.choice(unvisited_actions)
		state.transition(a) # update state to correspond to generated child
		leaf = Node(action = a, parent = node, player = state.last_player) # generate child node and add to tree ## FIX TO GET PROPER INDEX OF PLAYER
		node.children.append(leaf) # add child to its parent's list of children
	else:
		leaf = node
	
	# determine winner through random play
	winner = simulatePlayout(state)

	# update search tree
	backprop(leaf, winner)

	# remove reference to the state
	del state
	

def randomPlayout(s : TransferDurak) -> int:
	"""
	Samples a game from the belief state, then performs a random playout of the game.
	
	:param s: game state.
	:type s: TransferDurak
	:return: The number of the durak
	:rtype: int
	"""
	state = s.sampleBelief() # get a sample of the game from the belief state
	while not state.isTerminal():
		player = state.getCurrentPlayer()
		player_idx = state.attacker_pos if state.is_attacker_move else state.defender_pos
		
		a = random.choice(player.actions())
		state.last_move_str = state.getMoveString(a, player_idx)
		state.last_player = state.getCurrentPlayerNumber()
		state.last_move = a

		last_round = state.round
		state.transition(a)

		if state.round > last_round:
			state.restockHands() # Only restock at the end of a round

	return state.player_numbers[0] # this is the index of the durak


def heuristicPlayout(s: TransferDurak) -> int:
	"""
	Samples a game from the belief state, then performs a playout of the game according to player.chooseActionHeuristic
	
	:param s: game state.
	:type s: TransferDurak
	:return: The number of the durak
	:rtype: int
	"""
	state = s.sampleBelief() # get a sample of the game from the belief state
	while not state.isTerminal():
		player = state.getCurrentPlayer()
		player_idx = state.attacker_pos if state.is_attacker_move else state.defender_pos
		
		a = player.chooseActionHeuristic()
		state.last_move_str = state.getMoveString(a, player_idx)
		state.last_player = state.getCurrentPlayerNumber()
		state.last_move = a

		last_round = state.round
		state.transition(a)

		if state.round > last_round:
			state.restockHands() # Only restock at the end of a round

	return state.player_numbers[0] # this is the index of the durak


def epsilonLowestActionPlayout(s: TransferDurak, eps: float = 0.1) -> int:
	"""
	Samples a game from the belief state, then performs a playout of the game according to player.chooseActionHeuristic with an epsilon probability of choosing a random action
	
	:param s: game state.
	:type s: TransferDurak
	:return: The number of the durak
	:rtype: int
	"""
	state = s.sampleBelief() # get a sample of the game from the belief state
	while not state.isTerminal():
		player = state.getCurrentPlayer()
		player_idx = state.attacker_pos if state.is_attacker_move else state.defender_pos

		# choose a random action with probability epsilon
		if random.random() < eps:
			a = random.choice(player.actions())
		else:
			a = player.chooseActionHeuristic()

		state.last_move_str = state.getMoveString(a, player_idx)
		state.last_player = state.getCurrentPlayerNumber()
		state.last_move = a

		last_round = state.round
		state.transition(a)

		if state.round > last_round:
			state.restockHands() # Only restock at the end of a round

	return state.player_numbers[0] # this is the index of the durak


def simulatePlayout(s: TransferDurak):
	"""
	Method of playout used in MCTS to simulate games.
	
	:param s: Description
	:type s: TransferDurak
	"""
	return heuristicPlayout(s)


def MCTS(s: TransferDurak, num_iterations = None, time_limit = None):
	"""
	Performs Monte Carlo tree search from state s to determine the next move.
	
	:param s: The game state to search from.
	:type s: State
	:param num_iterations: Maximum number of iterations to search for, or None if using time constraint.
	:param time_limit: Maximum time to search for, or None if using iteration constraint.
	:return: The best action according to MCTS.
	:rtype: int
	"""
	# input control
	if num_iterations is None and time_limit is None:
		raise ValueError('one of num_iterations or time_limit must not be None')
	if num_iterations is not None and time_limit is not None:
		raise ValueError('one of num_iterations and time_limit must be None')
	
	# root of the search tree
	# each node's player is the player who sent the game to that state (the last person who played)
	root = Node(action = 'root' if s.last_move is None else s.last_move, parent = None, player = s.last_player)

	# iteration based constraint
	if num_iterations is not None:
		for i in range(num_iterations):
			updateSearchTree(root, s)

	# time based constraint
	if time_limit is not None:
		start = time.time()
		while time.time() - start < time_limit:
			updateSearchTree(root, s)

	# get the most visited child of the root
	visits = {}
	max_visits = -float('inf')
	max_idx = None
	for i,c in enumerate(root.children):
		visits[c.action] = c.N
		if c.N > max_visits:
			max_idx = i
			max_visits = c.N
	return root.children[max_idx].action


