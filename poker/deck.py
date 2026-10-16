from poker.enums import Suit, CardRank
from random import shuffle

class Card():

	def __init__(self, suit: Suit, rank: CardRank):
		self.suit = suit
		self.rank = rank

	def __str__(self):

		return (
			f"[{self.suit.name}, {self.rank.name}]"
		)

	def __repr__(self):

		return self.__str__()

class Deck():

	def __init__(self):
		self.cards: list[Card] = []
		self.position: int = 0

		for suit in Suit:

			for rank in CardRank:

				if (rank.name != CardRank.AS_SPECIAL.name):
					card = Card(suit=suit, rank=rank)
					self.cards.append(card)

	def reset_deck(self):
		self.position = 0
		self.__shuffle()

	def __shuffle(self):
		shuffle(self.cards)

	def get_card(self) -> Card:

		if (self.position == len(self.cards)):
			raise ValueError("Deck is empty")

		card = self.cards[self.position]
		self.position += 1
		return (card)

	def burn_card(self):
		if (self.position == len(self.cards)):
			raise ValueError("Deck is empty")

		self.position += 1
