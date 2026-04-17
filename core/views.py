from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from datetime import timedelta
from django.utils import timezone

from .forms import (
    AssignmentForm,
    CourseForm,
    EnrollmentRoleForm,
    JoinCourseForm,
    NoteForm,
    TaskForm,
)
from .models import Assignment, Course, Enrollment, Note, Task
from .permissions import user_has_course_role, user_is_course_member


@login_required
def dashboard(request):
    today = timezone.localdate()
    next_week = today + timedelta(days=7)

    if request.user.is_staff or request.user.is_superuser:
        courses = Course.objects.all()
        tasks = Task.objects.select_related("assignment", "assignment__course", "assigned_to").all()
    else:
        courses = Course.objects.filter(enrollment__user=request.user).distinct()
        tasks = Task.objects.select_related("assignment", "assignment__course", "assigned_to").filter(
            assigned_to=request.user
        )

    selected_course = request.GET.get("course")
    selected_status = request.GET.get("status")
    selected_due_date = request.GET.get("due_date")

    if selected_course:
        tasks = tasks.filter(assignment__course_id=selected_course)

    if selected_status:
        tasks = tasks.filter(status=selected_status)

    if selected_due_date == "overdue":
        tasks = tasks.filter(due_date__lt=today).exclude(status="done")
    elif selected_due_date == "7days":
        tasks = tasks.filter(due_date__range=[today, next_week]).exclude(status="done")
    elif selected_due_date == "today":
        tasks = tasks.filter(due_date=today)

    overdue = tasks.filter(due_date__lt=today).exclude(status="done").order_by("due_date")
    due_soon = tasks.filter(due_date__range=[today, next_week]).exclude(status="done").order_by("due_date")
    todo_tasks = tasks.filter(status="todo").order_by("due_date")
    in_progress_tasks = tasks.filter(status="doing").order_by("due_date")
    completed_tasks = tasks.filter(status="done").order_by("-due_date")

    context = {
        "courses": courses,
        "selected_course": selected_course,
        "selected_status": selected_status,
        "selected_due_date": selected_due_date,
        "overdue": overdue,
        "due_soon": due_soon,
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
    }
    return render(request, "dashboard.html", context)

@login_required
def course_list(request):
    if request.user.is_staff or request.user.is_superuser:
        courses = Course.objects.all().order_by("code", "semester")
        course_data = [
            {"course": course, "role": "admin"}
            for course in courses
        ]
    else:
        enrollments = (
            Enrollment.objects
            .filter(user=request.user)
            .select_related("course")
            .order_by("course__code", "course__semester")
        )
        course_data = [
            {"course": enrollment.course, "role": enrollment.role}
            for enrollment in enrollments
        ]

    return render(request, "course_list.html", {"course_data": course_data})

@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()

            Enrollment.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={"role": "instructor"},
            )

            messages.success(request, "Course created successfully.")
            return redirect("course_list")
    else:
        form = CourseForm()

    return render(request, "course_form.html", {"form": form})


@login_required
def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_role(request.user, course, {"instructor"}):
        messages.error(request, "Only instructors can edit this course.")
        return redirect("course_list")

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect("course_list")
    else:
        form = CourseForm(instance=course)

    return render(request, "course_form.html", {"form": form, "course": course})


@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_role(request.user, course, {"instructor"}):
        messages.error(request, "Only instructors can delete this course.")
        return redirect("course_list")

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("course_list")

    return render(request, "confirm_delete.html", {"object": course, "type": "Course"})


@login_required
def course_join(request):
    if request.method == "POST":
        form = JoinCourseForm(request.POST)
        if form.is_valid():
            join_code = form.cleaned_data["join_code"]
            course = Course.objects.filter(join_code=join_code).first()

            if course is None:
                form.add_error("join_code", "No course found with that join code.")
            else:
                enrollment, created = Enrollment.objects.get_or_create(
                    user=request.user,
                    course=course,
                    defaults={"role": "student"},
                )

                if created:
                    messages.success(request, f"You joined {course.code}.")
                else:
                    messages.info(request, f"You are already enrolled in {course.code}.")
                return redirect("course_list")
    else:
        form = JoinCourseForm()

    return render(request, "course_join.html", {"form": form})


