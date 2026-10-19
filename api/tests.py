import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import UserProfile
from books.models import Book, Category
from orders.models import Order, OrderItem

class ApiEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Seller User
        self.seller = User.objects.create_user(
            username='apiseller',
            email='apiseller@example.com',
            password='password123'
        )
        self.seller.profile.role = UserProfile.ROLE_SELLER
        self.seller.profile.save()

        # Create Customer User
        self.customer = User.objects.create_user(
            username='apicustomer',
            email='apicustomer@example.com',
            password='password123'
        )
        self.customer.profile.role = UserProfile.ROLE_CUSTOMER
        self.customer.profile.save()

        # Create Category
        self.cat = Category.objects.create(
            name='นิยายสืบสวน',
            slug='mystery',
            description='หมวดสืบสวนสอบสวน'
        )

        # Create Book
        sample_pdf = SimpleUploadedFile("sample.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        self.book = Book.objects.create(
            seller=self.seller,
            category=self.cat,
            title='เชอร์ล็อก โฮล์มส์ ตอนพิเศษ',
            author='Arthur Conan Doyle',
            price=180.00,
            pages=220,
            description='เรื่องราวการไขคดีปริศนา',
            pdf_file=sample_pdf
        )

    def test_api_docs_html_and_json(self):
        """Test API documentation endpoint in both HTML and JSON formats"""
        # HTML
        res_html = self.client.get(reverse('api_docs'))
        self.assertEqual(res_html.status_code, 200)
        self.assertContains(res_html, 'KhanetBook Web API Documentation')

        # JSON
        res_json = self.client.get(reverse('api_docs') + '?format=json')
        self.assertEqual(res_json.status_code, 200)
        data = json.loads(res_json.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('endpoints', data)

    def test_books_api_list_and_search(self):
        """Test /api/books/ listing, pagination and search"""
        res = self.client.get(reverse('api_book_list'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_books'], 1)
        self.assertEqual(data['books'][0]['title'], 'เชอร์ล็อก โฮล์มส์ ตอนพิเศษ')

        # Test search
        res_search = self.client.get(reverse('api_book_list') + '?q=เชอร์ล็อก')
        self.assertEqual(res_search.status_code, 200)
        search_data = json.loads(res_search.content)
        self.assertEqual(search_data['total_books'], 1)

        # Test search non-existent
        res_none = self.client.get(reverse('api_book_list') + '?q=ไม่มีหนังสือนี้แน่นอน')
        self.assertEqual(res_none.status_code, 200)
        none_data = json.loads(res_none.content)
        self.assertEqual(none_data['total_books'], 0)

    def test_book_detail_api(self):
        """Test /api/books/<id>/ retrieve book detail"""
        res = self.client.get(reverse('api_book_detail', kwargs={'pk': self.book.pk}))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['book']['id'], self.book.pk)
        self.assertEqual(data['book']['title'], self.book.title)

        # Test 404 for non-existent book
        res_404 = self.client.get(reverse('api_book_detail', kwargs={'pk': 9999}))
        self.assertEqual(res_404.status_code, 404)

    def test_category_api(self):
        """Test /api/categories/ list"""
        res = self.client.get(reverse('api_category_list'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['slug'], 'mystery')

    def test_cart_api_operations(self):
        """Test /api/cart/ and add/remove operations"""
        # Initially empty cart
        res_cart = self.client.get(reverse('api_cart'))
        self.assertEqual(res_cart.status_code, 200)
        data = json.loads(res_cart.content)
        self.assertEqual(data['cart_count'], 0)

        # Add to cart via API
        res_add = self.client.get(reverse('api_cart_add', kwargs={'pk': self.book.pk}))
        self.assertEqual(res_add.status_code, 200)
        add_data = json.loads(res_add.content)
        self.assertEqual(add_data['cart_count'], 1)
        self.assertEqual(add_data['total_price'], 180.00)

        # Remove from cart via API
        res_rm = self.client.get(reverse('api_cart_remove', kwargs={'pk': self.book.pk}))
        self.assertEqual(res_rm.status_code, 200)
        rm_data = json.loads(res_rm.content)
        self.assertEqual(rm_data['cart_count'], 0)

    def test_seller_dashboard_api_security(self):
        """Test role-based security on /api/seller/dashboard/"""
        # 1. Unauthenticated -> 401
        res_anon = self.client.get(reverse('api_seller_dashboard'))
        self.assertEqual(res_anon.status_code, 401)

        # 2. Customer -> 403
        self.client.login(username='apicustomer', password='password123')
        res_cust = self.client.get(reverse('api_seller_dashboard'))
        self.assertEqual(res_cust.status_code, 403)

        # 3. Seller -> 200
        self.client.login(username='apiseller', password='password123')
        res_seller = self.client.get(reverse('api_seller_dashboard'))
        self.assertEqual(res_seller.status_code, 200)
        seller_data = json.loads(res_seller.content)
        self.assertEqual(seller_data['status'], 'success')
        self.assertEqual(seller_data['seller'], 'apiseller')

    def test_health_api(self):
        """Test system health check endpoint"""
        res = self.client.get(reverse('api_health'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['system'], 'KhanetBook E-Book Store')
