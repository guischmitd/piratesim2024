from piratesim.common.random import RouletteSelector
from piratesim.quest import Quest


def test_no_items():
    roulette = RouletteSelector()
    assert roulette.roll() is None


def test_single_item():
    q = Quest.from_dict(
        {
            "name": "Plunder the Ghost Ship",
            "type": "treasure",
            "difficulty_min": 3,
            "difficulty_max": 5,
            "reward_min": 100,
            "reward_max": 300,
        }
    )

    roulette = RouletteSelector()
    roulette.add_item(q)

    assert roulette.roll() is q


def test_remove_impossible_items():
    q0 = Quest.from_dict(
        {
            "name": "Plunder the Ghost Ship",
            "type": "treasure",
            "difficulty_min": 3,
            "difficulty_max": 5,
            "reward_min": 100,
            "reward_max": 300,
        }
    )

    q1 = Quest.from_dict(
        {
            "name": "Save Cpt Shaliber",
            "type": "rescue",
            "difficulty_min": 1,
            "difficulty_max": 2,
            "reward_min": 10,
            "reward_max": 50,
        }
    )

    q2 = Quest.from_dict(
        {
            "name": "Loot the tavern",
            "type": "theft",
            "difficulty_min": 2,
            "difficulty_max": 4,
            "reward_min": 50,
            "reward_max": 90,
        }
    )

    roulette = RouletteSelector()
    roulette.add_item(q0, 0.0)
    roulette.add_item(q1, 1.0)
    roulette.add_item(q2, 0.5)

    q1_chosen = 0
    q2_chosen = 0

    for _ in range(1000):
        choice = roulette.roll()
        assert len(roulette.roulette) == 2

        assert choice is q1 or choice is q2
        if choice is q1:
            q1_chosen += 1
        elif choice is q2:
            q2_chosen += 1

    assert q2_chosen < q1_chosen
