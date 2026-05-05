from django.contrib import admin
from .models import Course, Assignment, Task, Note, Enrollment


# admin configuration for course model
# controls how courses are displayed in django admin panel
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "semester")


# admin configuration for assignment model
# adds filtering by status for easier management
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date", "status")
    list_filter = ("status",)


# admin configuration for task model
# shows key fields and allows filtering by status and priority
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assignment", "assigned_to", "status", "priority")
    list_filter = ("status", "priority")


# admin configuration for note model
# displays basic information about notes
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")


# admin configuration for enrollment model
# useful for managing users and their roles in courses
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "role")
    list_filter = ("role",)