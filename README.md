# Durak-Endgame-Monte-Carlo-Tree-Search

The Durak Engame Monte Carlo Tree Search (Durak MCTS) repository contains a Monte Carlo Tree Search (MCTS) based AI for playing Durak, implemented in Python.

The code provided can be run through `main.py` to play against the AI yourself. The paramters of the AI can be directly modified in the source code to alter the runtime for performance (as detailed below).

Here, we use the rules for the popular variant of Durak known as "Perevodnoy Durak" (Transfer Durak). More information on the rules can be found [here](https://www.pagat.com/beating/perevodnoy_durak.html)

## Durak as a Search Problem

One subtlety of applying MCTS to Durak is that the AI does not have access to the complete game state. We can circumvent this difficulty by modeling Durak as a partially observable Markov decision process (POMDP). In a POMDP, the system dynamics are the same as a fully observable Markov decision process, however the agent cannot observe the underlying state. Instead, it maintains a probability distribution of observations given the underlying state, $\mathbf{P}(o|s)$

