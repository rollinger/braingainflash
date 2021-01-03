from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (  # DetailView, ListView;DeleteView,UpdateView,
    CreateView,
)
from flashcards.forms import CardForm, TopicForm
from flashcards.models import Card, Topic
from studygroups.models import StudyGroup

# from django.http import HttpResponseRedirect
# from django.shortcuts import render
# rom django.urls import reverse, reverse_lazy


@method_decorator(login_required, name="dispatch")
class CreateCardView(CreateView):
    model = Card
    form_class = CardForm
    template_name = "flashcards/card_create_form.html"

    def get_initial(self):
        return {
            "creator": self.request.user,
            "group": StudyGroup.objects.get(unique_id=self.kwargs["unique_group_id"]),
        }

    def get_success_url(self):
        return StudyGroup.objects.get(
            unique_id=self.kwargs["unique_group_id"]
        ).get_absolute_url()


card_create_view = CreateCardView.as_view()


@method_decorator(login_required, name="dispatch")
class CreateTopicView(CreateView):
    model = Topic
    form_class = TopicForm
    template_name = "flashcards/topic_create_form.html"

    def get_initial(self):
        return {
            "creator": self.request.user,
            "group": StudyGroup.objects.get(unique_id=self.kwargs["unique_group_id"]),
        }

    def get_success_url(self):
        return StudyGroup.objects.get(
            unique_id=self.kwargs["unique_group_id"]
        ).get_absolute_url()


topic_create_view = CreateTopicView.as_view()


# TODO
card_delete_view = CreateCardView.as_view()
card_update_view = CreateCardView.as_view()
performance_update_view = CreateCardView.as_view()
