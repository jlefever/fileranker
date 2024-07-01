from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Response, Sequence, SequenceItem


@login_required
def index(request):
    seqs = Sequence.objects.all().order_by("id")
    return render(request, "fileranker/index.html", {"seqs": seqs})


@login_required
@require_http_methods(["GET"])
def sequence(request, name):
    item = get_current_item(request.user, name)
    ctx = {"item": item, "sequence_name": name}
    return render(request, "fileranker/sequence.html", ctx)


@login_required
@require_http_methods(["POST"])
def answer(request):
    print(dict(request.POST))
    item_id = int(request.POST.get("item_id"))
    sequence_name = request.POST.get("sequence_name")
    value = request.POST.get("preference")
    Response.objects.create(user=request.user, item_id=item_id, value=value).save()
    return redirect("sequence", sequence_name)


def get_current_item(user, sequence_name):
    answered_items = Response.objects.filter(user=user, item=OuterRef("pk"))
    return (
        SequenceItem.objects.annotate(
            has_response=Subquery(answered_items.values("id")[:1])
        )
        .filter(has_response__isnull=True, sequence__name=sequence_name)
        .first()
    )
