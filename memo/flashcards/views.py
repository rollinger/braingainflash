from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy  # what is the difference?
from django.utils.decorators import method_decorator
from django.views.generic import (  # DetailView, ListView;DeleteView,UpdateView,
    CreateView,
    FormView,
    UpdateView,
)
from flashcards.forms import CardForm, TopicForm, TrainGainForm
from flashcards.models import Card, Performance, Topic
from studygroups.models import StudyGroup
from utils.views import CustomRulesPermissionRequiredMixin

# from django.shortcuts import render


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


@method_decorator(login_required, name="dispatch")
class TrainCardsView(FormView):
    form_class = TrainGainForm
    template_name = "flashcards/train_cards_view.html"
    success_url = reverse_lazy("flashcards:train_cards_view")

    def get(self, request, *args, **kwargs):
        # Get the least learned object and prepare form initial and context_data
        obj = Performance.objects.get_least_learned_object_for(owner=self.request.user)
        if not obj:
            return HttpResponseRedirect(reverse("studygroups:group_list_view"))
        self.extra_context = {
            "card_performance": obj,
            "auto_redirect_timeout": obj.learn_timeout,  # REF
        }
        self.initial["card_performance_id"] = obj.pk
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # Add the training data to the MemoCardPerformance object and redirect
        card_performance = Performance.objects.get(
            pk=form.cleaned_data["card_performance_id"]
        )
        card_performance.add_learning_datapoint(
            form.cleaned_data["outcome_int"], form.cleaned_data["duration_sec"]
        )
        card_performance.save()
        return super().form_valid(form)


train_cards_view = TrainCardsView.as_view()


@method_decorator(login_required, name="dispatch")
class TestCardView(FormView):
    form_class = TrainGainForm
    template_name = "flashcards/test_cards_view.html"
    success_url = reverse_lazy("flashcards:test_cards_view")

    def get(self, request, *args, **kwargs):
        # Get the least recalled object and prepare form initial and context_data
        obj = Performance.objects.get_least_recalled_object_for(owner=self.request.user)
        if not obj:
            return HttpResponseRedirect(reverse("studygroups:group_list_view"))
        self.extra_context = {
            "card_performance": obj,
            "auto_redirect_timeout": obj.recall_timeout,
        }
        self.initial["card_performance_id"] = obj.pk
        self.initial["outcome_int"] = 0
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # Add the training data to the Performance object and redirect
        card_performance = Performance.objects.get(
            pk=form.cleaned_data["card_performance_id"]
        )
        card_performance.add_recalling_datapoint(
            form.cleaned_data["outcome_int"], form.cleaned_data["duration_sec"]
        )
        card_performance.save()
        return super().form_valid(form)


test_cards_view = TestCardView.as_view()
