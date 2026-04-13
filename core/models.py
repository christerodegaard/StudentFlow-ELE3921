# core/models.py
from django.conf import settings
from django.db import models


class Course(models.Model):
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    semester = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.code} — {self.title} ({self.semester})"


class Enrollment(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("ta", "TA"),
        ("instructor", "Instructor"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment_user_course")
        ]

    def __str__(self):
        return f"{self.user} in {self.course} ({self.role})"


class Assignment(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not started"),
        ("in_progress", "In progress"),
        ("done", "Done"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.course.code}: {self.title}"


class Task(models.Model):
    STATUS_CHOICES = [
        ("todo", "To do"),
        ("doing", "Doing"),
        ("done", "Done"),
    ]
    PRIORITY_CHOICES = [
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.author} on {self.task}"