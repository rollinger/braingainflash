from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy  # what is the difference?
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (  # DetailView, ListView;DeleteView,UpdateView,
    CreateView,
    FormView,
    UpdateView,
)
from flashcards.forms import BrainGainForm, CardForm, PerformanceForm, TopicForm
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
        return StudyGroup.objects.get(
            unique_id=self.kwargs["unique_group_id"]
        ).membership_for(self.request.user)

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
        return self.get_object().group.membership_for(self.request.user)

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


# CustomRulesPermissionRequiredMixin
@method_decorator(login_required, name="dispatch")
class UpdatePerformanceView(UpdateView):
    model = Performance
    form_class = PerformanceForm
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"

    def get_success_url(self):
        return self.get_object().card.group.get_absolute_url()


performance_update_view = UpdatePerformanceView.as_view()


@method_decorator(login_required, name="dispatch")
class BrainGainView(FormView):
    """MAIN VIEW for training the cards"""

    form_class = BrainGainForm
    template_name = "flashcards/brain_gain_view.html"
    mode, group, topic = "recall", None, None
    performance_object = None
    get_params = ""

    #
    # GET
    #
    def get(self, request, *args, **kwargs):
        # Get the parameters and performance_object
        self.get_parameters()
        self.performance_object = self.get_performance_object()
        if not self.performance_object:
            # Message and return to group if no performance object
            messages.add_message(
                self.request, messages.WARNING, _("No card was found to learn.")
            )
            return HttpResponseRedirect(reverse("flashcards:brain_gain_view"))
        # render to response
        return super().get(request, *args, **kwargs)

    def get_parameters(self):
        # Get the parameters and fetch objects
        self.mode = self.request.GET.get("mode", "recall")
        if "group" in self.request.GET:
            self.group = StudyGroup.objects.filter(
                unique_id=self.request.GET.get("group")
            ).first()
        if "topic" in self.request.GET:
            self.topic = Topic.objects.filter(
                unique_id=self.request.GET.get("topic")
            ).first()
        if self.group and self.topic and (self.topic not in self.group.topics.all()):
            # topic is none if not a group topic
            self.topic = None

    def get_performance_object(self):
        # Get the performance_object for mode, group and topic
        card_performance = Performance.objects.get_performance_object_for(
            owner=self.request.user,
            mode=self.mode,
            topic=self.topic,
            group=self.group,
        )
        return card_performance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.performance_object:
            # Prepare context and form
            context["mode"] = self.mode
            context["card_performance"] = self.performance_object
            context["auto_redirect_timeout"] = context["card_performance"].learn_timeout
            context["form"].fields[
                "card_performance_id"
            ].initial = self.performance_object.pk
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Change queryset of group and topic according to the self.requst.user and get params
        # Set mode
        form.fields["mode"].initial = self.mode
        # Set group
        form.fields["group"].queryset = StudyGroup.objects.filter(
            memberships__member=self.request.user
        )
        if self.group:
            form.fields["group"].initial = self.group.pk
            # Limit topic to only group topics
            form.fields["topic"].queryset = self.group.topics
        else:
            # Disable topic field
            form.fields["topic"].widget.attrs["disabled"] = True
            form.fields["topic"].queryset = Topic.objects.filter(
                group__memberships__member=self.request.user
            )
        # Set topic initial
        if self.topic:
            form.fields["topic"].initial = self.topic.pk
        return form

    #
    # POST
    #
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Save the datapoint
        if form.cleaned_data["save_datapoint"] is True:
            self.save_performance_datapoint(form)
        # Generate GET Params
        self.get_params = "?mode=" + form.cleaned_data["mode"]
        if form.cleaned_data["group"]:
            self.get_params += "&group=%s" % form.cleaned_data["group"].unique_id
        if form.cleaned_data["topic"]:
            self.get_params += "&topic=%s" % form.cleaned_data["topic"].unique_id
        return super().form_valid(form)

    def get_success_url(self):
        # Get the success url with the current modalities as GET params
        return reverse_lazy("flashcards:brain_gain_view") + self.get_params

    def save_performance_datapoint(self, form):
        # Add the training data to the Performance object and redirect
        card_performance = Performance.objects.get(
            pk=form.cleaned_data["card_performance_id"]
        )
        if form.cleaned_data["mode"] == "train":
            card_performance.add_training_datapoint(
                form.cleaned_data["outcome_int"], form.cleaned_data["duration_sec"]
            )
        elif form.cleaned_data["mode"] == "recall":
            card_performance.add_recalling_datapoint(
                form.cleaned_data["outcome_int"], form.cleaned_data["duration_sec"]
            )
        card_performance.save()


brain_gain_view = BrainGainView.as_view()
