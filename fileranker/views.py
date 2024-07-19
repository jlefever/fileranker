from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery
from django.shortcuts import redirect, render
from django.utils.timezone import localtime
from django.views.decorators.http import require_http_methods

from .models import Question, Response, Sequence


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
@require_http_methods(["POST"])
def answer(request):
    print(dict(request.POST))
    question_id = int(request.POST.get("question_id"))
    sequence_name = request.POST.get("sequence_name")
    value = request.POST.get("preference")
    Response.objects.create(
        user=request.user,
        question_id=question_id,
        responded_on=localtime(),
        value=value,
    ).save()
    return redirect("sequence", sequence_name)


def get_current_question(user, sequence_name):
    answered_items = Response.objects.filter(user=user, question=OuterRef("pk"))
    return (
        Question.objects.annotate(
            has_response=Subquery(answered_items.values("id")[:1])
        )
        .filter(has_response__isnull=True, sequence__name=sequence_name)
        .first()
    )
