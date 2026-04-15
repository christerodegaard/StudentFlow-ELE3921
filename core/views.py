from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignmentForm, CourseForm, NoteForm, TaskForm
from .models import Assignment, Course, Enrollment, Note, Task


@login_required
def dashboard(request):
    courses = Course.objects.filter(enrollment__user=request.user)
    tasks = Task.objects.filter(assigned_to=request.user)

    selected_course = request.GET.get("course")
    selected_status = request.GET.get("status")

    if selected_course:
        tasks = tasks.filter(assignment__course_id=selected_course)

    if selected_status:
        tasks = tasks.filter(status=selected_status)

    context = {
        "tasks": tasks,
        "courses": courses,
        "selected_course": selected_course,
        "selected_status": selected_status,
    }

    return render(request, "dashboard.html", context)


@login_required
def course_list(request):
    courses = Course.objects.filter(enrollment__user=request.user)
    return render(request, "course_list.html", {"courses": courses})


@login_required
def course_create(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to create courses.")
        return redirect("course_list")

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

    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this course.")
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

    if not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this course.")
        return redirect("course_list")

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("course_list")

    return render(request, "confirm_delete.html", {"object": course, "type": "Course"})


@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request, "assignment_list.html", {"course": course, "assignments": assignments})


@login_required
def assignment_create(request, course_id):
    course = get_object_or_404(Course, id=course_id)

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

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
            return redirect("assignment_list", course_id=course.id)
    else:
        form = AssignmentForm(instance=assignment)

    return render(request, "assignment_form.html", {"course": course, "form": form})


@login_required
def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course_id = assignment.course.id

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("assignment_list", course_id=course_id)

    return render(request, "confirm_delete.html", {"object": assignment, "type": "Assignment"})


@login_required
def task_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    tasks = Task.objects.filter(assignment=assignment, assigned_to=request.user)
    return render(request, "task_list.html", {"assignment": assignment, "tasks": tasks})


@login_required
def task_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

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