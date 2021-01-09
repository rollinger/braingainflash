from django import forms
from studygroups.models import StudyGroup

# from django.utils.translation import ugettext_lazy as _


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = [
            "name",
            "description",
            "is_publicly_available",
            "auto_approve_new_member",
            "new_member_role",
        ]

    def __init__(self, *args, **kwargs):
        super(StudyGroupForm, self).__init__(*args, **kwargs)
        if self.instance.is_main_user_group:
            self.fields["is_publicly_available"].widget = forms.HiddenInput()
            self.fields["auto_approve_new_member"].widget = forms.HiddenInput()
            self.fields["new_member_role"].widget = forms.HiddenInput()
