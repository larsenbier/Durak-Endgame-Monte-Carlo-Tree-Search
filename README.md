# Durak-Endgame-Monte-Carlo-Tree-Search

The Durak Engame Monte Carlo Tree Search (Durak MCTS) repository contains a Monte Carlo Tree Search (MCTS) based AI for playing Durak, implemented in Python.

The code provided can be run through `main.py` to play against the AI yourself. The parameters of the AI can be directly modified in the source code to alter the runtime for performance (as detailed below).
![Example of playing through `main.py`](playing.png)


Here, we use the rules for the popular variant of Durak known as "Perevodnoy Durak" (Transfer Durak). More information on the rules can be found [here](https://www.pagat.com/beating/perevodnoy_durak.html)

## Durak as a Search Problem

One subtlety of applying MCTS to Durak is that the AI does not have access to the complete game state (because cards are hidden in other players' hands or in the talon). We can circumvent this difficulty by modeling Durak as a partially observable Markov decision process (POMDP). In a POMDP, the system dynamics are the same as a fully observable Markov decision process, however the agent cannot observe the underlying state. Instead, it maintains a probability distribution of observations given the underlying state, which we call the sensor model.

To formulate our POMDP, we must define our observations, game states, and the conditional distribution of observations given states.

Let $\Omega$ denote the set of possible observations. This set is player-dependent. Given a player $p$, any $o\in\Omega$ is the tuple $(H,B,T)$, where $k$ is knowledge of $p$'s hand, $B$ is a collection of sets of cards known to be in the other players' hands (which we call *hand beliefs*), and $T$ is the set of Cards of which could be in the talon (which we call the *talon belief*). $p$ maintains a hand belief for each other player $q$ in the game, which are initialized as empty sets. Every time $p$ observes $q$ picking up a card (in a situation where the suit and rank are visible to all players), it adds that card to its hand belief for $q$. Likewise, every time $p$ observes $q$ playing a card, it removes that card from its hand belief for $q$. This way, $p$'s hand belief for $q$ contains all the cards known to be in $q's$ hand. $p$ also maintains a talon belief, which is initialized as $C$, the set of cards in the game, then updated every time $p$ observes a card being played or added to someone's hand. Importantly, all of this is information available to a human player unable to observe the true game state.

The game state is much simpler to define. We let $\Sigma$ denote the set of possible states. This is simply the set of all possible hands, talons, and discard piles over some set of cards $C$. 

The sensor model $\mathbf{P}(o|s)$ is 1 at the unique observation corresponding to s, and zero everywhere else. The prior distribution, as it turns out, is also quite simple. The main contribution of this implementation is sampling a state from the prior distribution $\mathbf{P}(s|o)$, then running MCTS on this state, avoiding performing MCTS on the belief states themselves. To sample a state, we can use the following algorithm, whose implementation should not modify the observation:
```text
Given some observation o = (H,B,T):
1. Copy p's hand, H.
2. Shuffle the talon belief, T, randomly in place (since we do not know the true order of the possible cards in the talon).
3. For each other player q, we copy p's hand beliefs from B, then sample from T to fill their hands.
4. Finally, since there are only n cards in the talon but m >= n cards in T, we take the first n cards from T.
```
Because of the fact that all talon orderings are equally likely when the game is dealt, $\mathbf{P}(s|o)$ is uniform over its support. Thus, this procedure correctly samples from $\mathbf{P}(s|o)$. 


## The AI

The AI can be broken into two decision-making phases: the earlygame and the endgame. The endgame is a simple threshold on the number of cards in the talon (chosen to be 4 in our implementation). Once the talon length drops below this threshold, we activate MCTS to play out the remainder of the game.

In the earlygame, the AI uses a simple hand-coded heuristic to play, whose logic is in `player.chooseActionHeuristic` in the `durak.py` module. We empirically found that using this strategy in the earlygame produced more wins. In the earlygame, observations correspond to many possible belief states and $\mathbf{P}(s|o)$ has high variance, which makes our sampling less representative of the true problem. Furthermore, this heuristic is much cheaper to compute than the MCTS action, which enables faster testing and faster playout during the early game when MCTS is not as effective.

In the endgame, our sampling algorithm is able to take full advantage of the information gathered throughout the earlygame and stored in the hand beliefs and talon belief. The added information reduces the variance of our samples, which makes MCTS viable for playing out the end game. The horizon on the decisions is generally much smaller compared to the earlygame, which is advantageous for MCTS.

As for the search itself: after sampling, we use a standard MCTS algorithm with the upper confidence bound applied to trees to select nodes for expansion. The playouts are performed using the heuristic from the earlygame, which empirically boosted performance against a random agent compared to using random playouts.

## Results
{content:
|          	|                                   Win Rate of First Agent                 	                          	|
|----------	|-------------------------	|---------------------	|-----------------------	|-------------------------	|
| Playouts 	| Random v Heuristic      	| Pure MCTS  v Random 	| Pure MCTS v Heuristic 	| Hybrid MCTS v Heuristic 	|
| 10       	| 0.15                    	| 0.87                	| 0.85                  	| 0.6                     	|
| 100      	| -                       	| 0.99                	| 0.67                  	| 0.89                    	|
| 200      	| -                       	| 1.0                 	| 0.71                  	| 0.88                    	|
| 500      	| -                       	| 1.0                 	| 0.65                  	| 0.89                    	|
| 700      	| -                       	| 0.99                	| 0.7                   	| 0.9                     	|
| 1000     	| -                       	| 1.0                 	| 0.73                  	| 0.86                    	|
}







