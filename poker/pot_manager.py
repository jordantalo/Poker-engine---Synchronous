from poker.player import Player

class Pot:

	def __init__(self, amount: int, eligible_players: list[Player]):
		self.amount: int = amount
		self.eligible_players: list[Player] = eligible_players
		self.odd_chip: int = 0

	def __str__(self):
		players = [player.name for player in self.eligible_players]

		return (
			f"Pot_amount: {self.amount} -> {players}"
		)

	def __repr__(self):

		return (
			self.__str__()
		)

class PotManager:

	def __init__(self, pot: int, results: list[list[Player]], players: list[Player]):
		self.pot: int = pot
		self.res: list[list[Player]] = results
		self.players: list[Player] = players
		self.players.sort(key=lambda x: x.current_bet)
		self.side_pots: list[Pot] = []
		self.uncalled_bet: tuple[Player, int] | None = None
		self.gains: dict[Player, int] = dict()
		self.__init_dict()

	def __repr__(self):
		players_name = [player.name for player in self.players]
		players_bet = [player.current_bet for player in self.players]
		gains = [(player.name, gain) for player, gain in self.gains.items()]
		side_pot_str: str = ""

		for side_pot in self.side_pots:
			side_pot_str += str(side_pot)
			side_pot_str += "\n"

		uncalled = "uncalled_bet: None\n"

		if (self.uncalled_bet):
			uncalled = f"uncalled_bet: {self.uncalled_bet[0].name} = {self.uncalled_bet[1]}\n"

		return (
			f"Pot: {self.pot}\n"
			f"Players: {players_name}\n"
			f"Curr_bet: {players_bet}\n"
			f"side_pots: \n{side_pot_str}\n"
			f"{uncalled}"
			f"gain_split: {gains}"
		)

	def __init_dict(self):

		for player in self.players:
			self.gains[player] = 0

	def get_gains_split(self) -> dict[Player, int]:
		self.__evaluate_uncalled_bet()
		self.__build_side_pot()
		self.__split_gains()
		self.__give_back_uncalled_bet()

		return (self.gains)

	def __evaluate_uncalled_bet(self):
		uncalled_amount = self.players[-1].current_bet - self.players[-2].current_bet

		if (uncalled_amount > 0):
			self.uncalled_bet = (self.players[-1], uncalled_amount)
			self.players[-1].current_bet -= uncalled_amount
			self.pot -= uncalled_amount

	def __give_back_uncalled_bet(self):

		if (self.uncalled_bet):
			self.gains[self.uncalled_bet[0]] += self.uncalled_bet[1]

	def __build_side_pot(self):
		i = 0
		prev_bet = 0
		side_pot = 1

		for i in range(len(self.players)):

			side_pot = (self.players[i].current_bet - prev_bet) * (len(self.players) - i)
			prev_bet = self.players[i].current_bet
			self.pot -= side_pot

			if (side_pot > 0):
				eligible_players = self.__get_eligible_players(i)
				pot = Pot(amount=side_pot, eligible_players=eligible_players)
				self.side_pots.append(pot)

			i += 1

	def __get_eligible_players(self, first_eligible_index: int):
		eligibles = []

		for i in range (first_eligible_index, len(self.players)):

			if (not self.players[i].is_folded):
				eligibles.append(self.players[i])

		return (eligibles)


	def __split_gains(self):

		for pot in self.side_pots:

			for winners in self.res:
				eligible_winners = 0

				for winner in winners:

					if (winner in pot.eligible_players):
						eligible_winners += 1

				if (eligible_winners > 0):
					self.__split_pot(winners, eligible_winners, pot)
					break


	def __split_pot(self, winners: list[Player], eligibles: int, pot: Pot):

		if (pot.amount % eligibles != 0):
			pot.odd_chip = pot.amount % eligibles

		for winner in winners:

			if (winner in pot.eligible_players):
				self.gains[winner] += pot.amount // eligibles

				if (pot.odd_chip > 0):
					self.gains[winner] += 1
					pot.odd_chip -= 1


# player1 = Player("jordan", 100)
# player2 = Player("titi", 1000)
# player3 = Player("Rinda", 1000)
# player4 = Player("tata", 1000)

# player1.current_bet = 20
# player2.current_bet = 50
# player3.is_folded = True
# player3.current_bet = 100
# player4.current_bet = 120

# players = [player1, player2, player3, player4]

# bets = [player.current_bet for player in players]

# pot_manager = PotManager(sum(bets), [[player1], [player4, player2]], players=players)
# pot_manager.get_gains_split()
# print (pot_manager)

