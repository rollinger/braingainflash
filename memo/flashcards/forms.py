from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout, Submit
from django import forms
from django.utils.translation import ugettext_lazy as _
from flashcards.models import LEARNING_PRIORITIES, Card, Performance, Topic
from studygroups.models import StudyGroup

LEARNING_PRIORITIES = (("all", _("All")),) + LEARNING_PRIORITIES


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["creator", "group", "topic", "front_text", "back_text"]
        widgets = {
            "creator": forms.HiddenInput(),
            "group": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False  # To suppress multiple ckeditor loads


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ["is_paused", "priority", "learn_timeout", "recall_timeout"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class CardSearchForm(forms.Form):
    search = forms.CharField(required=False)
    topic = forms.ChoiceField(required=False)
    paused = forms.ChoiceField(
        choices=(("all", _("All")), (False, _("Active")), (True, _("Inactive")))
    )
    priority = forms.ChoiceField(
        choices=LEARNING_PRIORITIES,  # (("all", _("All")),)
    )
    score_sort = forms.ChoiceField(
        choices=(
            ("no_sort", _("No Sort")),
            ("asc", _("Ascending")),
            ("dsc", _("Descending")),
        )
    )

    class Meta:
        fields = ["search", "topic"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap4/layout/inline_field.html"
        self.helper.layout = Layout(
            Div(InlineField("search", css_class=""), css_class="w-100"),
            InlineField("topic", css_class="custom-select", title=_("Filter by topic")),
            InlineField(
                "paused", css_class="custom-select", title=_("Filter by paused")
            ),
            InlineField(
                "priority", css_class="custom-select", title=_("Filter by priority")
            ),
            HTML("<small>Sort Score:</small>"),
            InlineField(
                "score_sort", css_class="custom-select", title=_("Sort by score")
            ),
            Submit("submit_filter", _("Filter"), css_class="btn-primary"),
            Submit("submit_reset", _("Clear"), css_class="btn-secondary"),
        )


class BrainGainForm(forms.Form):
    mode = forms.ChoiceField(choices=(("train", _("Cycle")), ("recall", _("Recall"))))
    group = forms.ModelChoiceField(
        queryset=StudyGroup.objects.none(), empty_label=_("All Groups"), required=False
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.none(), empty_label=_("All Topics"), required=False
    )
    card_performance_id = forms.IntegerField(widget=forms.HiddenInput())
    outcome_int = forms.IntegerField(initial=0, widget=forms.HiddenInput())
    duration_sec = forms.IntegerField(initial=0, widget=forms.HiddenInput())
    save_datapoint = forms.BooleanField(
        initial=False, required=False, widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.field_template = "bootstrap4/layout/inline_field.html"
        self.helper.layout = Layout(
            InlineField("mode", css_class=""),
            InlineField("group", css_class=""),
            InlineField("topic", css_class=""),
            InlineField("card_performance_id", css_class=""),
            InlineField("outcome_int", css_class=""),
            InlineField("duration_sec", css_class=""),
            InlineField("save_datapoint", css_class=""),
            Submit("next", _("Filter"), css_class="btn-primary"),
        )
