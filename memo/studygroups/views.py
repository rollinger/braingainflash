from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)
from flashcards.forms import CardForm, CardSearchForm
from flashcards.models import Performance
from studygroups.forms import StudyGroupForm
from studygroups.models import Membership, StudyGroup
from utils.views import CustomRulesPermissionRequiredMixin


@method_decorator(login_required, name="dispatch")
class StudyGroupListView(ListView):
    model = StudyGroup
    template_name = "studygroups/group_list_view.html"
    paginate_by = 8  # [multiples of 3 - 1 (2,5,8...)]

    def get_queryset(self, *args, **kwargs):
        # Returns group list for user
        return StudyGroup.objects.filter(memberships__member=self.request.user)

    def get_context_data(self, **kwargs):
        # Optional additional context data
        context = super(StudyGroupListView, self).get_context_data(**kwargs)
        return context


group_list_view = StudyGroupListView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupDirectoryView(ListView):
    model = StudyGroup
    template_name = "studygroups/group_directory_view.html"
    paginate_by = 9  # [multiples of 3 (3,6,9...)]

    def get_queryset(self, *args, **kwargs):
        # Returns public group list user is not a member
        return StudyGroup.objects.filter(is_publicly_available=True).filter(
            ~Q(memberships__member=self.request.user)
        )

    def get_context_data(self, **kwargs):
        # Optional additional context data
        context = super(StudyGroupDirectoryView, self).get_context_data(**kwargs)
        context["group_create_form"] = StudyGroupForm(
            initial={
                "creator": self.request.user,
            }
        )
        return context


group_directory_view = StudyGroupDirectoryView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupDetailView(CustomRulesPermissionRequiredMixin, DetailView):
    model = StudyGroup  # detail model
    permission_required = "studygroups.view_studygroup"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "studygroups/group_detail_view.html"
    paginate_by = 8  # 8  # [multiples of 3 - 1: (2,5,8...)]

    def get(self, request, *args, **kwargs):
        if "submit_reset" in self.request.GET:
            # redirect to group_detail_view with default form state
            # TODO: BUG clicking "clear" clears the form but results in an empty querset
            return HttpResponseRedirect(
                reverse(
                    "studygroups:group_detail_view",
                    kwargs={"slug": self.get_object().slug},
                )
            )
        return super().get(request, *args, **kwargs)

    def get_permission_object(self):
        return self.get_object().membership_for(self.request.user)

    def get_card_list(self):
        # Returns the card_list and filters by search and topic
        search_query = self.request.GET.get("search")
        topic_query = self.request.GET.get("topic")
        paused_query = self.request.GET.get("paused")
        priority_query = self.request.GET.get("priority")
        score_sort = self.request.GET.get("score_sort")
        # Narrow down cards
        card_list = self.object.cards.all()
        if topic_query is None and search_query is None:
            return card_list  # When search form is empty
        if topic_query:
            card_list = card_list.filter(topic__unique_id=topic_query)
        if search_query:
            card_list = card_list.filter(
                Q(front_text__icontains=search_query)
                | Q(back_text__icontains=search_query)
            )
        if paused_query != "all":
            card_list = card_list.filter(
                Q(performances__owner=self.request.user)
                & Q(performances__is_paused=paused_query)
            )
        if priority_query != "all":
            card_list = card_list.filter(
                Q(performances__owner=self.request.user)
                & Q(performances__priority=priority_query)
            )
        if score_sort == "asc":
            card_list = card_list.order_by("performances__recall_score")
        elif score_sort == "dsc":
            card_list = card_list.order_by("-performances__recall_score")
        else:
            card_list = card_list.order_by("-created_at")

        return card_list.all()

    def get_context_data(self, **kwargs):
        context = super(StudyGroupDetailView, self).get_context_data(**kwargs)
        # Get the card_list and filter by search
        card_list = self.get_card_list()
        # Add card_create_form for use in _create_card_modal.html
        card_create_form = CardForm(
            initial={
                "creator": self.request.user,
                "group": self.object,
            }
        )
        card_create_form.fields["topic"].queryset = self.object.topics
        context["card_create_form"] = card_create_form
        # Add card_edit_form for use in _edit_card_modal.html
        context["group_edit_form"] = StudyGroupForm(instance=self.object)
        # Add card search form to context
        context["card_search_form"] = self.get_card_search_form()
        paginator = Paginator(card_list, self.paginate_by)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        context["page_obj"] = page_obj
        return context

    def get_card_search_form(self):
        # builds the card search form
        card_search_form = CardSearchForm()
        card_search_form.fields["topic"].choices = [("", _("All Topics"))]
        for choice in self.object.topics.all():
            card_search_form.fields["topic"].choices.append((choice.unique_id, choice))
        card_search_form.fields["search"].initial = self.request.GET.get("search")
        card_search_form.fields["topic"].initial = self.request.GET.get("topic")
        card_search_form.fields["paused"].initial = self.request.GET.get("paused")
        card_search_form.fields["priority"].initial = self.request.GET.get("priority")
        card_search_form.fields["score_sort"].initial = self.request.GET.get(
            "score_sort"
        )
        return card_search_form


