from poker.enums import HandRank, CardRank

class HandScore:

	def __init__(self, rank: HandRank, height: list[str] = [], kickers: list[str] = []):
		self.rank = rank
		self.height = height
		self.kickers = kickers
		self.scoring = self.__get_scoring()

	def __str__(self):

		return (
			f"Main : {self.rank.name}\n"
			f"Hauteur : {self.height}\n"
			f"Kickers : {self.kickers}\n"
			f"Score: {self.scoring}"
		)

	def __repr__(self):

		return self.__str__()

	def __get_scoring(self):
		height_rank = [CardRank[height].value for height in self.height]
		kickers = [CardRank[kicker].value for kicker in self.kickers]

		return tuple([self.rank.value] + height_rank + kickers)
