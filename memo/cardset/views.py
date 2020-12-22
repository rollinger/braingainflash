# from django.shortcuts import render
from cardset.forms import MemoSetTreebeardFormFactory
from cardset.models import MemoCard, MemoSet
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import ModelFormMixin


@method_decorator(login_required, name="dispatch")
class RootListMemoSetView(ListView):
    model = MemoSet
    context_object_name = "rootlist"
    template_name = "cardset/memoset_root_list.html"

    def get_queryset(self, *args, **kwargs):
        # Returns root list for user
        return MemoSet.get_root_nodes().filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        # Optional additional context data
        context = super(RootListMemoSetView, self).get_context_data(**kwargs)
        return context


memoset_root_list_view = RootListMemoSetView.as_view()


class MemoSetModelFormMixin(ModelFormMixin):
    """ Mixin to handle get_success_url and the user list of memo lists"""

    def get_form_kwargs(self):
        kwargs = super(MemoSetModelFormMixin, self).get_form_kwargs()
        kwargs.update({"owner": self.request.user})
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

    def get_success_url(self):
        return reverse("cardset:memoset_root_list_view")


@method_decorator(login_required, name="dispatch")
class CreateMemoSetView(MemoSetModelFormMixin, CreateView):
    model = MemoSet
    form_class = MemoSetTreebeardFormFactory


memoset_create_view = CreateMemoSetView.as_view()


@method_decorator(login_required, name="dispatch")
class UpdateMemoSetView(MemoSetModelFormMixin, UpdateView):
    model = MemoSet
    form_class = MemoSetTreebeardFormFactory
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"

    def get_success_url(self):
        return reverse("cardset:memoset_root_list_view")


memoset_update_view = UpdateMemoSetView.as_view()


@method_decorator(login_required, name="dispatch")
class DeleteMemoSetView(DeleteView):
    model = MemoSet
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    success_url = reverse_lazy("cardset:memoset_root_list_view")


memoset_delete_view = DeleteMemoSetView.as_view()


class MemoSetDetailView(DetailView):
    model = MemoSet


memoset_detail_view = MemoSetDetailView.as_view()


class MemoCardDetailView(DetailView):
    model = MemoCard


memocard_detail_view = MemoCardDetailView.as_view()
