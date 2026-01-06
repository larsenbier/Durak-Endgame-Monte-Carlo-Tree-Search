# Durak-Endgame-Monte-Carlo-Tree-Search

The Durak Engame Monte Carlo Tree Search (Durak MCTS) repository contains a Monte Carlo Tree Search (MCTS) based AI for playing Durak, implemented in Python.

The code provided can be run through `main.py` to play against the AI yourself. The paramters of the AI can be directly modified in the source code to alter the runtime for performance (as detailed below).

Here, we use the rules for the popular variant of Durak known as "Perevodnoy Durak" (Transfer Durak). More information on the rules can be found [here](https://www.pagat.com/beating/perevodnoy_durak.html)

## Durak as a Search Problem

One subtlety of applying MCTS to Durak is that the AI does not have access to the complete game state (because cards are hidden in other players' hands or in the talon). We can circumvent this difficulty by modeling Durak as a partially observable Markov decision process (POMDP). In a POMDP, the system dynamics are the same as a fully observable Markov decision process, however the agent cannot observe the underlying state. Instead, it maintains a probability distribution of observations given the underlying state.

### POMDP Formulation
* **Observations** \ We let $\Omega$ denote the set of possible observations. This set is player-dependent. Given a player $p$, any $o\in\Omega$ is knowledge of $p$'s hand, along with collections of cards known to be in the other players' hands (which we call *hand beliefs*), and knowledge of which cards could be in the talon (which we call the *talon belief*). $p$ maintains a hand belief for each other player $q$ in the game, which are initialized as empty sets. Every time $p$ observes $q$ picking up a card (in a situation where the suit and rank are visible to all players), it adds that card to its hand belief for $q$. Likewise, every time $p$ observes $q$ playing a card, it removes that card from its hand belief for $q$. This way, $p$'s hand belief for $q$ contains all the cards known to be in $q's$ hand.
* $\Sigma$ := the set of possible states. This is simply the set of all possible hands, talons, and discard piles over some set of cards $C$.
* For $o\in\Omega$ and $s\in\Sigma$, $\mathbf{P}(o|s)$ is the probability distribution of $\Omega$ given $s$.
* $A_{s}$ := the set of available actions in state $s$, or just $A$ when the state is clear.




### Computing $\mathbf{P}(o|s)$