@login_required
def course_leave(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if enrollment.role == "instructor":
        other_instructors_exist = Enrollment.objects.filter(
            course=course,
            role="instructor",
        ).exclude(id=enrollment.id).exists()

        if not other_instructors_exist:
            messages.error(request, "A course must have at least one instructor.")
            return redirect("manage_enrollments", course_id=course.id)

    if request.method == "POST":
        enrollment.delete()
        messages.success(request, f"You left {course.code}.")
        return redirect("course_list")

    return render(
        request,
        "confirm_delete.html",
        {"object": enrollment, "type": "Enrollment"},
    )


@login_required
def manage_enrollments(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_role(request.user, course, {"instructor"}):
        messages.error(request, "Only instructors can manage enrollments.")
        return redirect("course_list")

    enrollments = Enrollment.objects.filter(course=course).select_related("user").order_by("role", "user__username")
    return render(
        request,
        "enrollment_manage.html",
        {"course": course, "enrollments": enrollments},
    )


@login_required
def enrollment_role_edit(request, course_id, enrollment_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_role(request.user, course, {"instructor"}):
        messages.error(request, "Only instructors can change roles.")
        return redirect("course_list")

    enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)

    if request.method == "POST":
        form = EnrollmentRoleForm(request.POST, instance=enrollment)
        if form.is_valid():
            new_role = form.cleaned_data["role"]

            if enrollment.user == request.user and enrollment.role == "instructor" and new_role != "instructor":
                other_instructors_exist = Enrollment.objects.filter(
                    course=course,
                    role="instructor",
                ).exclude(id=enrollment.id).exists()

                if not other_instructors_exist:
                    form.add_error("role", "This course must have at least one instructor.")
                else:
                    form.save()
                    messages.success(request, "Enrollment role updated.")
                    return redirect("manage_enrollments", course_id=course.id)
            else:
                form.save()
                messages.success(request, "Enrollment role updated.")
                return redirect("manage_enrollments", course_id=course.id)
    else:
        form = EnrollmentRoleForm(instance=enrollment)

    return render(
        request,
        "enrollment_form.html",
        {"course": course, "enrollment": enrollment, "form": form},
    )


@login_required
def enrollment_delete(request, course_id, enrollment_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_role(request.user, course, {"instructor"}):
        messages.error(request, "Only instructors can remove enrollments.")
        return redirect("course_list")

    enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)

    if enrollment.role == "instructor":
        other_instructors_exist = Enrollment.objects.filter(
            course=course,
            role="instructor",
        ).exclude(id=enrollment.id).exists()

        if not other_instructors_exist:
            messages.error(request, "A course must have at least one instructor.")
            return redirect("manage_enrollments", course_id=course.id)

    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Enrollment removed.")
        return redirect("manage_enrollments", course_id=course.id)

    return render(
        request,
        "confirm_delete.html",
        {"object": enrollment, "type": "Enrollment"},
    )


@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_is_course_member(request.user, course):
        messages.error(request, "You are not enrolled in this course.")
        return redirect("course_list")

    assignments = Assignment.objects.filter(course=course)
    return render(request, "assignment_list.html", {"course": course, "assignments": assignments})


@login_required
def assignment_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_role(request.user, course, {"ta", "instructor"}):
        messages.error(request, "Only TAs and instructors can create assignments.")
        return redirect("assignment_list", course_id=course.id)

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, "Assignment created.")
            return redirect("assignment_list", course_id=course.id)
    else:
        form = AssignmentForm()

    return render(request, "assignment_form.html", {"course": course, "form": form})


@login_required
def assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if not user_has_course_role(request.user, course, {"ta", "instructor"}):
        messages.error(request, "Only TAs and instructors can edit assignments.")
        return redirect("assignment_list", course_id=course.id)

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
            return redirect("assignment_list", course_id=course.id)
    else:
        form = AssignmentForm(instance=assignment)

    return render(
        request,
        "assignment_form.html",
        {"course": course, "assignment": assignment, "form": form},
    )


@login_required
def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if not user_has_course_role(request.user, course, {"ta", "instructor"}):
        messages.error(request, "Only TAs and instructors can delete assignments.")
        return redirect("assignment_list", course_id=course.id)

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("assignment_list", course_id=course.id)

    return render(request, "confirm_delete.html", {"object": assignment, "type": "Assignment"})


@login_required
def task_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if not user_is_course_member(request.user, course):
        messages.error(request, "You are not enrolled in this course.")
        return redirect("course_list")

    tasks = Task.objects.filter(assignment=assignment, assigned_to=request.user)
    return render(request, "task_list.html", {"assignment": assignment, "tasks": tasks})


@login_required
def task_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if not user_is_course_member(request.user, course):
        messages.error(request, "You are not enrolled in this course.")
        return redirect("course_list")

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assignment = assignment
            task.assigned_to = request.user
            task.save()
            messages.success(request, "Task created.")
            return redirect("task_list", assignment_id=assignment.id)
    else:
        form = TaskForm()

    return render(request, "task_form.html", {"assignment": assignment, "form": form})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    notes = Note.objects.filter(task=task)
    return render(request, "task_detail.html", {"task": task, "notes": notes})


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            return redirect("task_detail", task_id=task.id)
    else:
        form = TaskForm(instance=task)

    return render(request, "task_form.html", {"assignment": task.assignment, "task": task, "form": form})


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == "POST":
        assignment_id = task.assignment.id
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("task_list", assignment_id=assignment_id)

    return render(request, "confirm_delete.html", {"object": task, "type": "Task"})


@login_required
def note_create(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.task = task
            note.author = request.user
            note.save()
            messages.success(request, "Note added.")
            return redirect("task_detail", task_id=task.id)
    else:
        form = NoteForm()

    return render(request, "note_form.html", {"task": task, "form": form})


@login_required
def note_edit(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated.")
            return redirect("task_detail", task_id=note.task.id)
    else:
        form = NoteForm(instance=note)

    return render(request, "note_form.html", {"task": note.task, "note": note, "form": form})


@login_required
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    task_id = note.task.id

    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("task_detail", task_id=task_id)

    return render(request, "confirm_delete.html", {"object": note, "type": "Note"})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to StudentFlow!")
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})

