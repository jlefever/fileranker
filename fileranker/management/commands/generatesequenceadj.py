import random
from collections import defaultdict

import numpy as np
from django.core.management.base import BaseCommand, CommandParser

from fileranker import models


def sample_neighbor(locs: list[int], *, ratio: float) -> list[tuple[int, int]]:
    tol = np.std(locs) * ratio
    neighbors = defaultdict(list)
    for i in range(len(locs)):
        for j in range(i + 1, len(locs)):
            if np.abs(locs[i] - locs[j]) < tol:
                neighbors[i].append(j)
                neighbors[j].append(i)
    for neighbor_list in neighbors.values():
        random.shuffle(neighbor_list)
    pairs = []
    while True:
        i = np.random.choice(list(neighbors.keys()))
        j = neighbors[i].pop()
        neighbors[j].remove(i)
        pairs.append((i, j))
        if len(neighbors[i]) == 0:
            del neighbors[i]
        if len(neighbors[j]) == 0:
            del neighbors[j]
        if len(neighbors) == 0:
            break
    return pairs


class Command(BaseCommand):
    help = "Generate a random sequence of file pairs from the given projects"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("sequence_name", type=str)
        parser.add_argument("projects", nargs="+", type=str)
        parser.add_argument("--ratio", type=float)
        parser.add_argument("--seed", type=int)

    def handle(self, **options):
        sequence_name = options["sequence_name"]
        projects = options["projects"]
        ratio = options["ratio"]
        seed = options["seed"]
        files = list(models.File.objects.filter(project__name__in=projects))
        locs = [len(f.content.splitlines()) for f in files]
        pairs = sample_neighbor(locs, ratio=ratio)
        pairs = [(files[i].id, files[j].id) for i, j in pairs]
        seq = models.Sequence.objects.create(name=sequence_name, seed=seed)
        seq.save()
        for pos, (i, j) in enumerate(pairs):
            models.SequenceItem.objects.create(
                sequence=seq, position=pos, file_a_id=min(i, j), file_b_id=max(i, j)
            ).save()
        self.stdout.write(f"Generated a sequence with {len(pairs)} pairs")
