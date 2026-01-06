import random
import os
import copy

###################################################################
#                         Global Constants                        #
###################################################################

# parameterize number of suits
SUITS : int = 4 # spade, club, heart, diamond
RANKS : int = 9 # 9 corresponds to removing 2 through 5 (the way Durak is traditionally played)
HAND_SIZE : int = 6 # number of cards the player is supposed to draw to during early game

# printing normal durak game        # Number of Suit
SPADE : str = '\u2660'              # 0
CLUB: str = '\u2663'                # 1
HEART : str = '\u2665'              # 2
DIAMOND : str = '\u2666'            # 3
HIDDEN: str = '\u25A0'              # N/A

RED_COLOR : str = '\033[91m'
BLUE_COLOR : str = '\033[94m'
YELLOW_COLOR : str = '\033[93m'
ORANGE_COLOR :str = '\033[38;2;255;165;0m'
RESET_COLOR : str = '\033[0m'

# controls whether all player hands are displayed
OMNISCIENT_GAME : bool = False

# lists used for printing the Card class when SUITS == 4 and RANKS in [9, 13]
SUITMAP = [SPADE, CLUB, HEART, DIAMOND]
COLORMAP = [BLUE_COLOR, BLUE_COLOR, RED_COLOR, RED_COLOR]

###################################################################
#                           Card Class                            #
###################################################################

