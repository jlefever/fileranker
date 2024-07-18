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
    lloc = models.IntegerField(null=True)
    entities = models.IntegerField(null=True)
    commits = models.IntegerField(null=True)

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

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_sequence_name")
        ]


class SequenceItem(models.Model):
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)
    position = models.IntegerField()
    file_a = models.ForeignKey(File, related_name="+", on_delete=models.CASCADE)
    file_b = models.ForeignKey(File, related_name="+", on_delete=models.CASCADE)

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
    STRONG_A = "SA"
    WEAK_A = "WA"
    STRONG_B = "SB"
    WEAK_B = "WB"
    EQUIVALENT = "E"
    UNSURE = "U"
    VALUE_CHOICES = {
        STRONG_A: "Strong A",
        WEAK_A: "Weak A",
        STRONG_B: "Strong B",
        WEAK_B: "Weak B",
        EQUIVALENT: "Equivalent",
        UNSURE: "Unsure",
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(SequenceItem, on_delete=models.CASCADE)
    value = models.CharField(max_length=2, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.value}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "item"], name="unique_response")
        ]
