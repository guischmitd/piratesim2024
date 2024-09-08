from piratesim.common.assets import get_asset

quests = get_asset("quests/quests.csv")


class QuestNode:
    def __init__(self, quest_id, name, marked_as_root):
        self.quest_id = quest_id
        self.name = name
        self.marked_as_root = marked_as_root
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def print_tree(self, level=0):
        print(
            "  " * level
            + f"{self.quest_id}: {self.name}"
            + (" [ROOT]" if self.marked_as_root else "")
        )
        for child in self.children:
            child.print_tree(level + 1)


def build_quest_tree(df):
    # Create a dictionary to hold the QuestNode objects
    quest_dict = {}
    for _, row in df.iterrows():
        quest_id = row["quest_id"]
        quest_dict[quest_id] = QuestNode(
            quest_id, row["name"], bool(row["is_chain_root"])
        )

    # Track child quests to identify root nodes later
    child_quests = set()

    # Build the tree structure by linking parents to children
    for _, row in df.iterrows():
        quest_id = row["quest_id"]
        next_in_chain = row["next_in_chain"]
        next_if_failure = row["next_if_failure"]

        if next_in_chain != -1:
            child_node = quest_dict.get(next_in_chain)
            if child_node:
                quest_dict[quest_id].add_child(child_node)
                child_quests.add(next_in_chain)

        if next_if_failure != -1:
            failure_node = quest_dict.get(next_if_failure)
            if failure_node:
                quest_dict[quest_id].add_child(failure_node)
                child_quests.add(next_if_failure)

    # Root nodes are those not listed as children
    root_nodes = [
        node for quest_id, node in quest_dict.items() if quest_id not in child_quests
    ]

    return root_nodes


def print_quest_trees(roots):
    for root in roots:
        root.print_tree()
        print("\n")  # Add space between different trees


# Assuming the quests DataFrame is already loaded and available
roots = build_quest_tree(quests)
print_quest_trees(roots)
