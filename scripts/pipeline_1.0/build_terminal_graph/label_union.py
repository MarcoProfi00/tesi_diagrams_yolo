"""Utility condivise per fondere gruppi di label senza alterarne la root."""


class LabelUnionFind:
    """Union-find deterministico che mantiene come root la label numerica minore."""

    def __init__(self, labels=()):
        self._parent = {int(label): int(label) for label in labels}

    def find(self, label):
        """Restituisce la root applicando path compression."""
        label = int(label)
        self._parent.setdefault(label, label)
        while self._parent[label] != label:
            self._parent[label] = self._parent[self._parent[label]]
            label = self._parent[label]
        return label

    def union(self, label_a, label_b):
        """Fonde due label valide; ignora gli ancoraggi mancanti."""
        if label_a is None or label_b is None:
            return

        root_a = self.find(label_a)
        root_b = self.find(label_b)
        if root_a != root_b:
            self._parent[max(root_a, root_b)] = min(root_a, root_b)


def merge_label_groups(label_to_terminal_ids: dict, union_find: LabelUnionFind):
    """Materializza gruppi fusi, deduplicati e ordinati per terminal id."""
    merged = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        root = union_find.find(int(label))
        merged.setdefault(root, []).extend(terminal_ids)

    return {
        int(label): sorted(set(terminal_ids))
        for label, terminal_ids in merged.items()
    }
