from __future__ import annotations

from datetime import date

from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    """ModelForm for creating and updating `Todo` items.

    Includes server-side validation to ensure the `due_date` is not in the past
    and provides a native date picker via the HTML5 date input widget.
    """

    class Meta:
        model = Todo
        fields = ["title", "description", "due_date", "completed"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Short task title"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Optional details"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_due_date(self) -> date | None:
        """Validate that `due_date`, if provided, is not in the past.

        Returns the cleaned date or None. Same-day due dates are allowed.
        """
        due = self.cleaned_data.get("due_date")
        if due and due < date.today():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due
