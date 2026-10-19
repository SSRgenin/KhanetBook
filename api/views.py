import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.contrib.auth.models import User
from books.models import Book, Category
from orders.models import Order, OrderItem

def serialize_book(book, request=None):
    """Helper to convert Book instance into clean JSON-serializable dict."""
    cover_url = ""
    sample_url = ""
    if book.cover_image:
        cover_url = request.build_absolute_uri(book.cover_image.url) if request else book.cover_image.url
    if book.sample_file:
        sample_url = request.build_absolute_uri(book.sample_file.url) if request else book.sample_file.url

    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "price": float(book.price),
        "description": book.description,
        "pages": book.pages,
        "isbn": book.isbn or "",
        "category": book.category.name if book.category else None,
        "category_slug": book.category.slug if book.category else None,
        "cover_url": cover_url,
        "sample_url": sample_url,
        "seller": book.seller.username,
        "is_active": book.is_active,
        "created_at": book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }


def api_docs(request):
    """
    API Documentation endpoint.
    If requested via browser, renders an interactive HTML documentation page.
    If requested with Accept: application/json or ?format=json, returns JSON schema.
    """
    endpoints = [
        {
            "path": "/api/books/",
            "method": "GET",
            "description": "เรียกดูรายการหนังสือ E-Book ทั้งหมด พร้อมระบบค้นหา, กรองหมวดหมู่ และแบ่งหน้า (Pagination)",
            "params": [
                {"name": "q", "type": "string", "description": "คำค้นหา (ชื่อหนังสือ, ผู้แต่ง, คำอธิบาย, ISBN)"},
                {"name": "category", "type": "string", "description": "slug ของหมวดหมู่ เช่น light-novel, general-manga"},
                {"name": "sort", "type": "string", "description": "ตัวเลือกการเรียงลำดับ: newest (ใหม่สุด), price_asc (ราคาต่ำ-สูง), price_desc (ราคาสูง-ต่ำ)"},
                {"name": "page", "type": "integer", "description": "เลขหน้า (ค่าเริ่มต้น: 1)"},
                {"name": "page_size", "type": "integer", "description": "จำนวนรายการต่อหน้า (ค่าเริ่มต้น: 6, สูงสุด: 50)"}
            ],
            "sample_url": "/api/books/?q=&sort=newest&page=1"
        },
        {
            "path": "/api/books/<int:id>/",
            "method": "GET",
            "description": "เรียกดูข้อมูลรายละเอียดของหนังสือ E-Book เล่มที่ระบุตาม ID",
            "params": [
                {"name": "id", "type": "integer", "description": "รหัส ID ของหนังสือ"}
            ],
            "sample_url": "/api/books/11/"
        },
        {
            "path": "/api/categories/",
            "method": "GET",
            "description": "เรียกดูรายการหมวดหมู่หนังสือทั้งหมด พร้อมจำนวนหนังสือในแต่ละหมวด",
            "params": [],
            "sample_url": "/api/categories/"
        },
        {
            "path": "/api/cart/",
            "method": "GET",
            "description": "เรียกดูรายการสินค้าที่อยู่ในตะกร้าปัจจุบัน (Session Cart) พร้อมสรุปจำนวนและราคารวม",
            "params": [],
            "sample_url": "/api/cart/"
        },
        {
            "path": "/api/cart/add/<int:id>/",
            "method": "GET / POST",
            "description": "เพิ่มหนังสือลงในตะกร้าสินค้าผ่าน API ตอบกลับสถานะและจำนวนสินค้าล่าสุด",
            "params": [
                {"name": "id", "type": "integer", "description": "รหัส ID ของหนังสือที่จะเพิ่มลงตะกร้า"}
            ],
            "sample_url": "/api/cart/add/11/"
        },
        {
            "path": "/api/cart/remove/<int:id>/",
            "method": "GET / POST",
            "description": "นำหนังสือออกจากตะกร้าสินค้า",
            "params": [
                {"name": "id", "type": "integer", "description": "รหัส ID ของหนังสือที่จะนำออก"}
            ],
            "sample_url": "/api/cart/remove/11/"
        },
        {
            "path": "/api/seller/dashboard/",
            "method": "GET",
            "description": "ข้อมูลสถิติสำหรับผู้ขาย (Seller / Admin) สรุปยอดขายรวม, จำนวนเล่มที่ขายได้, รายได้แยกตามหมวดหมู่ (ต้องล็อกอินสิทธิ์ผู้ขาย)",
            "params": [],
            "sample_url": "/api/seller/dashboard/"
        },
        {
            "path": "/api/health/",
            "method": "GET",
            "description": "ตรวจสอบสถานะความพร้อมของระบบและฐานข้อมูล (System Health Check)",
            "params": [],
            "sample_url": "/api/health/"
        }
    ]

    if request.GET.get('format') == 'json' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            "status": "success",
            "title": "KhanetBook RESTful JSON API",
            "version": "1.0",
            "base_url": request.build_absolute_uri('/api/'),
            "endpoints": endpoints
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    return render(request, 'api/docs.html', {
        'endpoints': endpoints,
        'title': 'KhanetBook API Documentation'
    })


