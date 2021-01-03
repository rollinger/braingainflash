from django import forms
from flashcards.models import Card, Performance, Topic

# from django.utils.translation import ugettext_lazy as _


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


class TrainGainForm(forms.Form):
    card_performance_id = forms.IntegerField(widget=forms.HiddenInput())
    outcome_int = forms.IntegerField(initial=0, widget=forms.HiddenInput())
    duration_sec = forms.IntegerField(initial=0, widget=forms.HiddenInput())

    class Meta:
        fields = ["card_performance_id", "outcome_int", "duration_sec"]
