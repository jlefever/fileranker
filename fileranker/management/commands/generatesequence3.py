import random
from collections import defaultdict
from pathlib import Path
from typing import Generic, Iterator, TypeVar

import numpy as np
from django.core.management.base import BaseCommand, CommandParser

from fileranker import models

LLOC_TOL = 2
ENTITIES_TOL = 0

T = TypeVar("T")


class ItemLookup(Generic[T]):
    def __init__(self):
        self._items: dict[int, list[T]] = defaultdict(list)

    def add_item(self, value: int, item: T):
        self._items[value].append(item)

    def within(self, value_range: range) -> Iterator[T]:
        for value in value_range:
            yield from self._items[value]


class File:
    def __init__(self, id: int, lloc: int, entities: int):
        self.id = id
        self.lloc = lloc
        self.entities = entities

    def __repr__(self) -> str:
        return f"File(id={self.id}, lloc={self.lloc}, entities={self.entities})"


class FileLookup:
    def __init__(self):
        self._files: dict[int, File] = dict()
        self._by_lloc: ItemLookup[File] = ItemLookup()
        self._by_entities: ItemLookup[File] = ItemLookup()

    def add_file(self, file: File):
        if file.id in self._files:
            raise ValueError("duplicate file id")
        self._files[file.id] = file
        self._by_lloc.add_item(file.lloc, file)
        self._by_entities.add_item(file.entities, file)

    def rand_file(self) -> File:
        return random.choice(list(self._files.values()))

    def within(self, lloc_range: range, entities_range: range) -> set[File]:
        lloc = self._by_lloc.within(lloc_range)
        entities = self._by_entities.within(entities_range)
        return set(lloc) & set(entities)


class ProjectLookup:
    def __init__(self):
        self._projects: dict[str, FileLookup] = defaultdict(FileLookup)

    def add_file(self, project: str, file: File):
        self._projects[project].add_file(file)

    def rand_project(self) -> str:
        return random.choice(list(self._projects.keys()))

    def rand_file(self, project: str) -> File:
        return self._projects[project].rand_file()

    def rand_file_within_range(
        self, project: str, lloc_range: range, entities_range: range
    ) -> File | None:
        files = self._projects[project].within(lloc_range, entities_range)
        if len(files) == 0:
            return None
        return random.choice(list(files))

    def rand_file_pair(
        self, lloc_tol: int, entities_tol: int
    ) -> tuple[File, File] | None:
        a_project = self.rand_project()
        b_project = self.rand_project()
        a_file = self.rand_file(a_project)
        lloc_range = range(max(0, a_file.lloc - lloc_tol), a_file.lloc + lloc_tol + 1)
        entities_range = range(
            max(0, a_file.entities - entities_tol), a_file.entities + entities_tol + 1
        )
        b_file = self.rand_file_within_range(b_project, lloc_range, entities_range)
        if b_file is None:
            return None
        if a_file.id == b_file.id:
            return None
        return (a_file, b_file)

    def sample_n_pairs(
        self, lloc_tol: int, entities_tol: int, n: int
    ) -> list[tuple[File, File]]:
        ids: set[int] = set()
        pairs: set[tuple[File, File]] = set()
        while len(pairs) < n:
            pair = self.rand_file_pair(lloc_tol, entities_tol)
            if pair is None:
                continue
            if pair[0].id in ids or pair[1].id in ids:
                continue
            ids.add(pair[0].id)
            ids.add(pair[1].id)
            pairs.add(pair)
        return list(pairs)


class Command(BaseCommand):
    help = "Generate a random sequence of file pairs from the given projects"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("sequence_name", type=str)
        parser.add_argument("project_names_txt", type=str)
        parser.add_argument("n", type=int)

    def handle(self, **options):
        sequence_name = options["sequence_name"]
        projects = Path(options["project_names_txt"]).read_text().splitlines()

        files = list(models.File.objects.filter(project__name__in=projects))
        lookup = ProjectLookup()
        for file in files:
            if file.lloc is None:
                raise RuntimeError()
            if file.entities is None:
                raise RuntimeError()
            lookup.add_file(file.project.name, File(file.pk, file.lloc, file.entities))

        pairs = lookup.sample_n_pairs(LLOC_TOL, ENTITIES_TOL, int(options["n"]))
        pairs = [(p[0].id, p[1].id) for p in pairs]

        seq = models.Sequence.objects.create(name=sequence_name)
        seq.save()
        for pos, (i, j) in enumerate(pairs):
            models.SequenceItem.objects.create(
                sequence=seq, position=pos, file_a_id=min(i, j), file_b_id=max(i, j)
            ).save()
        self.stdout.write(f"Generated a sequence with {len(pairs)} pairs")
