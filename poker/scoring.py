from poker.enums import HandRank, CardRank, Suit
from poker.player import Player
from poker.deck import Card
from poker.hand_score import HandScore
from collections import Counter

class Hand:

	def __init__(self, player: Player, all_cards: list[Card]):
		self.player: Player = player
		self.all_cards: list[Card] = all_cards
		self.all_cards.sort(key=lambda x: x.rank.value, reverse=True)
		self.all_hands: list[list[Card]] = []
		self.best_hand: HandScore | None = None
		self.of_a_kind_methods = [
			self.__get_four_of_a_kind,
			self.__get_full_house,
			self.__get_three_of_a_kind,
			self.__get_two_pairs,
			self.__get_pairs,
			self.__get_high_card
		]

	def evaluate_best_hand(self):
		self.__calc_all_possible_hands()
		last_scoring = tuple()

		for hand in self.all_hands:
			score = self.__score_hand(hand)
			if (score.scoring > last_scoring):
				last_scoring = score.scoring
				self.best_hand = score

	def __calc_all_possible_hands(self):
		self.__backtrack(0, [])

	def __backtrack(self, start: int, comb: list[Card]):

		if (len(comb) == 5):
			self.all_hands.append(comb.copy())
			return

		for i in range(start, len(self.all_cards)):
			comb.append(self.all_cards[i])
			self.__backtrack(i + 1, comb)
			comb.pop()

	def __score_hand(self, hand: list[Card]) -> HandScore:
		hand_score = self.__evaluate_flush_straight_comb(hand)

		if (hand_score):
			return (hand_score)
		else:
			return (self.__evaluate_of_a_kind(hand))

	def __evaluate_flush_straight_comb(self, hand: list[Card]) -> HandScore | None:
		hand_score_straight = self.__get_straight(hand)
		hand_score_flush = self.__get_flush(hand)

		if (hand_score_flush and hand_score_straight and hand[0].rank == CardRank.AS):
			return (HandScore(HandRank.ROYAL_FLUSH))

		elif (hand_score_flush and hand_score_straight):
			return  (HandScore(HandRank.STRAIGHT_FLUSH, hand_score_straight.height))

		elif (hand_score_flush):
			return (hand_score_flush)

		elif (hand_score_straight):
			return (hand_score_straight)

		return (None)

	def __get_flush(self, hand: list[Card]) -> HandScore | None:
		first_suit: Suit = hand[0].suit

		for card in hand:
			if (card.suit != first_suit):
				return (None)

		hand_rank = HandRank.FLUSH
		height = [hand[0].rank.name]
		kickers = [hand[1].rank.name, hand[2].rank.name, hand[3].rank.name, hand[4].rank.name]
		hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
		return (hand_score)

	def __get_straight(self, hand: list[Card]) -> HandScore | None:
		hand = hand.copy()

		if (hand[0].rank == CardRank.AS and hand[-1].rank == CardRank.TWO):
			hand.append(Card(Suit.DIAMOND, CardRank.AS_SPECIAL))
			del hand[0]

		last_rank = hand[0].rank.value + 1

		for card in hand:
			if (last_rank - card.rank.value != 1):
				return (None)
			last_rank = card.rank.value

		hand_rank = HandRank.STRAIGHT
		height = [hand[0].rank.name]
		kickers = []
		hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
		return (hand_score)


	def __evaluate_of_a_kind(self, hand:list[Card]) -> HandScore | None:
		ranks = [card.rank.name for card in hand]
		counter = Counter(ranks)
		most_common = counter.most_common()

		for of_a_kind in self.of_a_kind_methods:
			res: HandScore = of_a_kind(most_common)

			if (res != None):
				return (res)

		return (None)

	def __get_full_house(self, most_common_rank) -> HandScore | None:

		if (most_common_rank[0][1] == 3 and most_common_rank[1][1] == 2):
			hand_rank = HandRank.FULL_HOUSE
			height = [most_common_rank[0][0], most_common_rank[1][0]]
			kickers = []
			hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
			return (hand_score)

		return (None)

	def __get_four_of_a_kind(self, most_common_rank) -> HandScore | None:

		if (most_common_rank[0][1] == 4):
			hand_rank = HandRank.FOUR_OF_A_KIND
			height = [most_common_rank[0][0]]
			kickers = [most_common_rank[1][0]]
			hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
			return (hand_score)

		return (None)

	def __get_three_of_a_kind(self, most_common_rank) -> HandScore | None:

		if (most_common_rank[0][1] == 3):
			hand_rank = HandRank.THREE_OF_A_KIND
			height = [most_common_rank[0][0]]
			kickers = [most_common_rank[1][0], most_common_rank[2][0]]
			hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
			return (hand_score)

		return (None)

	def __get_two_pairs(self, most_common_rank) -> HandScore | None:

		if (most_common_rank[0][1] == 2 and most_common_rank[1][1] == 2):
			hand_rank = HandRank.TWO_PAIR
			height = [most_common_rank[0][0], most_common_rank[1][0]]
			kickers = [most_common_rank[2][0]]
			hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
			return (hand_score)

		return (None)

	def __get_pairs(self, most_common_rank) -> HandScore | None:

		if (most_common_rank[0][1] == 2):
			hand_rank = HandRank.PAIR
			height = [most_common_rank[0][0]]
			kickers = [most_common_rank[1][0], most_common_rank[2][0], most_common_rank[3][0]]
			hand_score = HandScore(rank=hand_rank, height=height, kickers=kickers)
			return (hand_score)

		return (None)

	def __get_high_card(self, most_common_rank) -> HandScore:
		rank = HandRank.HIGH_CARD
		height = [most_common_rank[0][0]]
		kickers = [most_common_rank[1][0], most_common_rank[2][0], most_common_rank[3][0], most_common_rank[4][0]]
		hand_score = HandScore(rank=rank, height=height, kickers=kickers)

		return (hand_score)