def book_list_api(request):
    """
    GET /api/books/
    List books with search, filter, and pagination.
    """
    books = Book.objects.filter(is_active=True).select_related('category', 'seller')

    # 1. Search Query
    query = request.GET.get('q', '').strip()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(isbn__icontains=query)
        )

    # 2. Category Filter
    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if category:
            books = books.filter(category=category)
        else:
            return JsonResponse({
                "status": "error",
                "message": f"Category with slug '{category_slug}' not found"
            }, status=404)

    # 3. Sorting
    sort_option = request.GET.get('sort', 'newest')
    if sort_option == 'price_asc':
        books = books.order_by('price')
    elif sort_option == 'price_desc':
        books = books.order_by('-price')
    elif sort_option == 'title_asc':
        books = books.order_by('title')
    else:
        books = books.order_by('-created_at')

    # 4. Pagination
    total_count = books.count()
    try:
        page_size = int(request.GET.get('page_size', 6))
        page_size = max(1, min(page_size, 50))  # Between 1 and 50
    except (ValueError, TypeError):
        page_size = 6

    paginator = Paginator(books, page_size)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    data = [serialize_book(b, request) for b in page_obj]

    return JsonResponse({
        "status": "success",
        "total_books": total_count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "page_size": page_size,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "books": data
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def book_detail_api(request, pk):
    """
    GET /api/books/<int:pk>/
    Retrieve single book details.
    """
    book = Book.objects.filter(pk=pk, is_active=True).select_related('category', 'seller').first()
    if not book:
        return JsonResponse({
            "status": "error",
            "message": f"Book with id {pk} not found"
        }, status=404)

    return JsonResponse({
        "status": "success",
        "book": serialize_book(book, request)
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def category_list_api(request):
    """
    GET /api/categories/
    List all categories with book counts.
    """
    categories = Category.objects.annotate(book_count=Count('books')).order_by('name')
    data = []
    for c in categories:
        data.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "book_count": c.book_count
        })

    return JsonResponse({
        "status": "success",
        "total_categories": len(data),
        "categories": data
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def cart_api(request):
    """
    GET /api/cart/
    Retrieve cart items and total amount.
    """
    cart_ids = request.session.get('cart', [])
    books = Book.objects.filter(id__in=cart_ids, is_active=True)
    items = [serialize_book(b, request) for b in books]
    total_price = sum(b.price for b in books)

    return JsonResponse({
        "status": "success",
        "cart_count": len(cart_ids),
        "total_price": float(total_price),
        "items": items
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def cart_add_api(request, pk):
    """
    GET / POST /api/cart/add/<int:pk>/
    Add item to cart via API.
    """
    book = Book.objects.filter(pk=pk, is_active=True).first()
    if not book:
        return JsonResponse({
            "status": "error",
            "message": f"Book with id {pk} not found"
        }, status=404)

    cart = request.session.get('cart', [])
    already_in_cart = book.pk in cart

    if not already_in_cart:
        # Check if already purchased
        if request.user.is_authenticated:
            if OrderItem.objects.filter(order__user=request.user, order__status='completed', book=book).exists():
                return JsonResponse({
                    "status": "already_purchased",
                    "message": f"คุณมีหนังสือ '{book.title}' ในคลังหนังสือเรียบร้อยแล้ว",
                    "cart_count": len(cart)
                })

        cart.append(book.pk)
        request.session['cart'] = cart
        request.session.modified = True
        msg = f"เพิ่ม '{book.title}' ลงตะกร้าเรียบร้อยแล้ว"
    else:
        msg = f"'{book.title}' มีอยู่ในตะกร้าสินค้าแล้ว"

    # Calculate total
    cart_books = Book.objects.filter(id__in=cart)
    total_price = float(sum(b.price for b in cart_books))

    return JsonResponse({
        "status": "success",
        "message": msg,
        "already_in_cart": already_in_cart,
        "cart_count": len(cart),
        "total_price": total_price
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def cart_remove_api(request, pk):
    """
    GET / POST /api/cart/remove/<int:pk>/
    Remove item from cart via API.
    """
    cart = request.session.get('cart', [])
    if pk in cart:
        cart.remove(pk)
        request.session['cart'] = cart
        request.session.modified = True
        removed = True
        msg = "นำหนังสือออกจากตะกร้าเรียบร้อยแล้ว"
    else:
        removed = False
        msg = "ไม่พบหนังสือรายการนี้ในตะกร้า"

    cart_books = Book.objects.filter(id__in=cart)
    total_price = float(sum(b.price for b in cart_books))

    return JsonResponse({
        "status": "success" if removed else "not_found",
        "message": msg,
        "cart_count": len(cart),
        "total_price": total_price
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def seller_stats_api(request):
    """
    GET /api/seller/dashboard/
    Protected API for Seller / Admin dashboard metrics.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": "error",
            "message": "Authentication required. Please login first."
        }, status=401)

    profile = getattr(request.user, 'profile', None)
    is_seller = request.user.is_superuser or (profile and profile.is_seller())

    if not is_seller:
        return JsonResponse({
            "status": "error",
            "message": "Permission denied. Seller role required."
        }, status=403)

    if request.user.is_superuser:
        books = Book.objects.all().select_related('category', 'seller')
    else:
        books = Book.objects.filter(seller=request.user).select_related('category')

    total_sales_count = OrderItem.objects.filter(book__in=books, order__status='completed').count()
    revenue_agg = OrderItem.objects.filter(book__in=books, order__status='completed').aggregate(Sum('price'))
    total_revenue = float(revenue_agg['price__sum'] or 0.0)

    # Breakdown by category
    category_stats = []
    cats = Category.objects.filter(books__in=books).distinct()
    for c in cats:
        cat_books = books.filter(category=c)
        cat_count = OrderItem.objects.filter(book__in=cat_books, order__status='completed').count()
        cat_rev = OrderItem.objects.filter(book__in=cat_books, order__status='completed').aggregate(Sum('price'))['price__sum'] or 0.0
        category_stats.append({
            "category": c.name,
            "books_count": cat_books.count(),
            "sales_count": cat_count,
            "revenue": float(cat_rev)
        })

    return JsonResponse({
        "status": "success",
        "seller": request.user.username,
        "is_superuser": request.user.is_superuser,
        "total_books": books.count(),
        "total_sales_count": total_sales_count,
        "total_revenue": total_revenue,
        "sales_by_category": category_stats
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def health_check_api(request):
    """
    GET /api/health/
    System Health Check.
    """
    try:
        book_count = Book.objects.count()
        cat_count = Category.objects.count()
        order_count = Order.objects.count()
        db_ok = True
    except Exception as e:
        db_ok = False
        book_count = cat_count = order_count = 0

    return JsonResponse({
        "status": "healthy" if db_ok else "unhealthy",
        "system": "KhanetBook E-Book Store",
        "version": "1.0.0",
        "database": {
            "status": "connected" if db_ok else "error",
            "total_books": book_count,
            "total_categories": cat_count,
            "total_orders": order_count
        }
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
