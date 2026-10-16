from poker.game import Game, GameParam
import logging

def main():

	logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)-18s | %(message)s",
        datefmt="%H:%M:%S"
    )

	game_param = GameParam(100, 200, 3, 500)
	game = Game(game_param=game_param)

	game.add_player("jordan")
	game.add_player("titi")
	game.add_player("Rinda")

	game.start()

if __name__ == "__main__":
	main()
