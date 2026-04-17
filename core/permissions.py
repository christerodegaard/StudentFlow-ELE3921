from .models import Enrollment


def user_is_course_member(user, course):
    if user.is_staff or user.is_superuser:
        return True
    return Enrollment.objects.filter(user=user, course=course).exists()


def user_has_course_role(user, course, allowed_roles):
    if user.is_staff or user.is_superuser:
        return True
    return Enrollment.objects.filter(
        user=user,
        course=course,
        role__in=allowed_roles,
    ).exists()