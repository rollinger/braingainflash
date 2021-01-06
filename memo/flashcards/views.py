from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import (  # DetailView, ListView;DeleteView,UpdateView,
    CreateView,
    UpdateView,
)
from flashcards.forms import CardForm, TopicForm
from flashcards.models import Card, Topic
from studygroups.models import StudyGroup
from utils.views import CustomRulesPermissionRequiredMixin

# from django.http import HttpResponseRedirect
# from django.shortcuts import render
# rom django.urls import reverse, reverse_lazy


@method_decorator(login_required, name="dispatch")
class CreateTopicView(CustomRulesPermissionRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    permission_required = "studygroups.manage_studygroup_topic"
    template_name = "flashcards/topic_create_form.html"

    def get_permission_object(self):
        unique_id = self.kwargs["unique_group_id"]
        return StudyGroup.objects.get(unique_id=unique_id)

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


@method_decorator(login_required, name="dispatch")
class UpdateDeleteTopicView(CustomRulesPermissionRequiredMixin, UpdateView):
    model = Topic
    form_class = TopicForm
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    permission_required = "studygroups.manage_studygroup_topic"
    template_name = "flashcards/topic_update_form.html"

    def get_permission_object(self):
        return self.get_object().group

    def form_valid(self, form):
        if "delete" in form.data:
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        elif "update" in form.data:
            # self.object = form.save() # double execution
            return super().form_valid(form)

    def get_success_url(self):
        return self.get_object().group.get_absolute_url()


topic_update_delete_view = UpdateDeleteTopicView.as_view()


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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit choices to group topics
        form.fields["topic"].queryset = Topic.objects.filter(
            group__unique_id=self.kwargs["unique_group_id"]
        )
        return form

    def get_success_url(self):
        return StudyGroup.objects.get(
            unique_id=self.kwargs["unique_group_id"]
        ).get_absolute_url()


card_create_view = CreateCardView.as_view()


@method_decorator(login_required, name="dispatch")
class UpdateDeleteCardView(CustomRulesPermissionRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    permission_required = "studygroups.manage_studygroup_card"
    template_name = "flashcards/card_update_form.html"

    def get_permission_object(self):
        return self.get_object().group

    def form_valid(self, form):
        if "delete" in form.data:
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        elif "update" in form.data:
            # self.object = form.save() # double execution
            return super().form_valid(form)

    def get_success_url(self):
        return self.get_object().group.get_absolute_url()


card_update_delete_view = UpdateDeleteCardView.as_view()


# TODO
card_delete_view = CreateCardView.as_view()
card_update_view = CreateCardView.as_view()
performance_update_view = CreateCardView.as_view()
