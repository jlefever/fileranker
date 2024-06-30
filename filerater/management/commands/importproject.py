import pandas as pd
from django.core.management.base import BaseCommand, CommandParser

from filerater import models


class Command(BaseCommand):
    help = "Import a project from a CSV"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("project_name", type=str)
        parser.add_argument("csv_path", type=str)

    def handle(self, **options):
        project_name = options["project_name"]
        df = pd.read_csv(options["csv_path"])
        df = df.sort_values("filename")

        project = models.Project.objects.create(name=project_name)
        project.save()
        for _, row in df.iterrows():
            models.File.objects.create(
                project=project, filename=row["filename"], content=row["content"]
            ).save()

        self.stdout.write(f"Imported {len(df)} files")
