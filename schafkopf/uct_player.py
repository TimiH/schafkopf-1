from schafkopf.mc_tree import MCTree
from schafkopf.mc_node import MCNode
from schafkopf.helpers import sample_opponent_hands
from schafkopf.players import Player, DummyPlayer, RandomPlayer
from schafkopf.game import Game
from copy import deepcopy
import multiprocessing as mp
import random

class UCTPlayer(Player):

    def __init__(self, name="UCT", ucb_const=1):
        Player.__init__(self, name=name)
        self.ucb_const = 1

    def uct_search(self, game_state, num_simulations=100):
        root_node = MCNode(game_state=game_state)
        mc_tree = MCTree(root_node=root_node)

        sim_num = 1

        while sim_num <= num_simulations:
            selected_node = self.selection(mc_tree)
            rewards = self.simulation(selected_node)
            mc_tree.backup_rewards(leaf_node=selected_node, rewards=rewards)

        best_action = mc_tree.root_node.best_child(ucb_const=0)

        return best_action

    def selection(self, mc_tree):
        current_node = mc_tree.root_node
        while not current_node.is_terminal():
            if not current_node.fully_expanded():
                return self.expand(mc_tree=mc_tree, node=current_node)
            else:
                current_node = current_node.best_child(ucb_const=self.ucb_const)
        return current_node

    def expand(self, mc_tree, node):
        not_visited_actions = set(node.game_state["possible_actions"])
        for child in node.children:
            not_visited_actions.remove(child.previous_action)
        chosen_action = random.choice(not_visited_actions)
        new_state = self.get_new_state(game_state=node.game_state,
                                       action=chosen_action)
        new_node = MCNode(parent=node, game_state=new_state)
        mc_tree.add_node(node=new_node,
                         parent_node=node)
        return new_node

    def get_new_state(self, game_state, action):
        playerlist = [DummyPlayer(favorite_mode=action, favorite_cards=[action]),
                      DummyPlayer(favorite_mode=action, favorite_cards=[action]),
                      DummyPlayer(favorite_mode=action, favorite_cards=[action]),
                      DummyPlayer(favorite_mode=action, favorite_cards=[action])]
        game = Game(game_state=game_state, players=playerlist)
        game.next_action()
        return game.get_game_state()

    def simulation(self, selected_node):
        playerlist = [RandomPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]
        game = Game(players=playerlist, game_state=selected_node.game_state)
        game.play()
        rewards = game.get_payouts()
        return rewards

    def sample_and_search(self, public_info):
        leading_player_index = public_info["leading_player_index"]
        playerindex = public_info["current_player_index"]
        mode_proposals = public_info["mode_proposals"]
        game_mode = public_info["game_mode"]
        trumpcards = public_info["trumpcards"]
        tricks = public_info["tricks"]
        current_trick = public_info["current_trick"]

        # sample opponent hands
        player_hands = sample_opponent_hands(tricks=tricks,
                                             current_trick=current_trick,
                                             trumpcards=trumpcards,
                                             playerindex=playerindex,
                                             player_hand=self._hand)

        # game state
        game_state = public_info
        game_state["player_hands"] = player_hands

        best_action = self.uct_search(game_state=deepcopy(game_state), num_simulations=100)

        return best_action

    def choose_game_mode(self, public_info, options):
        return random.choice(tuple(options))

    def play_card(self, public_info, options=None):
        # choose card by sampling opponent cards N times, in each sample perform MonteCarloSimulation, return best card



        return best_action
