from django.test import TestCase
from django.urls import reverse
from .models import Student


class StudentRegistrationWorkflowTests(TestCase):
    student_data = {
        'student_id': 'STU001',
        'first_name': 'Alex',
        'last_name': 'Rivera',
        'gender': 'Female',
        'date_of_birth': '2002-04-15',
        'contact_no': '5551234567',
    }

    def test_module_06_and_student_directory_routes(self):
        student = Student.objects.create(**self.student_data)

        self.assertEqual(reverse('student_registration'), '/registration/')
        self.assertEqual(
            reverse('registration_success'),
            '/registration/success/'
        )
        self.assertEqual(
            reverse('student_registration_legacy'),
            '/registration/register/'
        )
        self.assertEqual(reverse('student_list'), '/registration/students/')
        self.assertEqual(
            reverse('student_create'),
            '/registration/students/create/'
        )
        self.assertEqual(
            reverse('student_detail', args=[student.pk]),
            f'/registration/students/{student.pk}/'
        )
        self.assertEqual(
            reverse('student_update', args=[student.pk]),
            f'/registration/students/{student.pk}/edit/'
        )
        self.assertEqual(
            reverse('student_delete', args=[student.pk]),
            f'/registration/students/{student.pk}/delete/'
        )

    def test_original_registration_route_remains_available(self):
        response = self.client.post(
            reverse('student_registration'),
            self.student_data
        )

        self.assertRedirects(response, reverse('registration_success'))
        self.assertTrue(Student.objects.filter(student_id='STU001').exists())

    def test_model_form_create_saves_and_shows_success_message(self):
        response = self.client.post(
            reverse('student_create'),
            self.student_data,
            follow=True
        )

        self.assertRedirects(response, reverse('student_list'))
        self.assertTrue(Student.objects.filter(student_id='STU001').exists())
        self.assertContains(response, 'Student record created successfully.')

    def test_model_form_update_saves_and_shows_success_message(self):
        student = Student.objects.create(**self.student_data)
        updated_data = dict(self.student_data, first_name='Jordan')

        response = self.client.post(
            reverse('student_update', args=[student.pk]),
            updated_data,
            follow=True
        )

        student.refresh_from_db()
        self.assertEqual(student.first_name, 'Jordan')
        self.assertRedirects(response, reverse('student_list'))
        self.assertContains(response, 'Student record updated successfully.')

    def test_create_and_update_use_shared_student_form_template(self):
        create_response = self.client.get(reverse('student_create'))
        student = Student.objects.create(**self.student_data)
        update_response = self.client.get(
            reverse('student_update', args=[student.pk])
        )

        self.assertTemplateUsed(
            create_response,
            'registration/student_form.html'
        )
        self.assertContains(create_response, '<title>Register Student</title>')
        self.assertTemplateUsed(
            update_response,
            'registration/student_form.html'
        )
        self.assertContains(update_response, '<title>Update Student</title>')

    def test_delete_requires_post_and_shows_success_message(self):
        student = Student.objects.create(**self.student_data)
        delete_url = reverse('student_delete', args=[student.pk])

        confirmation_response = self.client.get(delete_url)
        self.assertEqual(confirmation_response.status_code, 200)
        self.assertTemplateUsed(
            confirmation_response,
            'registration/student_confirm_delete.html'
        )
        self.assertContains(confirmation_response, 'csrfmiddlewaretoken')
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())

        response = self.client.post(delete_url, follow=True)

        self.assertRedirects(response, reverse('student_list'))
        self.assertFalse(Student.objects.filter(pk=student.pk).exists())
        self.assertContains(response, 'Student record deleted successfully.')

    def test_student_directory_hides_registration_shortcuts(self):
        response = self.client.get(reverse('student_list'))

        self.assertNotContains(response, 'Create Student with ModelForm')
        self.assertNotContains(response, 'Use Original Registration')
