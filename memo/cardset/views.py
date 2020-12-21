# from django.shortcuts import render
from cardset.models import MemoCard, MemoSet
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (  # CreateView,; DeleteView,; UpdateView,
    DetailView,
    ListView,
)


@method_decorator(login_required, name="dispatch")
class MemoSetRootListView(ListView):
    model = MemoSet
    context_object_name = "rootlist"
    template_name = "cardset/memoset_root_list.html"

    def get_queryset(self, *args, **kwargs):
        return MemoSet.get_root_nodes().filter(owner=self.request.user)
        # qs = super(MemoSetRootListView, self).get_queryset(*args, **kwargs)
        # qs = qs.filter(owner=self.request.user)
        # return qs

    def get_context_data(self, **kwargs):
        context = super(MemoSetRootListView, self).get_context_data(**kwargs)
        # context['friends'] = self.object.friends.order_by(
        #    'from_user__last_name')
        print(context)
        # context['rootlist'] = context
        return context


memoset_root_list_view = MemoSetRootListView.as_view()


class MemoSetDetailView(DetailView):
    model = MemoSet


memoset_detail_view = MemoSetDetailView.as_view()


class MemoCardDetailView(DetailView):
    model = MemoCard


memocard_detail_view = MemoCardDetailView.as_view()
