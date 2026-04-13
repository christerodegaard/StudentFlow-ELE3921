from django.contrib import admin
from .models import Course, Assignment, Task, Note, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "semester")
    search_fields = ("code", "title", "semester")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date", "status")
    list_filter = ("course", "status")
    search_fields = ("title",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assignment", "assigned_to", "status", "priority", "due_date")
    list_filter = ("status", "priority", "assignment__course")
    search_fields = ("title",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    list_filter = ("author",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "role")
    list_filter = ("role", "course")
    search_fields = ("user__username", "course__code", "course__title")