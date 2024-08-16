import csv

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied

from .models import Question, Sequence
from .models import Response as ResponseModel


@login_required
def index(request):
    seqs = Sequence.objects.all().order_by("id")
    return render(request, "fileranker/index.html", {"seqs": seqs})


@login_required
@require_http_methods(["GET"])
def sequence(request, name):
    question = get_current_question(request.user, name)
    if question is not None:
        goal = question.sequence.goal
        total = Question.objects.filter(sequence=question.sequence).count()
        if goal is None:
            goal = total
        percent = (question.position / goal) * 100
        info = {
            "position": question.position + 1,
            "goal": goal,
            "total": total,
            "percent": percent,
        }
        ctx = {"question": question, "sequence_name": name, "info": info}
        return render(request, "fileranker/sequence.html", ctx)
    else:
        ctx = {"question": question, "sequence_name": name}
        return render(request, "fileranker/sequence.html", ctx)


@login_required
@require_http_methods(["GET"])
def review(request, name, position):
    question = get_question(request.user, name, position)
    if question is not None:
        goal = question.sequence.goal
        total = Question.objects.filter(sequence=question.sequence).count()
        if goal is None:
            goal = total
        percent = (question.position / goal) * 100
        info = {
            "position": question.position + 1,
            "goal": goal,
            "total": total,
            "percent": percent,
        }
        ctx = {"question": question, "sequence_name": name, "info": info}
        return render(request, "fileranker/sequence.html", ctx)
    else:
        ctx = {"question": question, "sequence_name": name}
        return render(request, "fileranker/sequence.html", ctx)


@login_required
@require_http_methods(["POST"])
def answer(request):
    print(dict(request.POST))
    question_id = int(request.POST.get("question_id"))
    sequence_name = request.POST.get("sequence_name")
    value = request.POST.get("preference")
    ResponseModel.objects.create(
        user=request.user,
        question_id=question_id,
        responded_on=localtime(),
        value=value,
    ).save()
    return redirect("sequence", sequence_name)


def get_current_question(user, sequence_name):
    answered_items = ResponseModel.objects.filter(user=user, question=OuterRef("pk"))
    return (
        Question.objects.annotate(
            has_response=Subquery(answered_items.values("id")[:1])
        )
        .filter(has_response__isnull=True, sequence__name=sequence_name)
        .first()
    )


def get_question(user, sequence_name, position):
    try:
        # Retrieve the sequence object by its name
        sequence = Sequence.objects.get(name=sequence_name)
        
        # Retrieve the question object by sequence and position
        question = Question.objects.get(sequence=sequence, position=position)
        
        # Check if the user is an admin
        if user.is_superuser:
            return question
        
        # Check if the user has responded to the question
        response_exists = ResponseModel.objects.filter(user=user, question=question).exists()
        
        if response_exists:
            return question
        else:
            raise PermissionDenied("You must respond to this question before viewing it.")
    
    except (Sequence.DoesNotExist, Question.DoesNotExist):
        # Handle the case where the sequence or question does not exist
        return None

@user_passes_test(lambda u: u.is_superuser)
def download_responses_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="responses.csv"'

    writer = csv.writer(response)
    # Write the header row
    writer.writerow(["sequence", "position", "username", "responded_on", "value"])

    # Fetch and sort responses, excluding those from superusers
    responses = (
        ResponseModel.objects.filter(user__is_superuser=False)
        .select_related("question", "user", "question__sequence")
        .order_by("question__sequence__name", "question__position", "user__username")
    )

    # Write data rows
    for response_record in responses:
        sequence_name = response_record.question.sequence.name
        position = response_record.question.position
        username = response_record.user.username
        responded_on = response_record.responded_on
        value = response_record.value

        writer.writerow([sequence_name, position, username, responded_on, value])

    return response


@user_passes_test(lambda u: u.is_superuser)
def download_sequences_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sequences.csv"'

    writer = csv.writer(response)
    headers = [
        "sequence",
        "position",
        "project_a",
        "project_b",
        "filename_a",
        "filename_b",
        "content_a",
        "content_b",
    ]
    writer.writerow(headers)

    # Fetch all Question instances, ordered by sequence and position
    questions = Question.objects.select_related("sequence").order_by(
        "sequence__name", "position"
    )

    # Write each question's data to the CSV file
    for question in questions:
        row = [
            question.sequence.name,
            question.position,
            question.project_a,
            question.project_b,
            question.filename_a,
            question.filename_b,
            question.content_a,
            question.content_b,
        ]
        writer.writerow(row)

    return response
