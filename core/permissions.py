from .models import Enrollment


# checks if a user is enrolled in a given course
# admin users (staff/superuser) are always allowed
def user_is_course_member(user, course):
    if user.is_staff or user.is_superuser:
        return True
    return Enrollment.objects.filter(user=user, course=course).exists()


# checks if a user has a specific role in a course (instructor or TA)
# used to restrict actions like editing courses or creating assignments
def user_has_course_role(user, course, allowed_roles):
    if user.is_staff or user.is_superuser:
        return True
    return Enrollment.objects.filter(
        user=user,
        course=course,
        role__in=allowed_roles,
    ).exists()