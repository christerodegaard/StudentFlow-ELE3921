from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Course, Enrollment


class CourseModelTest(TestCase):

    def test_course_string_representation(self):
        course = Course.objects.create(
            code="ELE3921",
            title="Web Application Development",
            semester="Spring 2026"
        )
        self.assertIn("ELE3921", str(course))

    def test_join_code_generated_automatically(self):
        course = Course.objects.create(
            code="DAT100",
            title="Intro to Programming",
            semester="Spring 2026"
        )
        self.assertIsNotNone(course.join_code)
        self.assertEqual(len(course.join_code), 8)

    def test_join_code_is_unique(self):
        course1 = Course.objects.create(code="A", title="A", semester="Spring 2026")
        course2 = Course.objects.create(code="B", title="B", semester="Spring 2026")
        self.assertNotEqual(course1.join_code, course2.join_code)


class EnrollmentTest(TestCase):

    def test_student_can_enroll_in_course(self):
        user = User.objects.create_user(username="student1", password="testpassword123")
        course = Course.objects.create(code="DAT200", title="Databases", semester="Spring 2026")
        enrollment = Enrollment.objects.create(user=user, course=course, role="student")
        self.assertEqual(enrollment.role, "student")
        self.assertEqual(enrollment.user.username, "student1")

    def test_is_manager_returns_true_for_ta(self):
        user = User.objects.create_user(username="ta1", password="testpassword123")
        course = Course.objects.create(code="DAT300", title="Advanced DB", semester="Spring 2026")
        enrollment = Enrollment.objects.create(user=user, course=course, role="ta")
        self.assertTrue(enrollment.is_manager())

    def test_is_manager_returns_false_for_student(self):
        user = User.objects.create_user(username="student2", password="testpassword123")
        course = Course.objects.create(code="DAT400", title="ML", semester="Spring 2026")
        enrollment = Enrollment.objects.create(user=user, course=course, role="student")
        self.assertFalse(enrollment.is_manager())


class AuthTest(TestCase):

    def test_login_required_for_dashboard(self):
        client = Client()
        response = client.get(reverse("dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_user_can_access_dashboard(self):
        User.objects.create_user(username="user1", password="testpassword123")
        client = Client()
        client.login(username="user1", password="testpassword123")
        response = client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)