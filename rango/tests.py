from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse

class RangoViewTests(TestCase):
    def test_index_view_exists(self):
        """ Check whether the `index` view exists and return the correct HTTP response. """
        response = self.client.get(reverse('rango:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rango says hey there partner!")

    def test_about_view_exists(self):
        """ Check whether the `about` view exists and return the correct HTTP response. """
        response = self.client.get(reverse('rango:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rango says here is the about page.")

    def test_index_has_about_link(self):
        """ Does the `index` page contain a hyperlink that leads to the `about` page? """
        response = self.client.get(reverse('rango:index'))
        self.assertContains(response, '<a href="/rango/about/">About</a>', html=True)

    def test_about_has_index_link(self):
        """ Does the "about" page contain a hyperlink to return to the "index" page? """
        response = self.client.get(reverse('rango:about'))
        self.assertContains(response, '<a href="/rango/">Index</a>', html=True)
