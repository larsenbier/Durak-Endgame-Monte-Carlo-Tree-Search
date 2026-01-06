from durak import TransferDurak
from durak import HumanPlayer
from search import MCTS
import random
import pickle

###################################################################
#                  Automated Testing Functions                    #
###################################################################

def heuristicVsMCTS(num_iterations, num_games, num_players) -> list[int]:
    """
    Tests the lowestValueAction heuristic player against the MCTS player.
    If playing with 2 players: P0 is the lowestValueAction player, and P1 is the MCTS player.
    If playing with n players: P0,...,P(n-2) use lowestValueAction, and P(n-1) uses MCTS.
    
    :param num_iterations: number of playouts MCTS does
    :param num_games: number of games to play
    :param num_players: number of heuristic players for MCTS to play against
    :return: A list of the durak for each game. Each entry is the integer associated with the player who was durak
    :rtype: list[int]
    """
    print(f'MCTS vs {num_players - 1} Heuristic Players: AI: {num_iterations} playouts, trials: {num_games}...')
    deciles = [i for i in range(0,10)]
    benchmarks = [(i * num_games) // 10 for i in deciles]
    duraks = []
    decile = 0
    
    for iter in range(num_games):
        game = TransferDurak(num_players = num_players, num_humans = num_players - 1)
        
        # play out game
        while not game.isTerminal():
            # get player info
            player = game.getCurrentPlayer()

            # chosoe player action
            if type(player) is HumanPlayer:
                a, _, _ = player.lowestValueAction(player.actions()) # use simple heuristic as opponent
            else:
                a = MCTS(game, num_iterations = num_iterations)

            # update last player and move
            game.last_player = game.getCurrentPlayerNumber()
            game.last_move = a

            # transition game to next state
            last_round = game.round
            game.transition(a)

            # restock hands after end of round
            if game.round > last_round:
                game.restockHands()
        
        # add durak number to list
        duraks.append(game.player_numbers[0]) 
        
        # print updates
        if iter in benchmarks:
            print(f'{decile}% done - playouts completed: {iter}')
            decile += 10
        
    return duraks

def randomVsMCTS(num_iterations, num_games, num_players) -> list[int]:
    """
    Tests the random player against the MCTS player.
    If playing with 2 players: P0 is the random player, and P1 is the MCTS player.
    If playing with n players: P0,...,P(n-2) use random moves, and P(n-1) uses MCTS.
    
    :param num_iterations: number of playouts MCTS does
    :param num_games: number of games to play
    :param num_players: number of heuristic players for MCTS to play against
    :return: A list of the durak for each game. Each entry is the integer associated with the player who was durak
    :rtype: list[int]
    """

    print(f'MCTS vs {num_players - 1} Random Players: AI: {num_iterations} playouts, trials: {num_games}...')
    deciles = [i for i in range(0,10)]
    benchmarks = [(i * num_games) // 10 for i in deciles]
    duraks = []
    decile = 0
    
    for iter in range(num_games):
        game = TransferDurak(num_players = num_players, num_humans = num_players - 1)
        
        # play out game
        while not game.isTerminal():
            # get player info
            player = game.getCurrentPlayer()

            # chosoe player action
            if type(player) is HumanPlayer:
                a = random.choice(player.actions()) # use player heuristic
            else:
                a = MCTS(game, num_iterations = num_iterations)

            # update last player and move
            game.last_player = game.getCurrentPlayerNumber()
            game.last_move = a

            # transition game to next state
            last_round = game.round
            game.transition(a)

            # restock hands after end of round
            if game.round > last_round:
                game.restockHands()
        
        # add durak number to list
        duraks.append(game.player_numbers[0]) 
        
        # print updates
        if iter in benchmarks:
            print(f'{decile}% done - playouts completed: {iter}')
            decile += 10
        
    return duraks

def randomVsHeuristic(num_games, num_players):
    """
    Tests the lowestValueAction heuristic player against the random player.
    If playing with 2 players: P0 is the lowestValueAction player, and P1 is the random player.
    If playing with n players: P0,...,P(n-2) use lowestValueAction, and P(n-1) is random.
    
    :param num_games: number of games to play
    :param num_players: number of heuristic players for the random agent to play against
    :return: A list of the durak for each game. Each entry is the integer associated with the player who was durak
    :rtype: list[int]
    """
    print(f'random vs {num_players - 1} heuristic Players, trials: {num_games}...')
    deciles = [i for i in range(0,10)]
    benchmarks = [(i * num_games) // 10 for i in deciles]
    duraks = []
    decile = 0
    
    for iter in range(num_games):
        game = TransferDurak(num_players = num_players, num_humans = num_players - 1)

        # play out game
        while not game.isTerminal():
            # get player info
            player = game.getCurrentPlayer()

            # chosoe player action
            if type(player) is HumanPlayer:
                a, _, _ = player.lowestValueAction(player.actions()) # use simple heuristic as opponent
            else:
                a = random.choice(player.actions()) # bot uses random

            # update last player and move
            game.last_player = game.getCurrentPlayerNumber()
            game.last_move = a

            # transition game to next state
            last_round = game.round
            game.transition(a)

            # restock hands after end of round
            if game.round > last_round:
                game.restockHands()
        
        # add durak number to list
        duraks.append(game.player_numbers[0]) 
        
        # print updates
        if iter in benchmarks:
            print(f'{decile}% done - playouts completed: {iter}')
            decile += 10
        
    return duraks

def heuristicVsHybrid(num_iterations, num_games, num_players):
    """
    Tests the lowestValueAction heuristic player against the Hybrid player.
    If playing with 2 players: P0 is the lowestValueAction heuristic, and P1 is the Hybrid player.
    If playing with n players: P0,...,P(n-2) use lowestValueAction, and P(n-1) uses Hybrid moves.
    
    :param num_iterations: number of playouts MCTS does
    :param num_games: number of games to play
    :param num_players: number of heuristic players for MCTS to play against
    :return: A list of the durak for each game. Each entry is the integer associated with the player who was durak
    :rtype: list[int]
    """
    print(f'Hybrid vs {num_players - 1} heuristic Players, trials: {num_games}...')
    deciles = [i for i in range(0,10)]
    benchmarks = [(i * num_games) // 10 for i in deciles]
    duraks = []
    decile = 0
    
    for iter in range(num_games):
        game = TransferDurak(num_players = num_players, num_humans = num_players - 1)

        # play out game
        while not game.isTerminal():
            # get player info
            player = game.getCurrentPlayer()

            # choose player action
            if type(player) is HumanPlayer:
                a, _, _ = player.lowestValueAction(player.actions()) # use simple heuristic as opponent
            else:
                actions = player.actions() # if there is only one action, do not run MCTS
                if len(actions) == 1:
                    a = actions[0]
                elif len(game.talon) > 4:
                    a = player.chooseActionHeuristic()
                else:
                    a = MCTS(game, num_iterations = num_iterations)

            # update last player and move
            game.last_player = game.getCurrentPlayerNumber()
            game.last_move = a

            # transition game to next state
            last_round = game.round
            game.transition(a)

            # restock hands after end of round
            if game.round > last_round:
                game.restockHands()
        
        # add durak number to list
        duraks.append(game.player_numbers[0]) 
        
        # print updates
        if iter in benchmarks:
            print(f'{decile}% done - playouts completed: {iter}')
            decile += 10
        
    return duraks


###################################################################
#                  Writing Test Data Example                      #
###################################################################

# This code was used to generate the random vs hybrid test data.
# an equivalent outline was used for the other test scenarios.

# num_iters = [10, 100, 200, 500, 700, 1000]
# num_games = [100,100, 100, 100, 100, 100 ]
# # print(f'Hybrid win rate vs random:')
# for i in range(len(num_iters)):
#     duraks = heuristicVsHybrid(num_iters[i], num_games[i], num_players = 2) # WRITING
#     file_path = f'trials/heuristicVsHybrid_iters{num_iters[i]}_trails{num_games[i]}_players{2}.pkl'
#     with open(file_path, 'wb') as file: # WRITING
#         pickle.dump(duraks, file) # WRITING


###################################################################
#                       Reading Test Data                         #
###################################################################

graph = {}

# random vs MCTS
num_iters = [10, 100, 200, 500, 700, 1000]
num_games = [100,100, 100, 100, 100, 100]
# print(f'MCTS win rate vs random:')
graph['MCTS_random'] = []
for i in range(len(num_iters)):
    # duraks = randomVsMCTS(num_iters[i], num_games[i], num_players = 2) # WRITING
    file_path = f'trials/randomVsMSCTS_iters{num_iters[i]}_trails{num_games[i]}_players{2}.pkl'
    # with open(file_path, 'wb') as file: # WRITING
    #     pickle.dump(duraks, file) # WRITING
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    win_rate = len([d for d in data if d == 0]) / len(data)
    # print(f'\t{num_iters[i]} iters: {win_rate}')
    graph['MCTS_random'].append(win_rate)

# heuristic vs MCTS
num_iters = [10, 100, 200, 500, 700, 1000]
num_games = [100,100, 100, 100, 100, 100]
# print(f'MCTS win rate vs heuristic:')
graph['MCTS_heuristic'] = []
for i in range(len(num_iters)):
    file_path = f'trials/heuristicVsMSCTS_iters{num_iters[i]}_trails{num_games[i]}_players{2}.pkl'
    # with open(file_path, 'wb') as file: # WRITING
    #     pickle.dump(duraks, file) # WRITING
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    win_rate = len([d for d in data if d == 0]) / len(data)
    # print(f'\t{num_iters[i]} iters: {win_rate}')
    graph['MCTS_heuristic'].append(win_rate)

# heuristic vs hybrid
num_iters = [10, 100, 200, 500, 700, 1000]
num_games = [100,100, 100, 100, 100, 100]
# print(f'Hybrid win rate vs heuristic:')
graph['hybrid_heuristic'] = []
for i in range(len(num_iters)):
    file_path = f'trials/heuristicVsHybrid_iters{num_iters[i]}_trails{num_games[i]}_players{2}.pkl'
    # with open(file_path, 'wb') as file: # WRITING
    #     pickle.dump(duraks, file) # WRITING
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    win_rate = len([d for d in data if d == 0]) / len(data)
    # print(f'\t{num_iters[i]} iters: {win_rate}')
    graph['hybrid_heuristic'].append(win_rate)

# heuristic vs random
print(f'random win rate vs heuristic:', end = '')
file_path = f'trials/randomVsHeuristic_players{2}.pkl'
with open(file_path, 'rb') as file:
    data = pickle.load(file)
win_rate = len([d for d in data if d == 0]) / len(data)
# print(f'\t: {win_rate}')
graph['heuristic_random'] = [(1 - win_rate) for i in num_iters]

print(graph)
# x_axis = [10, 100, 200, 500, 700, 1000]
# import matplotlib.pyplot as plt
# names = ['Pure MCTS v Random', 'Pure MCTS v Heuristic', 'Hybrid v Heuristic', 'Heuristic v Random']
# for i, (label,key) in enumerate(graph.items()):
#     plt.plot(x_axis, key, label = names[i])
# plt.minorticks_on()
# plt.grid(True, which="major", linewidth=0.8)
# plt.grid(True, which="minor", linewidth=0.3, alpha=0.5)
# plt.xlabel("# Playouts")
# plt.ylabel("Player 1 Win Rate")
# plt.title('Durak Agent Win Rates')
# plt.legend()
# plt.show()
