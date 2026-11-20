from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class LoginFlowTests(TestCase):
    def setUp(self):
        self.username = 'student'
        self.password = 'SafeTestPassword123!'
        get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=True
        )

    def test_home_page_matches_requested_design(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
        self.assertContains(response, "<h1>Girly's Home Page</h1>")
        self.assertContains(
            response,
            'Welcome to my first Django application!'
        )
        self.assertContains(response, 'Staff Login')
        self.assertContains(response, 'Back to Landing Page')
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('landing'))

    def test_login_page_uses_project_template(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_valid_credentials_authenticate_and_redirect_to_staff_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': self.password},
            follow=True
        )

        self.assertRedirects(response, reverse('staff_dashboard'))
        self.assertTemplateUsed(response, 'registration/dashboard.html')
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, self.username)
        self.assertContains(response, reverse('student_list'))
        self.assertContains(response, reverse('logout'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_logout_uses_post_and_clears_authenticated_session(self):
        self.client.force_login(get_user_model().objects.get(
            username=self.username
        ))

        get_response = self.client.get(reverse('logout'))
        self.assertEqual(get_response.status_code, 405)
        self.assertTrue(get_response.wsgi_request.user.is_authenticated)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_invalid_credentials_show_a_generic_error(self):
        wrong_password_response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': 'wrong-password'}
        )
        unknown_user_response = self.client.post(
            reverse('login'),
            {'username': 'unknown-user', 'password': 'wrong-password'}
        )

        self.assertEqual(wrong_password_response.status_code, 200)
        self.assertFalse(
            wrong_password_response.wsgi_request.user.is_authenticated
        )
        self.assertEqual(unknown_user_response.status_code, 200)
        self.assertFalse(
            unknown_user_response.wsgi_request.user.is_authenticated
        )

        password_error = (
            wrong_password_response.context['form'].non_field_errors()
        )
        unknown_user_error = (
            unknown_user_response.context['form'].non_field_errors()
        )
        self.assertEqual(password_error, unknown_user_error)
        self.assertNotIn(self.username, str(password_error))
        self.assertContains(
            wrong_password_response,
            'Please enter a correct username and password.'
        )
        self.assertContains(
            unknown_user_response,
            'Please enter a correct username and password.'
        )
