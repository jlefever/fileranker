import itertools as it
import random

from django.core.management.base import BaseCommand, CommandParser

from filerater import models


class Command(BaseCommand):
    help = "Generate a random sequence of file pairs from the given projects"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("sequence_name", type=str)
        parser.add_argument("projects", nargs="+", type=str)
        parser.add_argument("--seed", type=int)

    def handle(self, **options):
        sequence_name = options["sequence_name"]
        projects = options["projects"]
        seed = options["seed"]
        files = models.File.objects.filter(project__name__in=projects).values("id")
        files = sorted([f["id"] for f in files])
        pairs = list(it.combinations_with_replacement(files, 2))
        pairs = [(a, b) for (a, b) in pairs if a != b]
        if seed is None:
            seed = random.randint(0, (2 ** 16) - 1)
        random.seed(seed)
        random.shuffle(pairs)
        seq = models.Sequence.objects.create(name=sequence_name, seed=seed)
        seq.save()
        for i, (a, b) in enumerate(pairs):
            models.SequenceItem.objects.create(
                sequence=seq, position=i, file_a_id=a, file_b_id=b
            ).save()
        self.stdout.write(f"Generated a sequence with {len(pairs)} pairs")
