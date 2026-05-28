from django import forms
from .models import Assignment, Course, Enrollment, Note, Task, PersonalNote


# form for creating and editing courses
# uses ModelForm to automatically map fields from the Course model
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "title", "semester"]
        widgets = {
            # Bootstrap styling for inputs
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "semester": forms.TextInput(attrs={"class": "form-control"}),
        }

    # ensure course code is uppercase and trimmed
    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()

    # basic validation to prevent empty titles
    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        return title

    # Basic validation for semester field
    def clean_semester(self):
        semester = self.cleaned_data["semester"].strip()
        if not semester:
            raise forms.ValidationError("Semester is required.")
        return semester


# form for assignments linked to a course
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "status", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

# form for tasks inside an assignment
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "status", "priority", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


# form for adding notes to a task
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["content"]
        widgets = {
            # Textarea for longer text input
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# form for joining a course using a join code
# connects to the dynamic join code logic in Course model
class JoinCourseForm(forms.Form):
    join_code = forms.CharField(
        max_length=8,
        label="Course join code",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter join code",
            }
        ),
    )

    # normalize input (trim + uppercase) before lookup
    def clean_join_code(self):
        return self.cleaned_data["join_code"].strip().upper()


# form for instructors to change a user's role in a course
class EnrollmentRoleForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["role"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
        }

class PersonalNoteForm(forms.ModelForm):
    class Meta:
        model = PersonalNote
        fields = ["course", "title", "content"]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None and not user.is_staff and not user.is_superuser:
            self.fields["course"].queryset = Course.objects.filter(
                enrollment__user=user
            ).distinct().order_by("code", "semester")