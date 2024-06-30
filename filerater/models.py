from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q


class Project(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_project_name")
        ]


class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    filename = models.TextField()
    content = models.TextField()

    def __str__(self):
        return f"{self.project}: {self.filename}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "filename"], name="unique_filename_per_project"
            )
        ]


class Sequence(models.Model):
    name = models.TextField()
    seed = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_sequence_name"),
            models.UniqueConstraint(fields=["seed"], name="unique_sequence_seed"),
        ]


class SequenceItem(models.Model):
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)
    position = models.IntegerField()
    file_a = models.ForeignKey(File, related_name="a_items", on_delete=models.CASCADE)
    file_b = models.ForeignKey(File, related_name="b_items", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sequence} ({self.position}): {self.file_a.filename} vs {self.file_b.filename}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sequence", "position"], name="unique_position_per_sequence"
            ),
            models.UniqueConstraint(
                fields=["sequence", "file_a", "file_b"],
                name="unique_files_per_sequence",
            ),
            models.CheckConstraint(
                check=Q(file_a_id__lt=F("file_b_id")), name="item_a_lt_b"
            ),
        ]


class Response(models.Model):
    PREFER_A = "A"
    PREFER_B = "B"
    UNSURE = "U"
    VALUE_CHOICES = {
        PREFER_A: "Prefer A",
        PREFER_B: "Prefer B",
        UNSURE: "Unsure",
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_a = models.ForeignKey(
        File, related_name="a_responses", on_delete=models.CASCADE
    )
    file_b = models.ForeignKey(
        File, related_name="b_responses", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=1, choices=VALUE_CHOICES)

    def __str__(self):
        return f"{self.user} - {self.value}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "file_a", "file_b"],
                name="unique_files_per_response",
            ),
            models.CheckConstraint(
                check=Q(file_a_id__lt=F("file_b_id")), name="response_a_lt_b"
            ),
        ]
