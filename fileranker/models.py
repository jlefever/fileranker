from django.contrib.auth.models import User
from django.db import models


class Sequence(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.SlugField(unique=True)
    display_name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    goal = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    project_a = models.TextField()
    project_b = models.TextField()
    filename_a = models.TextField()
    filename_b = models.TextField()
    content_a = models.TextField()
    content_b = models.TextField()

    def __str__(self):
        return (
            f"{self.sequence} ({self.position}): {self.filename_a} vs {self.filename_b}"
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sequence", "position"], name="unique_position_per_sequence"
            )
        ]
        ordering = ["sequence", "position"]


class Response(models.Model):
    A = "A"
    STRONG_A = "SA"
    WEAK_A = "WA"
    B = "B"
    STRONG_B = "SB"
    WEAK_B = "WB"
    EQUIVALENT = "E"
    UNSURE = "U"
    VALUE_CHOICES = [
        (A, "A"),
        (STRONG_A, "Strong A"),
        (WEAK_A, "Weak A"),
        (B, "B"),
        (STRONG_B, "Strong B"),
        (WEAK_B, "Weak B"),
        (EQUIVALENT, "Equivalent"),
        (UNSURE, "Unsure"),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    responded_on = models.DateTimeField()
    value = models.CharField(max_length=2, choices=VALUE_CHOICES)

    def __str__(self):
        return f"{self.user} - {self.value}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "question"], name="unique_response")
        ]
        ordering = ["-responded_on"]
