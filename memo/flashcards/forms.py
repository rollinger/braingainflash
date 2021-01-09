from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.utils.translation import ugettext_lazy as _
from flashcards.models import Card, Performance, Topic


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["creator", "group", "topic", "front_text", "back_text"]
        widgets = {
            "creator": forms.HiddenInput(),
            "group": forms.HiddenInput(),
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            "title",
            "group",
        ]
        widgets = {
            "group": forms.HiddenInput(),
        }


class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ["is_paused", "priority", "learn_timeout", "recall_timeout"]


class CardSearchForm(forms.Form):
    search = forms.CharField(required=False)
    topic = forms.ChoiceField(required=False)

    class Meta:
        fields = ["search", "topic"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap4/layout/inline_field.html"
        self.helper.layout = Layout(
            InlineField("search", css_class=""),
            InlineField("topic", css_class="custom-select"),
            Submit("submit", _("Filter"), css_class="btn-primary"),
        )


class TrainGainForm(forms.Form):
    # "topic",  topic = forms.ModelChoiceField(queryset=None, empty_label=_("All"), required=False)
    card_performance_id = forms.IntegerField(widget=forms.HiddenInput())
    outcome_int = forms.IntegerField(initial=0, widget=forms.HiddenInput())
    duration_sec = forms.IntegerField(initial=0, widget=forms.HiddenInput())

    class Meta:
        fields = ["card_performance_id", "outcome_int", "duration_sec"]