# Card class used as backbone of Durak game
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit


    def __str__(self) -> str:
        # full deck of 13 ranks
        if SUITS == 4 and RANKS == 13:
            rankmap = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] # convention is ace is highest number
            return f'{COLORMAP[self.suit]}{rankmap[self.rank]}{SUITMAP[self.suit]}{RESET_COLOR}'
        # remove 2,3,4,5
        if SUITS == 4 and RANKS == 9:
            rankmap = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] # convention is ace is highest number
            return f'{COLORMAP[self.suit]}{rankmap[self.rank]}{SUITMAP[self.suit]}{RESET_COLOR}'
        return f'({self.rank},{self.suit})'


    def __repr__(self) -> str:
        return str(self)


    def __eq__(self, other) -> bool:
        return self.rank == other.rank and self.suit == other.suit
    

    def __hash__(self):
        return hash((self.rank,self.suit))


    def strLen(self):
        if SUITS == 4 and RANKS == 9:
            if self.rank == 4: # index of 10 in rankmap
                return 3
            else:
                return 2
        if SUITS == 4 and RANKS == 13:
            if self.rank == 8: # index of 10 in rankmap
                return 3
            else:
                return 2
        else:
            return (self.rank // 10) + (self.suit // 10) + 2 + 3 # +2 is for base length, +3 is for tuple formatting, others are for having more than one digit in rank or suit

###################################################################
#                         Durak Classes                           #
###################################################################


class TransferDurak:
    def __init__(self, other = None, num_players: int = 2, num_humans = 1):
        """
        Docstring for __init__
        
        :param self: Description
        :param other: pass other if you want to copy the data of other. The new TransferDurak instance will be completely independent of the original
        :param num_players: the number of players in the game.
        :type num_players: int
        """
        if other is None:
            if num_players < 2:
                raise ValueError('Must have at least 2 players.')    
            
            # player setup
            self.player_numbers = [i for i in range(num_players)] # tracks the indices of the remaining players
            self.players = [HumanPlayer(game = self, position = i) for i in range(0, num_humans)] + [Player(game = self, position = i) for i in range(num_humans, num_players)]
            self.initPlayerHandBeliefs() 

            # other variables
            self.last_move_str = ''
            self.last_move = None
            self.last_player = None
            self.attack_cards = []
            self.defense_cards = []
            self.talon = self.generateTalon()
            self.discard = set()
            self.last_attack = set()
            self.last_defense = set()
            self.is_attacker_move = True
            self.defender_eating = False
            self.attacker_pos = 0 # index in self.players of the attacker
            self.defender_pos = 1 # index in self.players of the defender
            self.round = 0 # a round is one full cycle of attack and defense
            self.trump = random.randint(0, SUITS - 1)
            
            self.deal()


        else: # copy construcor. Carefully copy data without referencing old game
            
            self.player_numbers = copy.deepcopy(other.player_numbers)

            self.players = []
            for i,p in enumerate(other.players):
                if type(p) is HumanPlayer:
                    self.players.append(HumanPlayer(self, p.position))
                else:
                    self.players.append(Player(self, p.position))
                self.players[i].hand = copy.deepcopy(p.hand)
                self.players[i].hand_beliefs = copy.deepcopy(p.hand_beliefs)
                self.players[i].talon_belief = copy.deepcopy(p.talon_belief)
            
            self.last_move_str = copy.deepcopy(other.last_move)
            self.last_move = copy.deepcopy(other.last_move)
            self.last_player = other.last_player
            self.attack_cards = copy.deepcopy(other.attack_cards)
            self.defense_cards = copy.deepcopy(other.defense_cards)
            self.talon = copy.deepcopy(other.talon)
            self.discard = copy.deepcopy(other.discard)
            self.last_attack = copy.deepcopy(other.last_attack)
            self.last_defense = copy.deepcopy(other.last_defense)
            self.is_attacker_move = other.is_attacker_move
            self.defender_eating = other.defender_eating
            self.attacker_pos = other.attacker_pos
            self.defender_pos = other.defender_pos
            self.round = other.round
            self.trump = other.trump


    def getAttackGraphic(self):
        message = ''
        border = ' --------------------------------------------------------------------------'
        num_chars = len(border)

        # top border
        message += (border + '\n')
        
        # line in between
        message += ('|' + ' ' * (num_chars - 1) + '|\n')
        
        # attack and defense row prefix
        prefix = '| XXX: '

        # attack string
        attack = self.attack_cards
        message += '| Att: '
        available_spaces = num_chars
        available_spaces -= len(prefix)
        attack_str = ''
        for card in attack:
            attack_str += (str(card) + (' ' * (5 - card.strLen())))
            available_spaces -= 5
        message += attack_str + (' ' * (available_spaces) + '|\n')

        # line in between
        message += ('|' + ' ' * (num_chars - 1) + '|\n')

        # defense string
        defense = self.defense_cards
        message += '| Def: '
        available_spaces = num_chars
        available_spaces -= len(prefix)
        defense_str = ''
        for card in defense:
            defense_str += (str(card) + (' ' * (5 - card.strLen())))
            available_spaces -= 5
        message += defense_str + (' ' * (available_spaces) + '|\n')

        # line in between
        message += ('|' + ' ' * (num_chars - 1) + '|\n')

        # bottom border
        message += border
    
        return message


    def getTalonLastMoveAndOrderGraphic(self):
        # border box top lines
        message = ''
        talon_border = ' --------------'
        order_border = ' ----------' + '-----' * len(self.players)
        last_move_border = '--------------------------------------'

        message += (talon_border + ' ' * 4 + order_border + ' ' * 5 + last_move_border + '\n')
        
        # talon box line 1
        message += (f'| Talon: {len(self.talon)}' + ' ' * (len(talon_border) - 9 - len(str(len(self.talon)))) + '|')
    
        # order box line 1
        message += ' ' * 3
        order_start = f'| Order: P{self.players[0].position}'
        start_len = len(order_start)
        if self.player_numbers[self.attacker_pos] == self.players[0].position:
            order_start = f'| Order: {YELLOW_COLOR}P{self.players[0].position}{RESET_COLOR}'
        elif self.player_numbers[self.defender_pos] == self.players[0].position:
            order_start = f'| Order: {ORANGE_COLOR}P{self.players[0].position}{RESET_COLOR}'
        available_chars = len(order_border)
        available_chars -= start_len
        message += order_start
        for player in self.players[1:]:
            if self.player_numbers[self.attacker_pos] == player.position: # color the attacker yellow
                message += f' \u2192 {YELLOW_COLOR}P{player.position}{RESET_COLOR}'
            elif self.player_numbers[self.defender_pos] == player.position: # color the attacker yellow
                message += f' \u2192 {ORANGE_COLOR}P{player.position}{RESET_COLOR}'
            else:
                message += f' \u2192 P{player.position}'
            available_chars -= (4 + len(str(player.position)))
        message += ' ' * available_chars + '|'

        # last move box line 1
        message += ' ' * 3
        available_chars = len(last_move_border)
        last_move_start = f'| Last Move'
        message += last_move_start
        available_chars -= len(last_move_start)
        message += ' ' * (available_chars + 1) + '|\n'

        # talon box line 2
        if SUITS == 4:
            message += (f'| Trump: {COLORMAP[self.trump]}{SUITMAP[self.trump]}{RESET_COLOR}' + ' ' * (len(talon_border) - 10) + '|')

        # order box line 2
        message += ' ' * 3 + '|'
        available_chars = len(order_border)
        message += ' ' * (available_chars - 1) + '|'

        # last move box line 3
        message += ' ' * 3
        available_chars = len(last_move_border)
        last_move_start = f'| {self.last_move_str}'
        message += last_move_start
        available_chars -= self.getMoveStringLen(self.last_move, self.last_player)
        message += ' ' * (available_chars - 1) + '|\n'
        

        # bottom borders
        message += (talon_border + ' ' * 4 + order_border + ' ' * 5 + last_move_border + '\n')


        return message


    def getHandGraphic(self, player, hide_cards):
        message = ''
        border = (' ---------' + ('----' * (len(player.hand) - 2)))
        num_chars = len(border)
    
        message += (border + '\n')
        midsection = f'P{player.position} Hand'
        message += ('|' + (' ' * ((num_chars - len(midsection)) // 2)) + midsection + (' ' * ((num_chars - len(midsection)) // 2)) + '|\n')

        available_spaces = num_chars
        hand_str = f'| '
        available_spaces -= len(hand_str)

        # show cards to human player
        if hide_cards: # hide cards from human player
            for card in player.hand:
                hand_str += ('\u25A0' + '  ' )
                available_spaces -= 3
            message += hand_str + (' ' * (available_spaces) + '|\n')
        else:
            for card in player.hand:
                hand_str += (str(card) + ' ' )
                available_spaces -= (card.strLen() + 1)
            message += hand_str + (' ' * (available_spaces) + '|\n')
        
    
        message += border

        return message


    def show(self, player, hide_other_hands):
        """
        Shows the game state from the player's perspective.
        
        :param self: Description
        :param player: Player to display the game state for
        :param player: Controls whether hands NOT belonging to player should reveal their cards
        """
        for p in self.players:
            if player is p:
                print(self.getHandGraphic(p, hide_cards = False))
            else:
                print(self.getHandGraphic(p, hide_cards = hide_other_hands))
       
        print(self.getTalonLastMoveAndOrderGraphic())
        print(self.getAttackGraphic())


    def showOmniscient(self): 
        """
        Displays a comprehensive panel of info about the current gamestate.
        Includes information that would be invisible to a real player.
        
        :param self: Description
        """
        # show hands
        print(f'Trump Suit: {COLORMAP[self.trump]}{SUITMAP[self.trump]}{RESET_COLOR}')
        # print(f'Top 3 Talon Cards: {self.talon[-3:]}')
        print(f'Talon Size: {len(self.talon)}')
        print(f'Round Number: {self.round}')
        print('\nHands:')
        for i,player in enumerate(self.players):
            print(f'\tP{self.player_numbers[i]}: ( {player.showHand()})')

        # show previous move
        print(f'Last Move:\n\t{self.last_move_str}')

        # show attack and defense
        attack_str = 'Attack:\n'
        for card in self.attack_cards:
            attack_str += ('\t' + str(card))
        print(attack_str)
        defense_str = 'Defense:\n'
        for card in self.defense_cards:
            defense_str += ('\t' + str(card))
        print(defense_str)


        # show previous attack and defense
        attack_str = '\nLast Attack:\n'
        for card in self.last_attack:
            attack_str += ('\t' + str(card))
        print(attack_str)
        defense_str = 'Last Defense:\n'
        for card in self.last_defense:
            defense_str += ('\t' + str(card))
        print(defense_str)

        print(f'Attacker position: {self.attacker_pos}')
        print(f'Defender position: {self.defender_pos}')
        print(f'player numbers: {self.player_numbers}')
        print(f'num players: {len(self.players)}')

        # show attacker and defender
        print(f'Attacker: P{self.player_numbers[self.attacker_pos]}')
        print(f'Defender: P{self.player_numbers[self.defender_pos]}')
        print('')

        # show belief states:
        # for i,n in enumerate(self.player_numbers):
        #     p = self.players[i]
        #     print(f'P{n} Hand Belief States: {p.hand_beliefs}')
        # print('')

        # show talon belief states:
        # for i,n in enumerate(self.player_numbers):
        #     p = self.players[i]
        #     print(f'P{n} Talon Belief State: {p.talon_belief}')
        # print('')

        # player who is making a deicision
        # print(f'Acting Player: P{self.player_numbers[self.attacker_pos] if self.is_attacker_move else self.player_numbers[self.defender_pos]} ({"attacker" if self.is_attacker_move else "defender"}) moves: {self.getAttacker().actions() if self.is_attacker_move else self.getDefender().actions()}')


    def initPlayerHandBeliefs(self):
        """
        Initializes all player's hand beliefs to the empty set
        
        :param self: Description
        """
        for player in self.players:
            player.hand_beliefs = [set() for p in self.players]


    def beatsCard(self, d : Card, c : Card) -> bool: 
        if self.isTrump(d):
            if self.isTrump(c):
                if d.rank > c.rank: # d is higher trump
                    return True
                else:
                    return False # c is a higher trump card
            else:
                return True # c is not a trump
        if d.suit == c.suit:
            if d.rank > c.rank:
                return True
    
        return False # d is not a trump and is not the same suit as c, or d's rank is lower than c's


    def allowedAttackerPositions(self) -> list[int]:
        """
        Docstring for allowedAttackerPositions
        
        :param self: TransferDurak instance
        :return: An ordered list of the indices of the allowed attackers. Indices refer to positions in the self.players list.
        :rtype: list[int]
        """
        if len(self.players) < 3:
            return [self.movePosition(self.defender_pos, 1)] # only one possible attacker
        if len(self.players) == 3:
            return [self.movePosition(self.defender_pos, -1), self.movePosition(self.defender_pos, 1)]
        elif len(self.players) == 4:
            return [self.movePosition(self.defender_pos, -1), self.movePosition(self.defender_pos, 1), self.movePosition(self.defender_pos, 2)] # other 3 players attack right, left, across (from defender)
        else: # >= 5 players
            return [self.movePosition(self.defender_pos, 1), self.movePosition(self.defender_pos, -1)] # attackers to either side of the player


    def generateTalon(self):
        talon = []
        for suit in range(SUITS):
            for rank in range(RANKS):
                talon.append(Card(rank, suit))
        random.shuffle(talon) # randomly permute talon
        return talon
    

    def deal(self):
        for i in range(6):
            for player in self.players:
                player.privatePickUp(self.drawFromTalon())

    
    def drawFromTalon(self) -> Card:
        return self.talon.pop(-1)
            
    
    def movePosition(self, pos: int, move: int) -> int:
        """
        Gives the index of moving move positions along the players list (with wrap-around after passing the end of the list)
        
        :param self: game object
        :param pos: the position we start from in the list (must be within index range)
        :type pos: int
        :param move: the number of positions to move
        :type move: int
        :return: the index of advancing move indices from pos with wraparound
        :rtype: int
        """
        return  (pos + move) % len(self.players)
    

    def advanceAttackerPos(self, positions: int):
        """
        Advances the main attacker by "positions" positions
        
        :param self: TransferDurak instance
        :param positions: number of positions to advance the attacker
        :type positions: int
        """
        self.attacker_pos = self.allowedAttackerPositions()[0]
        self.attacker_pos = (self.attacker_pos + positions) % len(self.players)
        self.defender_pos = (self.attacker_pos + 1) % len(self.players)


    def restockHands(self): 
        """
        Restocks the player's hands going CCW starting with the most recent attacker.
        
        :param self: TransferDurak instance.
        """
        # order to restock in (CCW starting with most recent attacker)
        # gets called at the end of a round before advancing the player tracker, so the most recent attacker is the current player
        first_attacker_pos = self.allowedAttackerPositions()[0]
        restock_order = [(first_attacker_pos - i) % len(self.players) for i in range(len(self.players))]
        for i in restock_order:
            p = self.players[i]
            while len(p.hand) < HAND_SIZE and len(self.talon) > 0: # draw from talon until hands full or talon empty
                p.privatePickUp(self.drawFromTalon())


    def isTrump(self, c : Card):
        return c.suit == self.trump


    def getAttacker(self):
        return self.players[self.attacker_pos]
    

    def getDefender(self):
         return self.players[self.defender_pos]
    

    def passAttack(self):
        """
        Modifies self.attacker_pos to be the next allowed attacker.
        ONLY CALL WHEN PASSING IS ALLOWED. Otherwise, passAttack() will fail catastrophically.
        :param self: TransferDurak instance
        """
        eligible = self.allowedAttackerPositions() # list of allowed attackers
        cur_idx = eligible.index(self.attacker_pos) # index of current attacker in the list of allowed attackers
        self.attacker_pos = eligible[cur_idx + 1] # next allowed attacker in the list


    def transition(self, a: tuple):
        """
        Transitions the game through action a.
        Modifies the game in place.
        
        :param self: TransferDurak instance
        :param a: action taken
        :type a: tuple
        """
        # attacker transitions
        a_type, cards = a
        player = self.getCurrentPlayer()
        self.last_player = self.getCurrentPlayerNumber()
        if player.position == self.player_numbers[self.attacker_pos]:
            if not self.defender_eating: # part of the main attack phase (before the defender eats)
                if a_type == 'p': # pass attack to next eligible attacker (a == p only if this is possible)
                    self.passAttack()
                    self.is_attacker_move = True # next attacker goes
                    
                elif a_type == 'r': # the attack rides (block next attackers). Clears all cards involved in attack
                    self.discard = self.discard.union(set(self.attack_cards)) # add attack cards to discard
                    self.discard = self.discard.union(set(self.defense_cards)) # add defense cards to discard
                    self.attack_cards = [] # reset attack
                    self.defense_cards = [] # reset defense
                    self.advanceAttackerPos(1) # defender gets to attack now
                    self.is_attacker_move = True # current defender will attack
                    self.round += 1
                    
                elif a_type == 'a': # add card(s) to the attack
                    player.publicPlay(cards)
                    self.attack_cards += cards
                    self.is_attacker_move = False # defender gets a turn to defend
                    
                
            else: # defender is eating
                if a_type == 'p': # pass attack to next eligible attacker to add to pickup
                    self.passAttack()
                    self.is_attacker_move = True # next attacker goes
                    
                elif a_type == 'b': # block next attackers
                    self.defender_eating = False # set game to attack phase
                    self.is_attacker_move = True # next player attacks
                    self.advanceAttackerPos(2) # skip the defender's turn
                    self.round += 1
                    
                elif a_type == 'a': # add card(s) to the pickup of the defender
                    player.publicPlay(cards)
                    defender = self.getDefender()
                    defender.publicPickUp(cards)
                    self.is_attacker_move = True # defender does NOT get a chance to defend cards added to eat
         

        # defender transitions
        elif player.position == self.player_numbers[self.defender_pos]:
            if a_type == 'e': # eat attack
                self.defender_eating = True # set game to pickup phase for defender
                player.publicPickUp(self.attack_cards + self.defense_cards)
                self.last_attack = self.attack_cards # update the cards players may add to the pickup
                self.last_defense = self.defense_cards # update the cards players may add to the pickup
                self.attack_cards = []
                self.defense_cards = [] 
                self.attacker_pos = self.allowedAttackerPositions()[0] # reset attacker order to beginning for pickups
                # self.advanceAttackerPos(2) # MOVING ATTACKER IS NOW HANDLED BY BLOCK
                self.is_attacker_move = True # eating ==> attacker adds to pickup
                
            elif a_type == 't': # transfer attack (a_type == t only if a transfer is possible)
                player.publicPlay(cards)
                self.attack_cards += cards
                self.advanceAttackerPos(1) # player to the defender's left defends transferred cards
                self.is_attacker_move = False # transferring ==> new defender goes
                
            elif a_type == 'd': # defend the attack
                player.publicPlay(cards)
                self.defense_cards += cards
                self.is_attacker_move = True # attacker may add to attack
                self.attacker_pos = self.allowedAttackerPositions()[0] # reset attacker order to beginning for a successful defense
        self.removeOutPlayers()


    def removeOutPlayers(self):
        """
        Removes players from the game who have no cards

        :param self: TransferDurak instance
        """
        if len(self.talon) == 0:
            for i,p in enumerate(self.players):
                if len(p.hand) < 1:
                    self.player_numbers.pop(i) # remove the index of that player from the list of available indices
                    self.players.pop(i) # remove the player from the list of players

                    # move around attacker and defender indices based on who is removed from the game
                    if self.attacker_pos >= i:
                        self.attacker_pos = (self.attacker_pos - 1) % len(self.players)
                        self.defender_pos = (self.attacker_pos + 1) % len(self.players)
                    elif self.defender_pos == i:
                        self.defender_pos = (self.attacker_pos + 1) % len(self.players)

                    for p in self.players: # update hand beliefs for other players
                        p.hand_beliefs.pop(i)
        

    def isTerminal(self):
        """
        Returns True if and only if the game is in a terminal state (a durak has been decided)
        
        :param self: TransferDurak instance
        """
        if len(self.players) == 1:
            return True
        nonempty_hands = 0
        for p in self.players:
            if len(p.hand) > 0:
                nonempty_hands += 1
        return nonempty_hands <= 1


    def getMoveStringLen(self, a, player) -> int:
        if a is None:
            return 0
        message = f'P{player} '
        a_type, cards = a
        if a_type == 'e':
            message += 'ate'
            return len(message)
        elif a_type == 'b':
            message += 'blocked additions to the pickup'
            return len(message)
        elif a_type == 't':
            message += 'tranferred '
            message_len = len(message)
            for c in cards:
                message_len += (c.strLen() + 1)
            return message_len
        elif a_type == 'd':
            message += 'defended with '
            message_len = len(message)
            for c in cards:
                message_len += (c.strLen() + 1)
            return message_len
        elif a_type == 'r':
            message += 'rides'
            return len(message)
        elif a_type == 'p':
            attacker_positions = self.allowedAttackerPositions()
            attacker_idx = attacker_positions.index(player)
            if self.defender_eating:
                message += f'passed the additions to P{attacker_positions[attacker_idx + 1]}'
            else:
                message += f'passed the attack to P{attacker_positions[attacker_idx + 1]}'
            return len(message)
        else: #a_type == 'a': (an attack)
            if self.defender_eating: # adding cards to a pickup
                message += 'added '
                message_len = len(message)
                for c in cards:
                    message_len += (c.strLen() + 1)
                return message_len + len('to the pickup')
            else: # adding cards to an attack
                message += 'attacked with '
                message_len = len(message)
                for c in cards:
                    message_len += (c.strLen() + 1)
                return message_len


    def getMoveString(self, a, player) -> str:
        """
        String representing the move just taken. Includes the players involved
        
        :param self: TransferDurak instance
        :param a: action taken
        :param player: player who took the action
        :return: A string representing the move just taken.
        :rtype: str
        """
        message = f'P{player} '
        a_type, cards = a
        if a_type == 'e':
            message += 'ate'
        elif a_type == 'b':
            message += 'blocked additions to the pickup'
        elif a_type == 't':
            message += 'tranferred '
            for c in cards:
                message += (str(c) + ' ')
        elif a_type == 'd':
            message += 'defended with '
            for c in cards:
                message += (str(c) + ' ')
        elif a_type == 'r':
            message += 'rides'
        elif a_type == 'p':
            attacker_positions = self.allowedAttackerPositions()
            attacker_idx = attacker_positions.index(player)
            if self.defender_eating:
                message += f'passed the additions to P{attacker_positions[attacker_idx + 1]}'
            else:
                message += f'passed the attack to P{attacker_positions[attacker_idx + 1]}'
        elif a_type == 'a': # an attack
            if self.defender_eating: # adding cards to a pickup
                message += 'added '
                for c in cards:
                    message += (str(c) + ' ')
                message += 'to the pickup'
            else: # adding cards to an attack
                message += 'attacked with '
                for c in cards:
                    message += (str(c) + ' ')  
        return message


    def getCurrentPlayer(self):
        """
        Returns the current player
        
        :param self: TransferDurak instance
        """
        if self.is_attacker_move:
            return self.getAttacker()
        else:
            return self.getDefender()
    

    def getCurrentPlayerNumber(self) -> int:
        """
        :param self: TransferDurak instance
        :return: The number of the current player (NOT their index in the players list)
        :rtype: int
        """
        if self.is_attacker_move:
            return self.player_numbers[self.attacker_pos]
        else:
            return self.player_numbers[self.defender_pos]


    def actions(self):
        """
        Returns the possible actions in the current state.
        
        :param self: TransferDurak instance.
        """
        player = self.getCurrentPlayer()
        return player.actions()
    
        
    def sampleBelief(self):
        """
        Given a player's belief states, samples a possible actual game state.
        All possible states are equally likely since all cards are unique.
        
        :param self: Player instance
        """
        player = self.getCurrentPlayer()
        # get a copy of the current state
        # we will override the talon and the hands of the other players according to the belief state
        newState = TransferDurak(self) 
        
        # get new talon
        talon = list(player.talon_belief)
        random.shuffle(talon) # randomly shuffle the cards that the player believes may be in the talon
        talon = talon[:len(self.talon)] # get as many of them as are in the actual talon
        newState.talon = talon

        # set of all unaccounted-for cards
        used_cards = set(talon).union(set(self.discard)).union(set(player.hand))
        for belief in player.hand_beliefs:
            used_cards = used_cards.union(belief)
        available_cards = list(set(self.generateTalon()) - used_cards)

        # sample hands for players
        for i,other in enumerate(self.players):
            if other is not player: # only override other players hands
                hand = player.hand_beliefs[i]
                while len(hand) < len(other.hand): # only sample up to size of player's hand
                    hand.add(available_cards.pop(-1)) # add a random card from the available cards
                newState.players[i].hand = list(hand) # override hand
        
        return newState

###################################################################
#                         Player Class                            #
###################################################################

# Player class only used in durak
class Player:
    def __init__(self, game, position):
        self.game = game
        self.position = position # the number of the player (does not change during the game)
        self.hand = []
        self.hand_beliefs = []    
        self.talon_belief = set(self.game.generateTalon())
    

    def showHand(self) -> str:
        """
        Return a string showing the cards in self's hand.
        
        :param self: Player instance
        :return: string of cards
        :rtype: str
        """
        result = ''
        for c in self.hand:
            result += str(c) + ' '
        return result
        

    def privatePickUp(self, cards):
        """
        Add a card or a tuple of cards to the player's hand without updating anyone's belief states
        
        :param self: Player instance
        :param cards: card(s) to add to hand
        """
        if type(cards) is not tuple:
            if type(cards) is list:
                cards = tuple(cards)
            else:
                cards = (cards,)
        for c in cards:
            # does NOT propogate information to other players (since they don't know what card you pulled)
            self.hand.append(c)
            self.talon_belief.discard(c) # update talon belief for this player only
    

    def publicPickUp(self, cards):
        """
        Add a card (or a tuple of cards) to the player's hand and update the belief states of every other player in self.game
        
        :param self: Player instance
        :param cards: card(s) to add to hand
        """
        if type(cards) is not tuple:
            if type(cards) is list:
                cards = tuple(cards)
            else:
                cards = (cards,)

        cur_player_idx = self.game.player_numbers.index(self.position) # the index in the hand beliefs that must be updated

        for c in cards:
            # propogates information to other players about what cards you have (because they watched you pick them up during an attack)
            # if type(c) == type(list):
            self.hand.append(c)
            for other in self.game.players:
                if other is self: # no need to update self belief state (we know what our hand is)
                    continue
                other.hand_beliefs[cur_player_idx].add(c)


    def publicPlay(self, cards):
        """
        Remove a card  or a tuple of cards from the player's hand and update the belief states of every other player in self.game
        
        :param self: Player instance
        :param cards: card(s) to remove from hand
        """
        if type(cards) is not tuple:
            if type(cards) is list:
                cards = tuple(cards)
            else:
                cards = (cards,)
         
        cur_player_idx = self.game.player_numbers.index(self.position) # the index in the hand beliefs that must be updated

        for c in cards:
            # propagates information to other players about what cards you have (because they watched you play it during an attack or defense)
            self.hand.remove(c)
            for other in self.game.players:
                if other is self:
                    continue # no need to update self belief state (we know what our hand is)
                other.hand_beliefs[cur_player_idx].discard(c) # update hand beliefs for other plays
                other.talon_belief.discard(c) # update talon beliefs for other players (self's was updated when it picked up the card)
    

    def possibleFirstAttacks(self):
        """
        Returns a list of the possible opening attacks at the start of a round.
        
        :param self: Player instance
        """
        ranks = {card.rank for card in self.hand}
        attacks = []
        for r in ranks:
            cards_of_rank = [card for card in self.hand if card.rank == r]
            attacks += getAllSubsets(cards_of_rank)
        defender = self.game.getDefender()
        return [('a', tuple(a)) for a in attacks if len(a) > 0 and len(a) <= defender.handSize()] # return nonempty attacks <= the defender's hand size

        
    def possibleDefenses(self):
        """
        Returns a list of the possible permutations of cards that can defend the game's current attack
        
        :param self: Player instance
        """
        possible_defenses = []
        if len(self.game.defense_cards) > 0: # after the we have begun defending, only one card can be added at a time
            attack_card = self.game.attack_cards[-1]
            possible_defenses += [(card,) for card in self.hand if self.game.beatsCard(card, attack_card)]
        else: # defending the first attack
            defense_perms = getAllPermutations(self.hand, len(self.game.attack_cards)) # need all possible ways to defend the attack. Generate all subsets of length equal to the length of the attack
            for perm in defense_perms:
                valid_defense = True
                for i, card in enumerate(perm):
                    if not self.game.beatsCard(card, self.game.attack_cards[i]): # if any of the cards doesn't defend its corresponding attack card, don't consider that action
                        valid_defense = False
                        break
                if valid_defense:
                    possible_defenses.append(tuple(perm))
        return possible_defenses


    def canPassAttack(self):
        """
        Returns True if and only if an attack can be passed to the next player
        
        :param self: Player instance
        """
        eligible = self.game.allowedAttackerPositions() # indices of game.players list that are allowed to attack
        player_list_idx = self.game.player_numbers.index(self.position) # index of self in game.players list
        cur_idx = eligible.index(player_list_idx) # index of player_list_idx in the allowed attacker list
        if cur_idx < len(eligible) - 1:
            return True
        return False


    def attackerActions(self) -> list[tuple]:
        """
        Returns a list of the possible actions for an attacker in the game's current state.
        Returns the empty list if the current player is not an attacker
        
        :param self: Player instance
        :return: list of possible attacker actions
        :rtype: list[tuple]
        """
        possible_actions = []
        if self.game.player_numbers[self.game.attacker_pos] == self.position: # actions if the palyer is an attacker
            if not self.game.defender_eating: 
                if len(self.game.attack_cards) > 0: # if it is after the first card has been played, the attacker may pass or say it rides
                    possible_actions.append(('r',  tuple()))
                    if self.canPassAttack(): # if there is another player who can attack, allow a pass
                        possible_actions.append(('p',  tuple()))
                    # get cards that can be added to attack
                    addable_ranks = {card.rank for card in self.game.attack_cards + self.game.defense_cards}
                    possible_actions += [('a', (card,)) for card in self.hand if card.rank in addable_ranks] 
                else:
                    possible_actions += self.possibleFirstAttacks() # first attack allows multiple of same rank
            else: # code for adding cards after the defende eats
                if self.canPassAttack():
                    possible_actions.append(('p', tuple())) # pass addition to next player
                possible_actions.append(('b', tuple())) # block further additions
                addable_ranks = {card.rank for card in self.game.last_attack + self.game.last_defense}
                possible_actions += [('a', (card,)) for card in self.hand if card.rank in addable_ranks]
        return possible_actions
        

    def defenderActions(self) -> list[tuple]:
        """
        Returns a list of the possible actions for a defender in the game's current state.
        Returns the empty list if the current player is not a defender.
        
        :param self: Player instance
        :return: list of possible defender actions
        :rtype: list[tuple]
        """
        possible_actions = []
        if self.game.player_numbers[self.game.defender_pos] == self.position: # actions if the player is a defender
            possible_actions.append(('e', tuple()))
            if len(self.game.defense_cards) == 0: # may transfer the card before anything is played
                matching_rank_cards = [card for card in self.hand if card.rank == self.game.attack_cards[0].rank] # all cards in the defender's hand matching the attacking cards' rank
                receiving_player = self.game.players[self.game.movePosition(self.game.defender_pos, 1)] # get player who would receive transfer
                # all the ways the defender can pass the cards
                # worst rule in the game NOT allowed (check to make sure it is less than the new defender's hand size)
                possible_actions += [('t', tuple(cards)) for cards in getAllSubsets(matching_rank_cards) if len(cards) > 0 and (len(cards) + len(self.game.attack_cards)) <= receiving_player.handSize()]
            possible_actions += [('d', cards) for cards in self.possibleDefenses()] # actions if we choose to defend
        return possible_actions

    
    def actions(self) -> list[tuple]:
        """
        Returns a list of all possible actions for the current player. Returns the empty list if self is not the current player of self.game.
        
        :param self: Player instance
        :return: a list of possible actions
        :rtype: list[tuple]
        """
        return self.attackerActions() + self.defenderActions()


    def handSize(self):
        """
        Returns the length of self.hand
        
        :param self: Player instance
        """
        return len(self.hand)
    

    def lowestValueAction(self, actions):
        # first action to compare later ones against
        best_action = actions[0]
        best_rank = float('inf')
        best_has_trump = True
        for a_type, cards in actions:

            # blocking, riding, and eating are lowest priority
            if a_type in ['b', 'r', 'e']:
                continue

            # prefer passing to blocking, riding, and eating
            if a_type == 'p' and best_action[0] in ['b', 'r', 'e']:
                best_action = (a_type, cards)
                best_rank = float('inf')
                best_has_trump = True

            # FROM HERE BELOW IN THE FOR LOOP, a_type == 'a'

            # check if the current attack has a trump in it
            cur_has_trump = False
            for card in cards:
                if self.game.isTrump(card):
                    cur_has_trump = True
        
            # first move without a trump suit in it
            if best_has_trump and not cur_has_trump:
                best_action = (a_type, cards)
                best_rank = max([card.rank for card in cards])
                best_has_trump = False

            # move has a trump and a previous one did not
            elif not best_has_trump and cur_has_trump:
                continue

            # all previous moves had a trump, and the current one does too
            elif best_has_trump and cur_has_trump:
                max_trump_rank = max([card.rank for card in cards if self.game.isTrump(card)])
                if max_trump_rank < best_rank:
                    best_rank = max_trump_rank
                    best_action = (a_type, cards)
                    best_has_trump = True
            
            else: # a previous move did not have a trump, and the current one does not
                max_rank = max([card.rank for card in cards])
                if max_rank < best_rank:
                    best_rank = max_rank
                    best_action = (a_type, cards)
                    best_has_trump = False

        return best_action, best_rank, best_has_trump

    def chooseActionHeuristic(self):
        # IDEAS:
        # track the number of different ranks in the attack
        # if it gets too big, eat with some probability
        """
        Chooses an action based on a heuristic resembling the way a person might play Durak.
        The heuristic rules are:
        (1) always attack with the lowest card possible
        (2) always prefer attacking to riding, passing, or blocking 
        (3) always defend (or transfer) with the lowest card possible
        (4) always prefer defending to eating
        
        :param self: Description
        """
        TALON_TOLERANCE = 4
        EPSILON = 0.1

        actions = self.actions()
        a, max_rank, has_trump = self.lowestValueAction(actions)
        # prefer passing to blocking, riding, eating
        # choose to pass if we would add a high rank trump card in early game
        if self.position == self.game.player_numbers[self.game.attacker_pos] and self.canPassAttack():
            if has_trump and len(self.game.talon) > TALON_TOLERANCE and random.random() > EPSILON: # hoard trumps in early game
                return ('p', tuple())
        # choose to block, ride, or eat instead of attacking if we would add a high rank trump card in early game
        else:
            if has_trump and len(self.game.talon) > TALON_TOLERANCE and random.random() > EPSILON:
                if self.position == self.game.attacker_pos:
                    if self.game.defender_eating:
                        return ('b', tuple())
                    else:
                        return ('r', tuple())
                else:       
                    return ('e', tuple())
                
        # return lowest value action if in early game
        # also return lowest value action if we randomly chose to play a high card anyway
        return a
     
###################################################################
#                      Human Player Class                         #
###################################################################

# Used for human interaction with the game (and for running experiments in test.py)
class HumanPlayer(Player):
    def __init__(self, game, position):
        super().__init__(game, position)
    

    def chooseAction(self):
        """
        Prints the GUI and executes code for selecting an action manually.
        
        :param self: HumanPlayer instance
        """
        actions = self.actions()
        key = None
        if self.position == self.game.player_numbers[self.game.attacker_pos]: # if the player is attacking
            while key not in [str(i) for i in range(1, len(actions) + 1)]:
                clearScreen()
                self.game.show(self, hide_other_hands = (not OMNISCIENT_GAME))
                self.showPossibleAttacks(actions) 
                key = input(f'Enter an attack number in [1,{len(actions)}]: ')
            key = int(key)
        elif self.position == self.game.player_numbers[self.game.defender_pos]: # if the player is defending
            while key not in [str(i) for i in range(1, len(actions) + 1)]:
                clearScreen()
                self.game.show(self, hide_other_hands = (not OMNISCIENT_GAME))
                self.showPossibleDefenses(actions)
                key = input(f'Enter a defense number in [1,{len(actions)}]: ')
            key = int(key)
        return actions[key - 1]


    def showPossibleAttacks(self, actions: list[tuple]):
        """
        Prints the possible attacks in a human-readable way.
        
        :param self: HumanPlayer instance
        :param actions: a list of actions generated by player.actions()
        """
        print(f'Possible Attacks:')
        for i,a in enumerate(actions):
            a_type, cards = a
            if a_type == 'b':
                print(f'\t[{i + 1}] block additions')
            elif a_type == 'r':
                print(f'\t[{i + 1}] rides')
            elif a_type =='p':
                print(f'\t[{i + 1}] pass')
            elif a_type == 'a':
                print(f'\t[{i + 1}] ', end = '')
                for card in cards:
                    print(card, end = ' ')
                print('')
            

    def showPossibleDefenses(self, actions: list[tuple]):
        """
        Prints the possible defenses in a human-readable way.
        
        :param self: HumanPlayer instance
        :param actions: a list of actions generated by player.actions()
        """
        print(f'Possible Defenses:')
        for i,a in enumerate(actions):
            action_type = a[0]
            cards = a[1]
            if action_type == 'e':
                print(f'\t[{i + 1}] eat', end = '')
                print('')
            if action_type == 't':
                print(f'\t[{i + 1}] transfer ', end = '')
                for c in cards:
                    print(c, end = ' ')
                print('')
            if action_type == 'd':
                print(f'\t[{i + 1}] defend with ', end = '')
                for c in cards:
                    print(c, end = ' ')
                print('')

###################################################################
#                       Helper Functions                          #
###################################################################

def getAllSubsets(L : list) -> list[list]:
    """
    Returns a list of the subsets (stored as lists) of L. Order does not matter in subsets.
    
    :param L: list to generate all subsets of
    :type L: list
    :return: all subsets of L
    :rtype: list[list[Any]]
    """
    if len(L) == 0:
        return [[]]
    return [[L[0]] + subset for subset in getAllSubsets(L[1:])] + getAllSubsets(L[1:])


def getAllPermutations(L : list, n : int) -> list[list]:
    """
    Returns a list of the permutations of length n of L (stored as lists). Order DOES matter (i.e. [1,2,3] != [2,1,3]).
    
    :param L: list to generate all length n permutations of
    :type L: list
    :param n: length of permutations
    :type n: int
    :return: all subsets of L
    :rtype: list[list[Any]]
    """
    if len(L) == 0 or n == 0:
        return [[]]
    result = []
    for i in range(len(L)):
        result += [[L[i]] + perm for perm in getAllPermutations(L[:i] + L[i+1:], n - 1)]
    return result


def clearScreen():
    """Clears the terminal screen for Windows, macOS, and Linux."""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
