from piratesim.game import Game
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    # ap.add_argument('--pirates', type=int, default=5)
    ap.add_argument('--quests', type=int, default=2)
    ap.add_argument('--gold', type=int, default=500)
    ap.add_argument('--seed', type=int, required=False)

    args = ap.parse_args()
    game = Game(
        n_quests=args.quests,
        starting_gold=args.gold,
        seed=args.seed,
    )
    game.run()
