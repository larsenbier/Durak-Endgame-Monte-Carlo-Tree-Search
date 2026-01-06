from durak import TransferDurak
from durak import HumanPlayer
from search import MCTS
from durak import clearScreen

###################################################################
#                       Global Constants                          #
###################################################################

NUMBER_OF_PLAYERS : int = 2 # number of players in the game
NUMBER_OF_HUMANS : int = 1 # number of human players to control in the game
NUM_MCTS_PLAYOUTS : int = 250 # number of games MCTS simulates to make a move

###################################################################
#                       Playing Function                          #
###################################################################

def humanPlay(game : TransferDurak):
    """
    Call on game to play the game as a human player, providing input for each of the human players in the game.
    
    :param game: game to play
    :type game: TransferDurak
    """
    human_player = game.players[0]
    while not game.isTerminal():
        # get player info
        player = game.getCurrentPlayer()
        player_idx = game.attacker_pos if game.is_attacker_move else game.defender_pos

        # display game
        clearScreen()
        game.show(human_player, hide_other_hands = True)

        # choose player action
        if type(player) is HumanPlayer:
            a = player.chooseAction()
        else:
            key = input(f'\nPress enter to begin P{player_idx} AI move...')
            # if there is only one action, do not run MCTS
            actions = player.actions() 
            if len(actions) == 1:
                a = actions[0]
            # if we are NOT in the endgame, do not run MCTS
            elif len(game.talon) > 4:
                a = player.chooseActionHeuristic()
            else:
                a = MCTS(game, num_iterations = NUM_MCTS_PLAYOUTS)

        # update display info
        game.last_move_str = game.getMoveString(a, player_idx)
        game.last_player = game.getCurrentPlayerNumber()
        game.last_move = a

        # transition game to next state
        last_round = game.round
        game.transition(a)

        # restock hands after end of round
        if game.round > last_round:
            game.restockHands()

    clearScreen()
    game.show(human_player, hide_other_hands = True)
    print(f'Durak: P{game.player_numbers[0]}')



game = TransferDurak(num_players = NUMBER_OF_PLAYERS, num_humans = NUMBER_OF_HUMANS)
humanPlay(game)