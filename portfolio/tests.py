from django.test import TestCase
from django.urls import reverse
from .models import BlogPost


class PortfolioPageTests(TestCase):
    fixtures = []

    def test_home_page_loads(self):
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)

    def test_blog_list_loads(self):
        response = self.client.get(reverse('portfolio:blog_list'))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_loads_for_published_post(self):
        post = BlogPost.objects.create(
            title='Testing backend pages',
            slug='testing-backend-pages',
            excerpt='Short excerpt',
            body='Body',
            status=BlogPost.PUBLISHED,
        )

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.title)
