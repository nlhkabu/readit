from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
from books.factories import AuthorFactory, BookFactory, ReviewFactory, UserFactory
from books.models import Book
from books.views import list_books, ReviewList


class TestListBooks(TestCase):
	def test_list_books_url(self):
		url = resolve('/')
		self.assertEqual(url.func, list_books)
		
	def test_list_books_template(self):
		response = self.client.get(reverse(list_books))
		self.assertTemplateUsed(response, 'list.html')
		
	def test_list_books_returns_books_with_reviews(self):
		# Setup our data
		author = AuthorFactory()
		books_with_reviews = ReviewFactory.create_batch(2, authors=[author,])
		books_without_reviews = BookFactory.create_batch(4, authors=[author,])
		
		response = self.client.get(reverse(list_books))
		books = list(response.context['books'])
		
		self.assertEqual(books_with_reviews, books)
		self.assertNotEqual(books_without_reviews, books)
		

class TestReviewList(TestCase):
	def setUp(self):
		self.user = UserFactory(username="test")
		self.author = AuthorFactory()
	
	def test_reviews_url(self):
		url = resolve('/review/')
		self.assertEqual(url.func.__name__, ReviewList.__name__)
	
	def test_authentication_control(self):
		# Check unauthenticated users cannot view page
		response = self.client.get(reverse('review-books'))
		self.assertEqual(response.status_code, 302)
		
		self.client.login(username="test", password="test")
		response = self.client.get(reverse('review-books'))
		self.assertEqual(response.status_code, 200)
		
		# While we're here, confirm we're using correct template
		self.assertTemplateUsed(response, 'list-to-review.html')
		
	def test_review_list_returns_books_to_review(self):
		# Setup our data
		books_without_reviews = BookFactory.create_batch(2, authors=[self.author,])
		
		self.client.login(username="test", password="test")
		response = self.client.get(reverse('review-books'))
		
		books = list(response.context['books'])
		self.assertEqual(books, books_without_reviews)
		
	def test_can_create_new_book(self):
		self.client.login(username="test", password="test")
		response = self.client.post(
			reverse('review-books'),
			data={
				'title': 'My Brand New Book',
				'authors': [self.author.pk,],
				'reviewed_by': self.user.pk,
			},
		)
		
		self.assertIsNotNone(Book.objects.get(title="My Brand New Book"))
		
	
