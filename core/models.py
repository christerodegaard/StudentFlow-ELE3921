from django.contrib.auth.models import User
from django.db import models
import secrets
import string


# Generates a random code used for joining a course
def generate_join_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for i in range(length))


# Represents a course with basic info and a join code
class Course(models.Model):
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    semester = models.CharField(max_length=50)

    # Join code used by students to enroll in the course
    join_code = models.CharField(max_length=8, unique=True, blank=True, editable=False)

    class Meta:
        ordering = ["code", "semester"]
        constraints = [
            # Prevent duplicate courses with same code and semester
            models.UniqueConstraint(
                fields=["code", "semester"],
                name="unique_course_code_semester",
            )
        ]

    def save(self, *args, **kwargs):
        # dynamic join code generation
        # if no join code is set, generate one automatically
        # ensures the code is unique before saving
        if not self.join_code:
            code = generate_join_code()
            while Course.objects.filter(join_code=code).exclude(pk=self.pk).exists():
                code = generate_join_code()
            self.join_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.title} ({self.semester})"


# links a user to a course with a specific role
class Enrollment(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("ta", "TA"),
        ("instructor", "Instructor"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    class Meta:
        ordering = ["course", "user"]
        constraints = [
            # Each user can only be enrolled once per course
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment",
            )
        ]

    # Used to check if user can manage course content
    def is_manager(self):
        return self.role in {"ta", "instructor"}

    def is_instructor(self):
        return self.role == "instructor"

    def __str__(self):
        return f"{self.user} in {self.course} ({self.role})"


# Assignment belongs to a course
class Assignment(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Not started"),
        ("in_progress", "In progress"),
        ("done", "Done"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.course.code}: {self.title}"


# Task belongs to an assignment and is assigned to a user
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

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


# Notes can be added to tasks by users
class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.author} on {self.task}"