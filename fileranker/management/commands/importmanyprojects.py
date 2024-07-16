import pandas as pd
from django.core.management.base import BaseCommand, CommandParser

from tqdm import tqdm

from fileranker import models


class Command(BaseCommand):
    help = "Import a project from a CSV"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("csv_path", type=str)

    def handle(self, **options):
        df = pd.read_csv(options["csv_path"])

        for project_name, project_df in tqdm(list(df.groupby("project"))):
            project_df = project_df.sort_values("filename")
            project = models.Project.objects.create(name=project_name)
            project.save()
            for _, row in project_df.iterrows():
                models.File.objects.create(
                    project=project,
                    filename=row["filename"],
                    content=row["content"],
                    lloc=row["lloc"],
                    entities=row["entities"],
                ).save()

        self.stdout.write(f"Imported {len(df)} files")
