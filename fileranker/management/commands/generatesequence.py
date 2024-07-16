import itertools as it
import random

from django.core.management.base import BaseCommand, CommandParser

from fileranker import models


class Command(BaseCommand):
    help = "Generate a random sequence of file pairs from the given projects"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("sequence_name", type=str)
        parser.add_argument("projects", nargs="+", type=str)

    def handle(self, **options):
        sequence_name = options["sequence_name"]
        projects = options["projects"]
        files = models.File.objects.filter(project__name__in=projects).values("id")
        files = sorted([f["id"] for f in files])
        pairs = list(it.combinations_with_replacement(files, 2))
        pairs = [(a, b) for (a, b) in pairs if a != b]
        random.shuffle(pairs)
        seq = models.Sequence.objects.create(name=sequence_name)
        seq.save()
        for i, (a, b) in enumerate(pairs):
            models.SequenceItem.objects.create(
                sequence=seq, position=i, file_a_id=a, file_b_id=b
            ).save()
        self.stdout.write(f"Generated a sequence with {len(pairs)} pairs")
