# Durak-Endgame-Monte-Carlo-Tree-Search

The Durak Engame Monte Carlo Tree Search (Durak MCTS) repository contains a Monte Carlo Tree Search (MCTS) based AI for playing Durak, implemented in Python.

The code provided can be run through `main.py` to play against the AI yourself. The parameters of the AI can be directly modified in the source code, as detailed in "Configuration". An executable file (`durakMCTS.exe`) built from `main.py` through PyInstaller is also provided for those who do not wish to run their own python environment.

![Example of playing through `main.py`](playing.png)

Here, we use the rules for the popular variant of Durak known as "Perevodnoy Durak" (Transfer Durak). More information on the rules can be found [here](https://www.pagat.com/beating/perevodnoy_durak.html). It  can be played with two or more players, with the implementation supporting as many human players as desired.

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

The AI can be broken into two decision-making phases: the earlygame and the endgame. The difference bwteen earlygame and endgame is a simple threshold on the number of cards in the talon (chosen to be 4 in our implementation). Once the talon length drops below this threshold, we enter the endgame and activate MCTS to play out the remainder of the game.

In the earlygame, the AI uses a simple hand-coded heuristic to play, whose logic is in `player.chooseActionHeuristic` in the `durak.py` module. We empirically found that using this strategy in the earlygame produced more wins. In the earlygame, observations correspond to many possible belief states and $\mathbf{P}(s|o)$ has high variance, which makes our sampling less representative of the true problem. Furthermore, this heuristic is much cheaper to compute than the MCTS action, which enables faster testing and faster playout during the early game when MCTS is not as effective.

In the endgame, our sampling algorithm is able to take full advantage of the information gathered throughout the earlygame and stored in the hand beliefs and talon belief. The added information reduces the variance of our samples, which makes MCTS viable for playing out the end game. The horizon on the decisions is generally much smaller compared to the earlygame, which is advantageous for MCTS.

As for the search itself: after sampling, we use a standard MCTS algorithm with the upper confidence bound applied to trees to select nodes for expansion. The playouts are performed using the heuristic from the earlygame, which empirically boosted performance against a random agent compared to using random playouts.

## Results

To evaluate the performance of the Durak MCTS agent, we simulated it playing against a handful of other agents. We refer to the other agents as the "random" agent and the "heuristic" agent. The random agent chooses an available action at random with a uniform distribution over the possible actions. The heuristic player selects an action according to `player.lowestValueAction`. MCTS uses `player.chooseActionHeurisic` to select actions during the playouts, which operates very similarly to `player.lowestValueAction` but has some additional logic that promotes behavior to hoard trump cards early game.

The "MCTS" agent refers to an agent using MCTS to make every decision during the game. The final agent described above which only uses MCTS in the endgame is referred to as the "Hybrid" agent. The results of simulating games with a different number of MCTS playouts are tabulated below. The win rate represents the fraction of the time that the first player beat the second player. Each win rate was calculated over 100 games.

<table><thead>
  <tr>
    <th>Playouts</th>
    <th>Random v<br>Heuristic</th>
    <th>Pure MCTS <br>v Random</th>
    <th>Pure MCTS<br>v Heuristic</th>
    <th>Hybrid MCTS<br>v Heuristic</th>
  </tr></thead>
<tbody>
  <tr>
    <td>10</td>
    <td>0.15</td>
    <td>0.87</td>
    <td>0.85</td>
    <td>0.6</td>
  </tr>
  <tr>
    <td>100</td>
    <td>-</td>
    <td>0.99</td>
    <td>0.67</td>
    <td>0.89</td>
  </tr>
  <tr>
    <td>200<br></td>
    <td>-</td>
    <td>1.0</td>
    <td>0.71</td>
    <td>0.88</td>
  </tr>
  <tr>
    <td>500</td>
    <td>-</td>
    <td>1.0</td>
    <td>0.65</td>
    <td>0.89</td>
  </tr>
  <tr>
    <td>700</td>
    <td>-</td>
    <td>0.99</td>
    <td>0.7</td>
    <td>0.9</td>
  </tr>
  <tr>
    <td>1000</td>
    <td>-</td>
    <td>1.0</td>
    <td>0.73</td>
    <td>0.86</td>
  </tr>
</tbody>
</table>

A graph of the results indicates that within the range of 1000 playouts, 200-500 is sufficient to achieve most of the performance possible within the 1000 playout limit. It is important to remember that these data were gathered over only 100 games at each playout value, so there will be some variance due to the randomness of the game and search (for example, at 10 playouts the Pure MCTS seems to be much better than at higher playouts, although MCTS should improve overall with additional playouts).

![Graph of the results of `test.py`](result.png) 

From the graph, it is clear that the Pure MCTS is an improvement over the heuristic. Pure MCTS trounces the random agent (the heuristic only beats the random agent 15% of the time, versus the pure MCTS beating it almost every time) and defeats the heuristic agent a large percentage of the time (around 70% of the time on average), which is already a good improvement. The best performing agent is the hybrid agent, which defeats the heuristic agent 85-90% of the time within this range of playouts. The hybrid also beat me, an experienced human player, in a large fraction of the games I played. The hybrid was not tested against the random agent, since the Pure MCTS agent already played nearly perfectly against a random agent. The data suggest that the best strategy is one that uses a heuristic for early play and MCTS for the endgame. A more efficient implementation that allows for faster playouts might change this conclusion, as might an observation model that tracks more information to improve the sampling from $\mathbf{P}(s|o)$.

## Configuration

Simple parameters can be changed in the "Global Variables" section of `main.py` and `durak.py`. 

In `durak.py`, the most relevant global variables are `SUITS`, `RANKS`, and `HAND_SIZE`, which control the number of suits in the game, the number of ranks in the game, and the minimum number of cards in each player's hand. Beyond that, `OMNISCIENT_GAME` controls whether the human player gets to see the other players' cards in their hand (False by default).

In `main.py`, the only modifiable values are the number of playouts performed during MCTS and the number of humans in the game. The game only supports 2 players at the moment, but by changing the value of `NUMBER_OF_HUMANS`, you can make games with 0, 1, or 2 humans players. A human must control every human in the game, so if there is more than 1 human in a game of durak, they must input action choices for each human in the game.

Further modifications, like changing the method of simulating playouts or altering heuristics, must be made by modifying existing functions.
