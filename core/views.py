from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignmentForm, CourseForm, NoteForm, TaskForm
from .models import Assignment, Course, Enrollment, Note, Task


def get_user_courses(user):
    # Staff users can see all courses
    if user.is_staff:
        return Course.objects.all().order_by("code")

    # Regular users only see courses they are enrolled in
    return Course.objects.filter(enrollment__user=user).distinct().order_by("code")


def user_has_course_access(user, course):
    # Staff users can access all courses
    if user.is_staff:
        return True

    return Enrollment.objects.filter(user=user, course=course).exists()


@login_required
def dashboard(request):
    today = date.today()
    upcoming_limit = today + timedelta(days=7)

    # Only show tasks assigned to the logged-in user
    tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related("assignment", "assignment__course")

    # Limit course filter choices to enrolled courses
    courses = get_user_courses(request.user)

    selected_course = request.GET.get("course")
    selected_status = request.GET.get("status")
    selected_due = request.GET.get("due")

    if selected_course:
        tasks = tasks.filter(assignment__course_id=selected_course)

    if selected_status:
        tasks = tasks.filter(status=selected_status)

    if selected_due == "overdue":
        tasks = tasks.filter(due_date__lt=today)
    elif selected_due == "soon":
        tasks = tasks.filter(due_date__range=(today, upcoming_limit))
    elif selected_due == "today":
        tasks = tasks.filter(due_date=today)

    overdue = tasks.filter(due_date__lt=today, status__in=["todo", "doing"])
    due_soon = tasks.filter(
        due_date__range=(today, upcoming_limit),
        status__in=["todo", "doing"],
    )
    completed = tasks.filter(status="done")
    todo = tasks.filter(status="todo")
    doing = tasks.filter(status="doing")

    context = {
        "overdue": overdue,
        "due_soon": due_soon,
        "completed": completed,
        "todo": todo,
        "doing": doing,
        "courses": courses,
        "selected_course": selected_course,
        "selected_status": selected_status,
        "selected_due": selected_due,
    }

    return render(request, "dashboard.html", context)


@login_required
def course_list(request):
    # Only show courses the user is enrolled in
    courses = get_user_courses(request.user)
    return render(request, "course_list.html", {"courses": courses})


@login_required
def course_create(request):
    # Keep course creation restricted to staff/admin
    if not request.user.is_staff:
        raise Http404("You do not have permission to create courses.")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully.")
            return redirect("course_list")
    else:
        form = CourseForm()

    return render(request, "course_form.html", {"form": form})


@login_required
def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_access(request.user, course) or not request.user.is_staff:
        raise Http404("You do not have permission to edit this course.")

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect("course_list")
    else:
        form = CourseForm(instance=course)

    return render(request, "course_form.html", {"form": form, "course": course})


@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not user_has_course_access(request.user, course) or not request.user.is_staff:
        raise Http404("You do not have permission to delete this course.")

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect("course_list")

    return render(request, "confirm_delete.html", {"object": course, "type": "Course"})


@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # User must be enrolled in this course
    if not user_has_course_access(request.user, course):
        raise Http404("You do not have access to this course.")

    assignments = Assignment.objects.filter(course=course).order_by("due_date", "title")

    return render(
        request,
        "assignment_list.html",
        {"course": course, "assignments": assignments},
    )


@login_required
def assignment_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Restrict assignment management to staff/admin for now
    if not user_has_course_access(request.user, course) or not request.user.is_staff:
        raise Http404("You do not have permission to create assignments for this course.")

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, "Assignment created successfully.")
            return redirect("assignment_list", course_id=course.id)
    else:
        form = AssignmentForm()

    return render(request, "assignment_form.html", {"course": course, "form": form})


@login_required
def assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if not user_has_course_access(request.user, course) or not request.user.is_staff:
        raise Http404("You do not have permission to edit this assignment.")

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully.")
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
    course_id = assignment.course.id

    if not user_has_course_access(request.user, assignment.course) or not request.user.is_staff:
        raise Http404("You do not have permission to delete this assignment.")

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully.")
        return redirect("assignment_list", course_id=course_id)

    return render(
        request,
        "confirm_delete.html",
        {"object": assignment, "type": "Assignment"},
    )


@login_required
def task_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if not user_has_course_access(request.user, assignment.course):
        raise Http404("You do not have access to this assignment.")

    # Users only see their own tasks
    tasks = Task.objects.filter(
        assignment=assignment,
        assigned_to=request.user,
    ).order_by("due_date", "-priority", "title")

    return render(request, "task_list.html", {"assignment": assignment, "tasks": tasks})


@login_required
def task_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if not user_has_course_access(request.user, assignment.course):
        raise Http404("You do not have access to this assignment.")

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assignment = assignment
            task.assigned_to = request.user
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect("task_list", assignment_id=assignment.id)
    else:
        form = TaskForm()

    return render(request, "task_form.html", {"assignment": assignment, "form": form})


@login_required
def task_detail(request, task_id):
    # Users can only open their own task detail page
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    notes = Note.objects.filter(task=task).order_by("-created_at")
    return render(request, "task_detail.html", {"task": task, "notes": notes})


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if not user_has_course_access(request.user, task.assignment.course):
        raise Http404("You do not have access to this task.")

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect("task_detail", task_id=task.id)
    else:
        form = TaskForm(instance=task)

    return render(
        request,
        "task_form.html",
        {"assignment": task.assignment, "task": task, "form": form},
    )


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if not user_has_course_access(request.user, task.assignment.course):
        raise Http404("You do not have access to this task.")

    if request.method == "POST":
        assignment_id = task.assignment.id
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect("task_list", assignment_id=assignment_id)

    return render(request, "confirm_delete.html", {"object": task, "type": "Task"})


@login_required
def note_create(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

    if not user_has_course_access(request.user, task.assignment.course):
        raise Http404("You do not have access to this task.")

    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.task = task
            note.author = request.user
            note.save()
            messages.success(request, "Note added successfully.")
            return redirect("task_detail", task_id=task.id)
    else:
        form = NoteForm()

    return render(request, "note_form.html", {"task": task, "form": form})


@login_required
def note_edit(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    task = note.task

    if not user_has_course_access(request.user, task.assignment.course):
        raise Http404("You do not have access to this note.")

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully.")
            return redirect("task_detail", task_id=task.id)
    else:
        form = NoteForm(instance=note)

    return render(request, "note_form.html", {"task": task, "note": note, "form": form})


@login_required
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    task_id = note.task.id

    if not user_has_course_access(request.user, note.task.assignment.course):
        raise Http404("You do not have access to this note.")

    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted successfully.")
        return redirect("task_detail", task_id=task_id)

    return render(request, "confirm_delete.html", {"object": note, "type": "Note"})


def register(request):
    # Simple signup using Django's built-in user form
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to StudentFlow!")
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})