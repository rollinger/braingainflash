# from django.shortcuts import render
from cardset.forms import (
    MemoCardForm,
    MemoCardPerformanceForm,
    MemoSetTreebeardFormFactory,
    TrainGainForm,
)
from cardset.models import MemoCard, MemoCardPerformance, MemoSet
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (  # DetailView;
    CreateView,
    DeleteView,
    FormView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import ModelFormMixin
from rules.contrib.views import PermissionRequiredMixin as PermissionRulesRequiredMixin


#
# Memo Sets
#
@method_decorator(login_required, name="dispatch")
class RootListMemoSetView(ListView):
    model = MemoSet
    context_object_name = "rootlist"
    template_name = "cardset/memoset_root_list.html"

    def get_queryset(self, *args, **kwargs):
        # Returns root list for user
        return MemoSet.get_root_nodes().filter(creator=self.request.user)

    def get_context_data(self, **kwargs):
        # Optional additional context data
        context = super(RootListMemoSetView, self).get_context_data(**kwargs)
        return context


memoset_root_list_view = RootListMemoSetView.as_view()


class MemoSetModelFormMixin(ModelFormMixin):
    """ Mixin to handle get_success_url and the user list of memo lists"""

    def get_form_kwargs(self):
        kwargs = super(MemoSetModelFormMixin, self).get_form_kwargs()
        kwargs.update({"creator": self.request.user})
        if "unique_id" in self.kwargs:
            kwargs.update(
                {
                    "selected_parent": str(
                        MemoSet.objects.get_by_unique_id(
                            unique_id=self.kwargs["unique_id"]
                        ).pk
                    )
                }
            )
        else:
            kwargs.update({"selected_parent": "0"})
        return kwargs

    """
    def get_success_url(self):
        return reverse("cardset:memoset_root_list_view")
    """


@method_decorator(login_required, name="dispatch")
class CreateMemoSetView(MemoSetModelFormMixin, CreateView):
    model = MemoSet
    form_class = MemoSetTreebeardFormFactory
    template_name = "cardset/memoset_create_form.html"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memoset_create_view = CreateMemoSetView.as_view()


@method_decorator(login_required, name="dispatch")
class UpdateMemoSetView(MemoSetModelFormMixin, UpdateView):
    model = MemoSet
    form_class = MemoSetTreebeardFormFactory
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    template_name = "cardset/memoset_update_form.html"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memoset_update_view = UpdateMemoSetView.as_view()


@method_decorator(login_required, name="dispatch")
class DeleteMemoSetView(DeleteView):
    model = MemoSet
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memoset_delete_view = DeleteMemoSetView.as_view()


#
# Memo Cards
#
@method_decorator(login_required, name="dispatch")
class CreateMemoCardView(CreateView):
    model = MemoCard
    form_class = MemoCardForm
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    template_name = "cardset/memocard_create_form.html"
    success_url = reverse_lazy("cardset:memoset_root_list_view")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["memoset"] = MemoSet.objects.get_by_unique_id(self.kwargs["unique_id"])
        return data

    def get_initial(self):
        return {
            "creator": self.request.user,
            "memoset": MemoSet.objects.get_by_unique_id(self.kwargs["unique_id"]),
        }


memocard_create_view = CreateMemoCardView.as_view()


@method_decorator(login_required, name="dispatch")
class UpdateMemoCardView(PermissionRulesRequiredMixin, UpdateView):
    # PermissionRulesRequiredMixin DOES NOT WORK YET... diff test_rule / has_perm???
    model = MemoCard
    form_class = MemoCardForm
    permission_required = "can_update_memocard"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    template_name = "cardset/memocard_update_form.html"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memocard_update_view = UpdateMemoCardView.as_view()


@method_decorator(login_required, name="dispatch")
class DeleteMemoCardView(PermissionRulesRequiredMixin, DeleteView):
    # PermissionRulesRequiredMixin DOES NOT WORK YET... diff test_rule / has_perm???
    model = MemoCard
    permission_required = "can_delete_memocard"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memocard_delete_view = DeleteMemoCardView.as_view()


@method_decorator(login_required, name="dispatch")
class UpdateMemoCardPerformanceView(PermissionRulesRequiredMixin, UpdateView):
    # PermissionRulesRequiredMixin DOES NOT WORK YET... diff test_rule / has_perm???
    model = MemoCardPerformance
    form_class = MemoCardPerformanceForm
    permission_required = "can_update_memocardperformance"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    template_name = "cardset/memocardperformance_update_form.html"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memocardperformance_update_view = UpdateMemoCardPerformanceView.as_view()


@method_decorator(login_required, name="dispatch")
class TrainGainView(FormView):
    form_class = TrainGainForm
    template_name = "cardset/train_gain_view.html"
    success_url = reverse_lazy("cardset:train_gain_view")

    def get(self, request, *args, **kwargs):
        # Get the least learned object and prepare form initial and context_data
        obj = MemoCardPerformance.objects.get_least_learned_object_for(
            user=self.request.user
        )
        if not obj:
            return HttpResponseRedirect(reverse("cardset:memoset_root_list_view"))
        self.extra_context = {
            "card_performance": obj,
            "auto_redirect_timeout": obj.learning_timeout,
        }
        self.initial["card_performance_id"] = obj.pk
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # Add the training data to the MemoCardPerformance object and redirect
        card_performance = MemoCardPerformance.objects.get(
            pk=form.cleaned_data["card_performance_id"]
        )
        card_performance.add_learning_datapoint(
            form.cleaned_data["outcome_int"], form.cleaned_data["duration_sec"]
        )
        card_performance.save()
        return super().form_valid(form)


train_gain_view = TrainGainView.as_view()


@method_decorator(login_required, name="dispatch")
class TestGainView(FormView):
    form_class = TrainGainForm
    template_name = "cardset/test_gain_view.html"
    success_url = reverse_lazy("cardset:test_gain_view")

    def get(self, request, *args, **kwargs):
        # Get the least recalled object and prepare form initial and context_data
        obj = MemoCardPerformance.objects.get_least_recalled_object_for(
            user=self.request.user
        )
        if not obj:
            return HttpResponseRedirect(reverse("cardset:memoset_root_list_view"))
        self.extra_context = {
            "card_performance": obj,
            "auto_redirect_timeout": obj.learning_timeout,
        }
        self.initial["card_performance_id"] = obj.pk
        self.initial["outcome_int"] = 0
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        # Add the training data to the MemoCardPerformance object and redirect
        card_performance = MemoCardPerformance.objects.get(
            pk=form.cleaned_data["card_performance_id"]
        )
        card_performance.add_recalling_datapoint(
            form.cleaned_data["outcome_int"], form.cleaned_data["duration_sec"]
        )
        card_performance.save()
        return super().form_valid(form)


test_gain_view = TestGainView.as_view()
