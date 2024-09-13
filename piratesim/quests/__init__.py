from piratesim.common.assets import get_asset

def load_quest_bank():
    return get_asset("quests/quests.csv").set_index("quest_id")