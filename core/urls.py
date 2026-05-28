from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # dashboard/ authentication
    path("", views.dashboard, name="dashboard"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.register, name="register"),

    # course management
    path("courses/", views.course_list, name="course_list"),
    path("courses/new/", views.course_create, name="course_create"),
    path("courses/join/", views.course_join, name="course_join"),  # join via dynamic join code
    path("courses/<int:course_id>/edit/", views.course_edit, name="course_edit"),
    path("courses/<int:course_id>/delete/", views.course_delete, name="course_delete"),
    path("courses/<int:course_id>/leave/", views.course_leave, name="course_leave"),

    # enrollment management (roles and members)
    path("courses/<int:course_id>/enrollments/", views.manage_enrollments, name="manage_enrollments"),
    path("courses/<int:course_id>/enrollments/<int:enrollment_id>/edit/", views.enrollment_role_edit, name="enrollment_role_edit"),
    path("courses/<int:course_id>/enrollments/<int:enrollment_id>/delete/", views.enrollment_delete, name="enrollment_delete"),

    # assignments within a course
    path("courses/<int:course_id>/assignments/", views.assignment_list, name="assignment_list"),
    path("courses/<int:course_id>/assignments/new/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:assignment_id>/edit/", views.assignment_edit, name="assignment_edit"),
    path("assignments/<int:assignment_id>/delete/", views.assignment_delete, name="assignment_delete"),

    # tasks within an assignment
    path("assignments/<int:assignment_id>/tasks/", views.task_list, name="task_list"),
    path("assignments/<int:assignment_id>/tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),

    # notes on tasks
    path("tasks/<int:task_id>/notes/new/", views.note_create, name="note_create"),
    path("notes/<int:note_id>/edit/", views.note_edit, name="note_edit"),
    path("notes/<int:note_id>/delete/", views.note_delete, name="note_delete"),

    # personal notes
    path("personal-notes/", views.personal_note_list, name="personal_note_list"),
    path("personal-notes/new/", views.personal_note_create, name="personal_note_create"),
    path("personal-notes/<int:note_id>/edit/", views.personal_note_edit, name="personal_note_edit"),
    path("personal-notes/<int:note_id>/delete/", views.personal_note_delete, name="personal_note_delete"),
]