group_detail_view = StudyGroupDetailView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupCreateView(CustomRulesPermissionRequiredMixin, CreateView):
    model = StudyGroup
    permission_required = "studygroups.add_studygroup"
    fields = [
        "name",
        "description",
        "is_publicly_available",
        "auto_approve_new_member",
        "new_member_role",
    ]
    template_name = "studygroups/group_create_view.html"
    success_url = reverse_lazy("studygroups:group_list_view")

    def get_permission_object(self):
        # No membership permission object required
        return None

    def form_valid(self, form):
        # save form
        # handle slug and membership for the user
        study_group = form.save()
        membership, created = Membership.objects.get_or_create(
            member=self.request.user, group=study_group, role="admin", approved=True
        )
        return super().form_valid(form)


group_create_view = StudyGroupCreateView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupUpdateView(CustomRulesPermissionRequiredMixin, UpdateView):
    model = StudyGroup
    permission_required = "studygroups.edit_studygroup"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    form_class = StudyGroupForm
    template_name = "studygroups/group_update_view.html"
    # success_url comes from object.get_absolute_url

    def get_permission_object(self):
        return self.get_object().membership_for(self.request.user)


group_update_view = StudyGroupUpdateView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupDeleteView(CustomRulesPermissionRequiredMixin, DeleteView):
    model = StudyGroup
    permission_required = "studygroups.edit_studygroup"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    template_name = "studygroups/group_confirm_delete.html"
    success_url = reverse_lazy("studygroups:group_list_view")

    def get_permission_object(self):
        return self.get_object().membership_for(self.request.user)


group_delete_view = StudyGroupDeleteView.as_view()


@method_decorator(login_required, name="dispatch")
class InviteStudyGroupRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        group = StudyGroup.objects.get(slug=self.kwargs["slug"])
        return reverse_lazy(
            "studygroups:group_join_view", kwargs={"unique_id": group.unique_id}
        )


group_invite_view = InviteStudyGroupRedirectView.as_view()


@method_decorator(login_required, name="dispatch")
class JoinStudyGroupRedirectView(RedirectView):
    url = reverse_lazy("studygroups:group_list_view")

    def get(self, request, *args, **kwargs):
        # Get or create a membership and sets a message
        #
        # TODO: CHECK if user.plan allows for addition of another group
        # And redirect to upgrade_plan
        study_group = StudyGroup.objects.get(unique_id=self.kwargs["unique_id"])
        membership, created = Membership.objects.get_or_create(
            member=self.request.user,
            group=study_group,
            role=study_group.new_member_role,
            approved=study_group.auto_approve_new_member,
        )
        # Get or create performance objects for all cards|request.user
        for card in study_group.cards.all():
            p, c = Performance.objects.get_or_create(owner=request.user, card=card)
        # Set Message for joining
        approval_msg = ""
        if study_group.auto_approve_new_member:
            approval_msg = _("Your were approved immediately.")
        else:
            approval_msg = _("Please be patient and wait for approval.")
        messages.add_message(
            self.request,
            messages.SUCCESS,
            _('You joined the study group "{group_name}". {approval_msg}').format(
                group_name=study_group.name, approval_msg=approval_msg
            ),
        )
        return super().get(request, *args, **kwargs)


group_join_view = JoinStudyGroupRedirectView.as_view()


@method_decorator(login_required, name="dispatch")
class LeaveStudyGroupRedirectView(RedirectView):
    url = reverse_lazy("studygroups:group_list_view")

    def get(self, request, *args, **kwargs):
        # Deletes the membership and sets a message
        study_group = StudyGroup.objects.get(unique_id=self.kwargs["unique_id"])
        if study_group.is_member(request.user):
            Membership.objects.get(
                member=self.request.user,
                group=study_group,
            ).delete()
            # Delete performance objects for all cards|request.user
            for card in study_group.cards.all():
                Performance.objects.filter(owner=request.user, card=card).delete()
            # Set Leave message
            messages.add_message(
                self.request,
                messages.WARNING,
                _('You left the study group "{group_name}".').format(
                    group_name=study_group.name,
                ),
            )
        return super().get(request, *args, **kwargs)


group_leave_view = LeaveStudyGroupRedirectView.as_view()


@method_decorator(login_required, name="dispatch")
class ManageMembershipRedirectView(CustomRulesPermissionRequiredMixin, RedirectView):
    permission_required = "studygroups.manage_studygroup_memberships"
    # TODO: Refactor with SingleObjectMixin view to get the membership-to-manage by unique_id

    def get_permission_object(self):
        admin_membership = Membership.objects.get(
            unique_id=self.kwargs["unique_id"]
        ).group.membership_for(self.request.user)
        return admin_membership

    def get(self, request, *args, **kwargs):
        # Manage the membership and sets a message
        unique_id = self.kwargs["unique_id"]
        verb = self.kwargs["verb"]
        membership = Membership.objects.get(unique_id=unique_id)
        # Set redirect url
        self.url = reverse_lazy(
            "studygroups:group_detail_view", kwargs={"slug": membership.group.slug}
        )
        # Change membership verbs: [approve, block, make_viewer, make_editor, make_admin]
        # and save changes
        if membership:
            if verb == "approve":
                membership.approved = True
                membership.blocked = False
            elif verb == "block":
                membership.approved = False
                membership.blocked = True
            elif verb == "make_viewer":
                membership.role = "viewer"
            elif verb == "make_editor":
                membership.role = "editor"
            elif verb == "make_admin":
                membership.role = "admin"
            membership.save()
        # Call super get leading to redirect
        return super().get(request, *args, **kwargs)


membership_manage_view = ManageMembershipRedirectView.as_view()
