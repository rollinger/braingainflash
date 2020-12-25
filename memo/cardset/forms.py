from cardset.models import MemoCard, MemoSet  # MemoCardPerformance,
from django import forms
from django.utils.translation import ugettext_lazy as _
from treebeard.forms import MoveNodeForm, movenodeform_factory


# See: https://django-treebeard.readthedocs.io/en/latest/forms.html
class MemoSetTreebeardForm(MoveNodeForm):
    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop("creator", None)
        selected_parent = kwargs.pop("selected_parent", "0")
        super(MemoSetTreebeardForm, self).__init__(*args, **kwargs)
        self.fields["creator"].initial = self.creator
        self.fields["creator"].widget = forms.HiddenInput()
        self.fields["_ref_node_id"].initial = selected_parent

    def mk_dropdown_tree(self, model, for_node=None):
        """Creates a tree-like list of choices only for the user MemoSets
        forked: https://github.com/django-treebeard/django-treebeard/blob/master/treebeard/forms.py
        """
        options = [(0, _("-- root --"))]
        for node in model.get_rootlist_for(self.creator).all():
            self.add_subtree(for_node, node, options)
        return options


MemoSetTreebeardFormFactory = movenodeform_factory(MemoSet, form=MemoSetTreebeardForm)


class MemoCardForm(forms.ModelForm):
    class Meta:
        model = MemoCard
        fields = ["creator", "memoset", "topic", "question_text", "answer_text"]
        widgets = {"creator": forms.HiddenInput(), "memoset": forms.HiddenInput()}


class TrainGainForm(forms.Form):
    card_performance_id = forms.IntegerField()  # forms.UUIDField()
    outcome_int = forms.IntegerField(initial=1)
    duration_sec = forms.IntegerField(initial=0)

    class Meta:
        fields = ["card_performance_id", "outcome_int", "duration_sec"]
        widgets = {
            "card_performance_id": forms.HiddenInput(),
            "outcome_int": forms.HiddenInput(),
            "duration_sec": forms.HiddenInput(),
        }
