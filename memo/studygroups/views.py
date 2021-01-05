from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse_lazy
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
from flashcards.models import Performance
from studygroups.forms import StudyGroupForm
from studygroups.models import Membership, StudyGroup
from utils.views import CustomRulesPermissionRequiredMixin


@method_decorator(login_required, name="dispatch")
class StudyGroupListView(ListView):
    model = StudyGroup
    template_name = "studygroups/group_list_view.html"

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

    def get_queryset(self, *args, **kwargs):
        # Returns public group list user is not a member
        return StudyGroup.objects.filter(is_publicly_available=True).filter(
            ~Q(memberships__member=self.request.user)
        )

    def get_context_data(self, **kwargs):
        # Optional additional context data
        context = super(StudyGroupDirectoryView, self).get_context_data(**kwargs)
        return context


group_directory_view = StudyGroupDirectoryView.as_view()


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
class StudyGroupDetailView(CustomRulesPermissionRequiredMixin, DetailView):
    model = StudyGroup
    permission_required = "studygroups.view_studygroup"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "studygroups/group_detail_view.html"


group_detail_view = StudyGroupDetailView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupUpdateView(CustomRulesPermissionRequiredMixin, UpdateView):
    model = StudyGroup
    permission_required = "studygroups.edit_studygroup"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    form_class = StudyGroupForm
    template_name = "studygroups/group_update_view.html"
    # success_url comes from object.get_absolute_url


group_update_view = StudyGroupUpdateView.as_view()


@method_decorator(login_required, name="dispatch")
class StudyGroupDeleteView(CustomRulesPermissionRequiredMixin, DeleteView):
    model = StudyGroup
    permission_required = "studygroups.edit_studygroup"
    slug_field = "unique_id"
    slug_url_kwarg = "unique_id"
    template_name = "studygroups/group_confirm_delete.html"
    success_url = reverse_lazy("studygroups:group_list_view")


group_delete_view = StudyGroupDeleteView.as_view()


@method_decorator(login_required, name="dispatch")
class JoinStudyGroupRedirectView(RedirectView):
    url = reverse_lazy("studygroups:group_list_view")

    def get(self, request, *args, **kwargs):
        # Get or create a membership and sets a message
        # TODO: CHECK if user.plan allows for addition of another group
        study_group = StudyGroup.objects.get(unique_id=self.kwargs["unique_id"])
        if study_group.is_member(request.user):
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

    def get_permission_object(self):
        unique_id = self.kwargs["unique_id"]
        return Membership.objects.get(unique_id=unique_id).group

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
