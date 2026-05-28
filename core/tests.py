from django.test import TestCase
from django.contrib.auth.models import User

from .models import Course, Enrollment


class CourseModelTest(TestCase):

    def test_course_string_representation(self):
        course = Course.objects.create(
            code="ELE3921",
            title="Web Application Development",
            semester="Spring 2026"
        )

        self.assertIn("ELE3921", str(course))


class EnrollmentTest(TestCase):

    def test_student_can_enroll_in_course(self):
        user = User.objects.create_user(
            username="student1",
            password="testpassword123"
        )

        course = Course.objects.create(
            code="DAT200",
            title="Databases",
            semester="Spring 2026"
        )

        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            role="student"
        )

        self.assertEqual(enrollment.role, "student")
        self.assertEqual(enrollment.user.username, "student1")