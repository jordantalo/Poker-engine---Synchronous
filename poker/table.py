from poker.deck import Deck, Card
from poker.player import Player
from random import randint
import logging

logger = logging.getLogger(__name__)

class Table():

	def __init__(self, size: int = 4):
		self.players: list[Player] = []
		self.pot: int = 0
		self.community_cards: list[Card] = []

		if (size < 2 or size > 10):
			raise ValueError("Minimum 2 players - Maximum 10 players")

		self.size: int = size
		self.dealer_idx: int = randint(0, size - 1)
		self.small_blind_idx: int = 0
		self.big_blind_idx: int = 0
		self.current_bet_to_match:int = 0
		self.last_raise: int = 0
		self.ready: bool = False
		self.deck: Deck = Deck()
		self.is_winner: bool = False
		self.players_folded: int = 0
		self.players_not_acting: int = 0
		self.is_round_winner: bool = False

	def prepare_next_turn(self):
		self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
		self.pot = 0
		self.is_round_winner = False
		self.last_raise = 0
		self.players_folded = 0
		self.players_not_acting = 0
		self.current_bet_to_match = 0
		self.community_cards.clear()
		self.deck.reset_deck()
		self.__calc_blind_idx()

		for player in self.players:
			player.reset()

	def __calc_blind_idx(self):

		if not self.players:
			raise ValueError("No players in the table")

		elif (len(self.players) > 2):
			self.small_blind_idx = (self.dealer_idx + 1) % len(self.players)
			self.big_blind_idx = (self.dealer_idx + 2) % len(self.players)

		else:
			self.small_blind_idx = self.dealer_idx
			self.big_blind_idx = (self.dealer_idx + 1) % len(self.players)

	def add_player(self, player: Player):

		if (self.ready == True):
			raise ValueError("Table is already full")

		self.players.append(player)

		if (len(self.players) == self.size):
			self.ready = True

	def get_SB_player(self):
		return self.players[self.small_blind_idx]

	def get_BB_player(self):
		return self.players[self.big_blind_idx]

	def remove_losers(self):
		players_to_remove = []

		for player in self.players:

			if (player.stack == 0):
				players_to_remove.append(player)

		for player in players_to_remove:

			if (self.is_winner == True):
				raise ValueError("Cannot remove another player because there is a winner")

			self.__remove_loser(player)

	def __remove_loser(self, player: Player):
		player_idx = self.players.index(player)
		self.players.remove(player)

		if (len(self.players) == 1):
			self.is_winner = True
			return

		if (player_idx == self.dealer_idx):

			if (self.dealer_idx == 0):
				self.dealer_idx = len(self.players) - 1
			else:
				self.dealer_idx -= 1

	def deal_cards(self):
		to_give_idx = self.dealer_idx

		for i in range(len(self.players) * 2):
			to_give_idx = (to_give_idx + 1) % len(self.players)
			self.players[to_give_idx].receive_card(self.deck.get_card())

	def add_to_pot(self, amount: int):
		self.pot += amount

	def process_small_blind(self, amount: int):
		player = self.get_SB_player()
		logger.info("PLAYER PAY SMALL BLIND -> %s", player.name)
		small_blind = player.pay_small_blind(amount)
		self.add_to_pot(amount=small_blind)

		if (not player.is_acting):
			self.players_not_acting += 1

	def process_big_blind(self, amount: int):
		player = self.get_BB_player()
		logger.info("PLAYER PAY BIG BLIND -> %s", player.name)
		big_blind = player.pay_big_blind(amount)
		self.current_bet_to_match += big_blind
		self.add_to_pot(amount=big_blind)

		if (not player.is_acting):
			self.players_not_acting += 1

	def process_call(self, player_idx: int):
		logger.info("PLAYER CALL -> %s", self.players[player_idx].name)
		call = self.players[player_idx].call(self.current_bet_to_match)
		self.add_to_pot(call)

		if (not self.players[player_idx].is_acting):
			self.players_not_acting += 1

	def process_raise(self, player_idx: int, amount: int):
		player = self.players[player_idx]
		logger.info("PLAYER RAISE -> %s", player.name)
		raise_amount, call_amount = player.raise_bet(amount, self.last_raise, self.current_bet_to_match)
		self.current_bet_to_match += raise_amount
		self.add_to_pot(raise_amount + call_amount)
		self.last_raise = raise_amount

		if (not player.is_acting):
			self.players_not_acting += 1

	def process_fold(self, player_idx: int):
		logger.info("PLAYER FOLD -> %s", self.players[player_idx].name)
		self.players[player_idx].fold()
		self.players_folded += 1
		self.players_not_acting += 1

		if (self.players_folded == len(self.players) - 1):
			self.is_round_winner = True

	def reveal_flop(self):
		self.deck.burn_card()
		self.community_cards.append(self.deck.get_card())
		self.community_cards.append(self.deck.get_card())
		self.community_cards.append(self.deck.get_card())
		logger.info("Flop revealed")
		logger.info("Community cards: %r", self.community_cards)

	def reveal_turn(self):
		self.deck.burn_card()
		self.community_cards.append(self.deck.get_card())
		logger.info("Turn revealed")
		logger.info("Community cards: %r", self.community_cards)

	def reveal_river(self):
		self.deck.burn_card()
		self.community_cards.append(self.deck.get_card())
		logger.info("River revealed")
		logger.info("Community cards: %r", self.community_cards)

	def process_winner(self, player_idx: int, pot: int):
		logger.info("GAIN RECEIVED -> %s received %s tokens", self.players[player_idx].name, pot)
		self.players[player_idx].receive_pot(pot=pot)
