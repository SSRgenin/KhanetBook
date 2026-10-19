from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import UserProfile
from books.models import Category, Book
from orders.models import Order, OrderItem
from books.forms import BookForm

class EbookStoreTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Seller User
        self.seller_user = User.objects.create_user(
            username='testseller',
            email='testseller@example.com',
            password='password123'
        )
        self.seller_profile = self.seller_user.profile
        self.seller_profile.role = UserProfile.ROLE_SELLER
        self.seller_profile.save()

        # Create Customer User
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            email='testcustomer@example.com',
            password='password123'
        )
        self.customer_profile = self.customer_user.profile
        self.customer_profile.role = UserProfile.ROLE_CUSTOMER
        self.customer_profile.save()

        # Create Category
        self.category = Category.objects.create(
            name='คอมพิวเตอร์',
            slug='computer',
            description='หมวดคอมพิวเตอร์'
        )

        # Create Sample PDF
        self.sample_pdf = SimpleUploadedFile(
            "test_book.pdf",
            b"%PDF-1.4 sample content",
            content_type="application/pdf"
        )

        # Create Book
        self.book = Book.objects.create(
            seller=self.seller_user,
            category=self.category,
            title='Django Guide',
            author='Author Test',
            price=199.00,
            pages=200,
            description='Django learning guide',
            pdf_file=self.sample_pdf
        )

    def test_book_list_and_search(self):
        """Test public catalog view and search functionality"""
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Guide')

        # Test Search by title
        search_res = self.client.get(reverse('book_list') + '?q=Django')
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, 'Django Guide')

        # Test Search with non-existing term
        search_none = self.client.get(reverse('book_list') + '?q=NonExistentBookXYZ')
        self.assertEqual(search_none.status_code, 200)
        self.assertContains(search_none, 'ไม่พบหนังสือ')

    def test_rbac_access_control(self):
        """Test that Customers cannot access Seller pages (Create Book), but Sellers can"""
        # Customer attempts to access book create
        self.client.login(username='testcustomer', password='password123')
        cust_response = self.client.get(reverse('book_create'))
        # Should redirect with permission error message
        self.assertEqual(cust_response.status_code, 302)

        # Seller accesses book create
        self.client.login(username='testseller', password='password123')
        seller_response = self.client.get(reverse('book_create'))
        self.assertEqual(seller_response.status_code, 200)

    def test_form_validation_negative_price(self):
        """Test form validation: negative price is rejected"""
        form_data = {
            'title': 'Bad Price Book',
            'author': 'Author',
            'category': self.category.id,
            'price': -50.00,  # Invalid negative price!
            'pages': 100,
            'description': 'Valid desc'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_cart_and_checkout_flow(self):
        """Test adding book to cart, viewing cart, and completing checkout"""
        self.client.login(username='testcustomer', password='password123')

        # Add to cart
        add_res = self.client.get(reverse('add_to_cart', kwargs={'pk': self.book.pk}))
        self.assertEqual(add_res.status_code, 302)

        # View cart
        cart_res = self.client.get(reverse('cart'))
        self.assertEqual(cart_res.status_code, 200)
        self.assertContains(cart_res, 'Django Guide')

        # Checkout POST
        checkout_res = self.client.post(reverse('checkout'), {
            'payment_method': 'PromptPay QR Code'
        })
        self.assertEqual(checkout_res.status_code, 302)

        # Verify Order and OrderItem in DB
        order = Order.objects.filter(user=self.customer_user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, Order.STATUS_COMPLETED)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().book, self.book)

        # Verify book appears in My Library
        lib_res = self.client.get(reverse('my_library'))
        self.assertEqual(lib_res.status_code, 200)
        self.assertContains(lib_res, 'Django Guide')
