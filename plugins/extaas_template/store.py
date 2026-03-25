from collections import defaultdict

class ExtaasStore:
    def __init__(self):
        self.nodes = defaultdict(dict)

    def update_node(self, node, data):
        old_keys = set(self.nodes[node].keys())
        new_keys = set(data.keys())

        # eemaldame kadunud keyd
        for key in old_keys - new_keys:
            self.nodes[node].pop(key, None)

        self.nodes[node].update(data)

    def get_node(self, node):
        return self.nodes.get(node, {})