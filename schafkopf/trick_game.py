from copy import deepcopy
from schafkopf.game_modes import NO_GAME, PARTNER_MODE, WENZ, SOLO
from schafkopf.helpers import define_trumpcards
from schafkopf.trick import Trick


class TrickGame:
    def __init__(self, playerlist, leading_player_index, offensive_player_indices, game_mode, mode_proposals):
        self.playerlist = playerlist
        self.max_num_tricks = len(playerlist[0].get_hand())
        self.leading_player_index = leading_player_index
        self.current_player_index = leading_player_index
        self.offensive_player_indices = offensive_player_indices
        self.game_mode = game_mode
        self.mode_proposals = mode_proposals
        self.trumpcards = define_trumpcards(game_mode)
        self.tricks = []
        self.current_trick = Trick(leading_player_index=leading_player_index)
        self.scores = [0 for player in playerlist]

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1)  % 4

    def get_current_player(self):
        return self.playerlist[self.current_player_index]

    def get_public_info(self):
        leading_player = deepcopy(self.leading_player_index)
        current_player = deepcopy(self.current_player_index)
        tricks = deepcopy(self.tricks)
        current_trick = deepcopy(self.current_trick)
        mode_proposals = deepcopy(self.mode_proposals)
        game_mode = deepcopy(self.game_mode)
        trumpcards = deepcopy(self.trumpcards)
        return {"leading_player_index": leading_player,
                "mode_proposals": mode_proposals,
                "game_mode": game_mode,
                "trumpcards": trumpcards,
                "tricks": tricks,
                "current_trick": current_trick,
                "current_player_index": current_player}

    def suit_in_hand(self, suit, hand):
        suit_cards = [card for card in hand if card[1] == suit and card not in self.trumpcards]
        if len(suit_cards) > 0:
            return suit_cards
        else:
            return hand

    def possible_cards(self, current_trick, hand):

        if current_trick.num_cards == 0:
            if self.game_mode[0] == PARTNER_MODE and (7, self.game_mode[1]) in hand:
                forbidden_cards = [card for card in hand if card not in self.trumpcards
                                and card[1] == self.game_mode[1] and card[0] != 7]
                return [card for card in hand if card not in forbidden_cards]
            else:
                return hand

        else:
            first_card = current_trick.cards[current_trick.leading_player_index]

            if first_card in self.trumpcards:
                players_trumpcards = [trump for trump in self.trumpcards if trump in hand]
                if len(players_trumpcards) > 0:
                    return players_trumpcards
                else:
                    return hand
            elif self.game_mode[0] == PARTNER_MODE and first_card[1] == self.game_mode[1] and (7, self.game_mode[1]) in hand:
                return (7, self.game_mode[1])
            else:
                suit = first_card[1]
                return self.suit_in_hand(suit, hand)

    def reset_current_trick(self):
        self.tricks.append(self.current_trick)
        self.current_trick = Trick(self.current_player_index)

    def play_next_card(self):
        current_player = self.get_current_player()
        if self.current_trick.num_cards == 0:
            self.current_trick.leading_player_index = self.current_player_index
        options = self.possible_cards(self.current_trick, current_player.get_hand())
        info = self.get_public_info()
        next_card = current_player.play_card(public_info=info, options=options)
        self.current_trick.cards[self.current_player_index] = next_card
        self.current_trick.num_cards += 1

    def trick_finished(self):
        if self.current_trick.num_cards == 4:
            self.current_trick.calculate_points()
            self.current_trick.determine_trickwinner(self.trumpcards)
            self.current_player_index = self.current_trick.winner
            self.scores[self.current_player_index] += self.current_trick.score
            self.reset_current_trick()
        else:
            self.next_player()

    def finished(self):
        if len(self.tricks) == self.max_num_tricks:
            return True
        else:
            return False

    def play(self):
        while not self.finished():
            self.play_next_card()
            self.trick_finished()