from poker.deck import Card
from poker.hand_score import HandScore
import logging

logger = logging.getLogger(__name__)

class Player():

	def __init__(self, name: str, stack: int):
		self.name: str = name
		self.stack: int = stack
		self.current_bet: int = 0
		self.hole_cards: list[Card] = []
		self.is_folded = False
		self.is_acting = True
		self.is_all_in = False
		self.hand_score: HandScore | None = None

	def __str__(self):
		return (
			f"player_name: {self.name}\n"
			f"hand_score: \n{self.hand_score}"
		)

	def __repr__(self):
		return (
			f"player_name: {self.name}\n"
			f"player_stack: {self.stack}\n"
			f"player_curr_bet: {self.current_bet}\n"
			f"player_hole_cards --> {self.hole_cards}\n"
			f"player_is_folded: {self.is_folded}\n"
			f"player_is_acting: {self.is_acting}\n"
			f"player_is_all_in: {self.is_all_in}"
		)

	def receive_card(self, card: Card):

		if (len(self.hole_cards) == 2):
			raise ValueError("This player has already two cards")

		self.hole_cards.append(card)

	def call(self, current_bet_to_match) -> int:
		amount = current_bet_to_match - self.current_bet

		if (amount >= self.stack):
			amount = self.stack
			self.is_all_in = True
			self.is_acting = False

		logger.info("CALL AMOUNT -> %s", amount)

		if (self.is_all_in): logger.info("ALL_IN -> %s is all in", self.name)
		self.stack -= amount
		self.current_bet += amount

		return (amount)

	def raise_bet(self, raise_amount: int, last_raise: int, current_bet_to_match: int) -> tuple[int, int]:

		if (not self.is_acting):
			raise ValueError(f"{self.name} is not acting durint that turn - he should wait next turn to play")

		if (raise_amount < last_raise and raise_amount < self.stack):
			raise ValueError(f"{self.name} raise need to be higher than last_raise amount ({last_raise})")

		call_amount = current_bet_to_match - self.current_bet

		if (self.stack - call_amount <= 0):
			self.is_all_in = True
			self.is_acting = False
			raise_amount = 0

		elif (self.stack - raise_amount - call_amount <= 0):
			self.is_all_in = True
			self.is_acting = False
			raise_amount = self.stack - call_amount

		self.stack -= (raise_amount + call_amount)
		logger.info("RAISE AMOUNT -> %s", raise_amount)
		if (self.is_all_in): logger.info("ALL_IN -> %s is all in", self.name)
		self.current_bet += (raise_amount + call_amount)

		return ((raise_amount, call_amount))

	def fold(self):
		self.is_folded = True
		self.is_acting = False

	def reset(self):
		self.current_bet = 0
		self.hole_cards.clear()
		self.is_folded = False
		self.is_all_in = False
		self.is_acting = True
		self.hand_score = None

	def pay_small_blind(self, small_blind: int) -> int:

		if (self.stack == 0):
			raise ValueError(f"Player stack is empty")

		if (small_blind >= self.stack):
			small_blind = self.stack
			self.is_all_in = True
			self.is_acting = False

		logger.info("SMALL BLIND AMOUNT -> %s", small_blind)
		if (self.is_all_in): logger.info("ALL_IN -> %s is all in", self.name)
		self.stack -= small_blind
		self.current_bet += small_blind

		return (small_blind)

	def pay_big_blind(self, big_blind: int) -> int:

		if (self.stack == 0):
			raise ValueError(f"Player stack is empty")

		if (big_blind >= self.stack):
			big_blind = self.stack
			self.is_all_in = True
			self.is_acting = False

		logger.info("BIG BLIND AMOUNT -> %s", big_blind)
		if (self.is_all_in): logger.info("ALL_IN -> %s is all in", self.name)
		self.stack -= big_blind
		self.current_bet += big_blind

		return (big_blind)

	def receive_pot(self, pot: int):
		self.stack += pot
