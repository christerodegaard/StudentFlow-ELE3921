from django import forms
from .models import Course
from .models import Assignment
from .models import Task
from .models import Note




class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "title", "semester"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "semester": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        if not code:
            raise forms.ValidationError("Course code is required.")
        return code
    

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "status", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        return title

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

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Task title is required.")
        return title
    

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("Note content is required.")
        return content