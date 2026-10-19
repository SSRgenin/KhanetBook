from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.contrib import messages
from accounts.decorators import role_required
from .models import Book, Category
from .forms import BookForm, CategoryForm

def book_list(request):
    """
    Public catalog with Search, Category Filter, Sorting, and Pagination
    """
    books = Book.objects.filter(is_active=True).select_related('category', 'seller')
    categories = Category.objects.annotate(book_count=Count('books')).filter(book_count__gt=0)
    
    # 1. Search filter (q)
    query = request.GET.get('q', '').strip()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(isbn__icontains=query)
        )

    # 2. Category filter
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        books = books.filter(category=selected_category)

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

    # 4. Pagination (6 books per page for responsive grid)
    paginator = Paginator(books, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort_option': sort_option,
        'total_count': books.count(),
    })


def book_detail(request, pk):
    """
    Display single book detail, sample download, and purchase status
    """
    book = get_object_or_404(Book.objects.select_related('category', 'seller'), pk=pk)
    
    # Check if logged in user already purchased this book
    is_purchased = False
    if request.user.is_authenticated:
        from orders.models import OrderItem
        is_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__status='completed',
            book=book
        ).exists()

    # Related books in the same category
    related_books = Book.objects.filter(category=book.category, is_active=True).exclude(pk=book.pk)[:3]

    return render(request, 'books/book_detail.html', {
        'book': book,
        'is_purchased': is_purchased,
        'related_books': related_books,
    })


@role_required(allowed_roles=['seller'])
def book_create(request):
    """
    Role-protected view for Sellers to publish a new e-book (CRUD - Create)
    """
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.seller = request.user
            book.save()
            messages.success(request, f"เพิ่มหนังสือ '{book.title}' สำเร็จแล้ว!")
            return redirect('book_detail', pk=book.pk)
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อผิดพลาดด้านล่าง")
    else:
        form = BookForm()

    return render(request, 'books/book_form.html', {
        'form': form,
        'action_title': 'เพิ่มหนังสือ E-Book เล่มใหม่',
        'button_text': 'บันทึกและเผยแพร่',
    })


@role_required(allowed_roles=['seller'])
def book_update(request, pk):
    """
    Role-protected view for Sellers to edit their e-book (CRUD - Update)
    """
    book = get_object_or_404(Book, pk=pk)

    # Permission check: seller can only edit their own book (superuser can edit all)
    if not request.user.is_superuser and book.seller != request.user:
        messages.error(request, "คุณไม่มีสิทธิ์แก้ไขหนังสือเล่มนี้ (ไม่ใช่ผู้ขายเจ้าของผลงาน)")
        return redirect('book_detail', pk=book.pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"แก้ไขข้อมูลหนังสือ '{book.title}' สำเร็จแล้ว")
            return redirect('book_detail', pk=book.pk)
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อผิดพลาด")
    else:
        form = BookForm(instance=book)

    return render(request, 'books/book_form.html', {
        'form': form,
        'book': book,
        'action_title': f"แก้ไขข้อมูลหนังสือ: {book.title}",
        'button_text': 'บันทึกการแก้ไข',
    })


@role_required(allowed_roles=['seller'])
def book_delete(request, pk):
    """
    Role-protected view for Sellers to delete their e-book (CRUD - Delete)
    """
    book = get_object_or_404(Book, pk=pk)

    # Permission check
    if not request.user.is_superuser and book.seller != request.user:
        messages.error(request, "คุณไม่มีสิทธิ์ลบหนังสือเล่มนี้")
        return redirect('book_detail', pk=book.pk)

    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f"ลบหนังสือ '{title}' ออกจากระบบเรียบร้อยแล้ว")
        return redirect('seller_dashboard')

    return render(request, 'books/book_confirm_delete.html', {'book': book})


@role_required(allowed_roles=['seller'])
def seller_dashboard(request):
    """
    Seller Dashboard: Overview of published books, sales statistics, and management
    """
    if request.user.is_superuser:
        books = Book.objects.all().select_related('category', 'seller')
    else:
        books = Book.objects.filter(seller=request.user).select_related('category')

    # Aggregates
    from orders.models import OrderItem
    total_sales_count = OrderItem.objects.filter(book__in=books, order__status='completed').count()
    total_revenue = OrderItem.objects.filter(book__in=books, order__status='completed').aggregate(Sum('price'))['price__sum'] or 0

    return render(request, 'books/seller_dashboard.html', {
        'books': books,
        'total_books': books.count(),
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
    })
