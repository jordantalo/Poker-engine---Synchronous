from enum import Enum

class Suit(Enum):
	CLUB = 1
	HEART = 2
	DIAMOND = 3
	SPADE = 4

class CardRank(Enum):
	AS_SPECIAL = 0
	TWO = 1
	THREE = 2
	FOUR = 3
	FIVE = 4
	SIX = 5
	SEVEN = 6
	EIGHT = 7
	NINE = 8
	TEN = 9
	JACK = 10
	QUEEN = 11
	KING = 12
	AS = 13

class TurnState(Enum):
	PREFLOP = 1
	FLOP = 2
	TURN = 3
	RIVER = 4
	SHOWDOWN = 5

class HandRank(Enum):
	HIGH_CARD = 1
	PAIR = 2
	TWO_PAIR = 3
	THREE_OF_A_KIND = 4
	STRAIGHT = 5
	FLUSH = 6
	FULL_HOUSE = 7
	FOUR_OF_A_KIND = 8
	STRAIGHT_FLUSH = 9
	ROYAL_FLUSH = 10