class CompareHand:

	def __init__(self, community_cards: list[Card], players: list[Player]):
		self.community_cards: list[Card] = community_cards
		self.players: list[Player] = players
		self.all_hands: list[Hand] = []
		self.classification: list[list[Player]] = []

	def get_classification(self):
		self.__evaluate_players_hand()
		self.all_hands.sort(key=lambda x: x.best_hand.scoring, reverse=True)
		self.__wrap_results()

		return (self.classification)

	def __evaluate_players_hand(self):

		for player in self.players:

			if (player.is_folded):
				continue

			cards = self.community_cards + player.hole_cards
			player_hand = Hand(player, cards)
			player_hand.evaluate_best_hand()
			player.hand_score = player_hand.best_hand
			self.all_hands.append(player_hand)

	def __wrap_results(self):
		self.classification.append([self.all_hands[0].player])
		rank = 0

		for i in range(1, len(self.all_hands)):
			prev_player_score = self.all_hands[i - 1].best_hand.scoring
			curr_player_score = self.all_hands[i].best_hand.scoring

			if (prev_player_score == curr_player_score):
				self.classification[rank].append(self.all_hands[i].player)

			else:
				rank += 1
				self.classification.append([self.all_hands[i].player])



# player1 = Player("jordan", 1000)
# player1.receive_card(Card(Suit.DIAMOND, CardRank.TEN))
# player1.receive_card(Card(Suit.CLUB, CardRank.TEN))

# player2 = Player("olek", 1000)
# player2.receive_card(Card(Suit.HEART, CardRank.TEN))
# player2.receive_card(Card(Suit.SPADE, CardRank.TEN))

# player3 = Player("clem", 1000)
# player3.receive_card(Card(Suit.CLUB, CardRank.AS))
# player3.receive_card(Card(Suit.CLUB, CardRank.THREE))

# players = [player1, player2, player3]

# community_cards: list[Card] = []
# community_cards.append(Card(Suit.DIAMOND, CardRank.AS))
# community_cards.append(Card(Suit.SPADE, CardRank.THREE))
# community_cards.append(Card(Suit.HEART, CardRank.AS))
# community_cards.append(Card(Suit.DIAMOND, CardRank.TWO))
# community_cards.append(Card(Suit.SPADE, CardRank.TWO))

# compare_hands = CompareHand(community_cards=community_cards, players=players)
# classification = compare_hands.compare()

# for rank, players in enumerate(classification):
# 	print(f"Rank: {rank}")
# 	for player in players:
# 		print(player)
# 		print("")


