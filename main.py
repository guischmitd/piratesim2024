from piratesim.game import Game
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--pirates', type=int, default=5)
    ap.add_argument('--quests', type=int, default=3)
    ap.add_argument('--gold', type=int, default=1000)
    ap.add_argument('--seed', type=int, required=False)

    args = ap.parse_args()
    game = Game(
        n_pirates=args.pirates,
        n_quests=args.quests,
        gold=args.gold,
        seed=args.seed
    )
    game.run()
