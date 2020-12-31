from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, RedirectView
from studygroups.models import Membership, StudyGroup


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
class StudyGroupCreateView(CreateView):
    model = StudyGroup
    fields = [
        "name",
        "description",
        "is_publicly_available",
        "auto_approve_new_member",
        "new_member_role",
    ]
    template_name = "studygroups/studygroup_create_form.html"
    success_url = reverse_lazy("studygroups:group_list_view")

    def form_valid(self, form):
        # save form
        # handle slug and membership for the user
        study_group = form.save()
        membership, created = Membership.objects.get_or_create(
            member=self.request.user, group=study_group, role=2, approved=True
        )
        return super().form_valid(form)


group_create_view = StudyGroupCreateView.as_view()


class JoinStudyGroupRedirectView(RedirectView):
    success_url = reverse_lazy("studygroups:group_list_view")

    def get(self, request, *args, **kwargs):
        # Get or create a membership and sets a message
        study_group = StudyGroup.objects.get(unique_id=self.kwargs["unique_id"])
        if study_group.is_member(request.user):
            membership, created = Membership.objects.get_or_create(
                member=self.request.user,
                group=study_group,
                role=study_group.new_member_role,
                approved=study_group.auto_approve_new_member,
            )


group_join_view = JoinStudyGroupRedirectView.as_view()
