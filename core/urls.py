from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # Courses
    path("courses/", views.course_list, name="course_list"),
    path("courses/new/", views.course_create, name="course_create"),

    # Assignments
    path("courses/<int:course_id>/assignments/", views.assignment_list, name="assignment_list"),
    path("courses/<int:course_id>/assignments/new/", views.assignment_create, name="assignment_create"),

    # ✅ NEW: assignment edit/delete
    path("assignments/<int:assignment_id>/edit/", views.assignment_edit, name="assignment_edit"),
    path("assignments/<int:assignment_id>/delete/", views.assignment_delete, name="assignment_delete"),

    # Tasks
    path("assignments/<int:assignment_id>/tasks/", views.task_list, name="task_list"),
    path("assignments/<int:assignment_id>/tasks/new/", views.task_create, name="task_create"),

    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),

    # Notes
    path("tasks/<int:task_id>/notes/new/", views.note_create, name="note_create"),
    path("notes/<int:note_id>/edit/", views.note_edit, name="note_edit"),
    path("notes/<int:note_id>/delete/", views.note_delete, name="note_delete"),

    path("courses/<int:course_id>/edit/", views.course_edit, name="course_edit"),
    path("courses/<int:course_id>/delete/", views.course_delete, name="course_delete"), 

    path("register/", views.register, name="register"),
]