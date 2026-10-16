from poker.table import Table
from poker.enums import TurnState
from poker.player import Player
from poker.scoring import CompareHand
from poker.pot_manager import PotManager
import logging

logger = logging.getLogger(__name__)

class GameParam():
	def __init__(self, small_blind: int, big_blind: int, num_player: int, player_stack):
		self.small_blind: int = small_blind
		self.big_blind: int = big_blind
		self.num_players: int = num_player
		self.player_stack: int = player_stack

	def raise_blinds(self):

		if (self.big_blind * 2 > self.player_stack):
			return

		self.big_blind *= 2
		self.small_blind *= 2

class Game():

	def __init__(self, game_param: GameParam):
		self.param: GameParam = game_param
		self.table = Table(self.param.num_players)
		self.acting_player: int = 0
		self.river_raise_idx: int = 0
		self.to_speak: int = 0
		self.state: TurnState = TurnState.PREFLOP
		self.phases = [
			(TurnState.PREFLOP, self.__pre_flop),
			(TurnState.FLOP, self.__flop),
			(TurnState.TURN, self.__turn),
			(TurnState.RIVER, self.__river),
			(TurnState.SHOWDOWN, self.__showdown)
		]

	def __reset(self):
		self.to_speak = len(self.table.players)
		self.first_to_show = 0
		self.last_river_raise_idx = -1

	def add_player(self, player_name: str):
		player = Player(player_name, self.param.player_stack)
		self.table.add_player(player)

	def start(self):
		if (not self.table.ready):
			missing = self.param.num_players - len(self.table.players)
			print (f"Game cannot start - Table is not full - {missing} player(s) missing")
			return

		while (not self.table.is_winner):
			self.table.prepare_next_turn()
			self.__process_turn()
			self.table.remove_losers()

		logger.info("FINAL WINNER -> %s", self.table.players[0])
		logger.info("END OF GAME")

	def __process_turn(self):
		self.__reset()
		self.table.deal_cards()

		for state, phase in self.phases:
			self.state = state
			logger.info("NEW PHASE -> %s", state.name)
			phase()

			if (self.table.is_round_winner):
				self.__find_next_to_act()
				logger.info("ROUND WINNER -> %s", self.table.players[self.acting_player].name)
				self.table.process_winner(self.acting_player, self.table.pot)
				return

	def __pre_flop(self):
		self.table.process_small_blind(self.param.small_blind)
		self.table.process_big_blind(self.param.big_blind)
		self.__run_betting_round()

	def __flop(self):
		self.table.reveal_flop()
		self.__run_betting_round()

	def __turn(self):
		self.table.reveal_turn()
		self.__run_betting_round()

	def __river(self):
		self.table.reveal_river()
		self.__run_betting_round()

	def __showdown(self):
		players = self.__get_player_in_odd_chip_priority()
		compare_hands = CompareHand(self.table.community_cards, players)
		classification = compare_hands.get_classification()
		curr_to_show = self.__find_first_to_show()

		for i in range (self.__tot_active_players()):
			logger.info("HAND SHOWDOWN -> %s", self.table.players[curr_to_show].name)
			logger.info("PLAYER HOLECARDS -> %s", self.table.players[curr_to_show].hole_cards)
			logger.info("PLAYER HANDRANK -> %s", self.table.players[curr_to_show].hand_score.rank.name)
			next_to_show = self.__find_next_active_player(curr_to_show)
			curr_to_show = next_to_show

		winners = classification[0]

		for winner in winners:
			logger.info("WINNER -> %s", winner)

		pot_manager = PotManager(self.table.pot, classification, players)
		gains_split = pot_manager.get_gains_split()

		for index, player in enumerate(self.table.players):
			self.table.process_winner(index, gains_split[player])

	def __run_betting_round(self):

		if (self.__is_only_one_player_acting() and self.state != TurnState.PREFLOP):
			return

		self.__find_first_to_act()
		self.to_speak = len(self.table.players) - self.table.players_not_acting

		while (self.__are_players_betting()):
			logger.info("PLAYERS TO SPEAK -> %s", self.to_speak)
			self.to_speak -= 1
			curr_player = self.table.players[self.acting_player]
			self.__get_player_action(curr_player)
			self.__find_next_to_act()

	def	__get_player_action(self, player: Player):
		"""Get the player action via stdin - only for test engine locally"""

		logger.info("GET_PLAYER_ACTION \n\nCurrent bet to match: %s\n%r\n", self.table.current_bet_to_match , player)

		print("what do you want to do ?")
		print("1 - call")
		print("2 - raise")
		print("3 - fold\n")


		choice = input("Enter your choice: ")
		while (choice != "1" and choice != "2" and choice != "3"):
			choice = input("Enter your choice: ")
		print("")

		if (choice == "1"):
			self.table.process_call(self.acting_player)

		elif (choice == "2"):
			raise_amount_str = input("Enter your raise amount: ")
			raise_amount = int(raise_amount_str)
			self.to_speak = len(self.table.players) - self.table.players_not_acting - 1
			logger.debug("PLAYERS TO SPEAK UPDATED -> %s", self.to_speak)
			self.table.process_raise(self.acting_player, raise_amount)
			if self.state == TurnState.RIVER: self.river_raise_idx = self.acting_player

		elif (choice == "3"):
			self.table.process_fold(self.acting_player)


	def __find_next_to_act(self):
		self.acting_player = (self.acting_player + 1) % len(self.table.players)

		while (not self.table.players[self.acting_player].is_acting):
			self.acting_player = (self.acting_player + 1) % len(self.table.players)

	def __find_first_to_act(self):

		if (len(self.table.players) == 2):
			self.acting_player = self.table.small_blind_idx if self.state == TurnState.PREFLOP else self.table.big_blind_idx
			return

		if (self.state == TurnState.PREFLOP):
			self.acting_player = (self.table.big_blind_idx + 1) % len(self.table.players)
			return

		first_to_act = (self.table.dealer_idx + 1) % len(self.table.players)
		for i in range(len(self.table.players)):
			if (self.table.players[first_to_act].is_acting):
				break
			first_to_act = (first_to_act + 1) % len(self.table.players)

		self.acting_player = first_to_act

	def __find_first_to_show(self) -> int:

		if (self.last_river_raise_idx != -1):
			return (self.last_river_raise_idx)

		if (len(self.table.players) == 2):
			return (self.table.dealer_idx)

		player_closest_from_button = self.__find_next_active_player(self.table.dealer_idx)

		return (player_closest_from_button)

	def __find_next_active_player(self, curr_player: int) -> int:

		next_player = (curr_player + 1) % len(self.table.players)

		while (True):
			if (self.table.players[next_player].is_folded == False):
				break
			next_player = (next_player + 1) % len(self.table.players)

		return (next_player)

	def __tot_active_players(self) -> int:

		return (len(self.table.players) - self.table.players_folded)

	def __get_player_in_odd_chip_priority(self):
		player_idx = self.table.dealer_idx
		players = []

		for i in range(len(self.table.players)):
			player_idx = (player_idx + 1) % len(self.table.players)
			players.append(self.table.players[player_idx])

		return (players)

	def __are_players_betting(self):

		return (self.to_speak > 0 and not self.table.is_round_winner)

	def __is_only_one_player_acting(self):

		return (self.table.players_not_acting == len(self.table.players) - 1)
