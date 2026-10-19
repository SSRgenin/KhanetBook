import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, FileResponse
from django.contrib import messages
from django.conf import settings
from books.models import Book
from .models import Order, OrderItem

def add_to_cart(request, pk):
    book = get_object_or_404(Book, pk=pk, is_active=True)
    cart = request.session.get('cart', [])

    # Check if already in cart
    if book.pk not in cart:
        # Check if already purchased
        if request.user.is_authenticated:
            if OrderItem.objects.filter(order__user=request.user, order__status='completed', book=book).exists():
                messages.info(request, f"คุณมีหนังสือ '{book.title}' ในคลังหนังสือของคุณแล้ว")
                return redirect('my_library')
        
        cart.append(book.pk)
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"เพิ่ม '{book.title}' ลงตะกร้าเรียบร้อยแล้ว")
    else:
        messages.info(request, f"'{book.title}' อยู่ในตะกร้าสินค้าของคุณแล้ว")

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cart')


def remove_from_cart(request, pk):
    cart = request.session.get('cart', [])
    if pk in cart:
        cart.remove(pk)
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "นำหนังสือออกจากตะกร้าแล้ว")
    return redirect('cart')


def cart_view(request):
    cart_ids = request.session.get('cart', [])
    books = Book.objects.filter(id__in=cart_ids)
    total_price = sum(book.price for book in books)

    return render(request, 'orders/cart.html', {
        'books': books,
        'total_price': total_price,
    })


@login_required
def checkout_view(request):
    cart_ids = request.session.get('cart', [])
    if not cart_ids:
        messages.warning(request, "ไม่มีสินค้าในตะกร้า")
        return redirect('book_list')

    books = Book.objects.filter(id__in=cart_ids)
    total_price = sum(book.price for book in books)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'PromptPay / QR Code')
        notes = request.POST.get('notes', '')

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status=Order.STATUS_COMPLETED,  # Digital goods auto-completed on checkout
            payment_method=payment_method,
            notes=notes
        )

        # Create OrderItems
        for book in books:
            OrderItem.objects.create(
                order=order,
                book=book,
                price=book.price
            )

        # Clear cart
        request.session['cart'] = []
        request.session.modified = True

        messages.success(request, f"สั่งซื้อและชำระเงินเรียบร้อยแล้ว! รหัสคำสั่งซื้อ #{order.id} หนังสือพร้อมให้ดาวน์โหลดในคลังหนังสือของคุณทันที")
        return redirect('order_detail', pk=order.pk)

    return render(request, 'orders/checkout.html', {
        'books': books,
        'total_price': total_price,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items__book'), pk=pk)

    # Permission check: only order owner or seller/admin can view
    if not request.user.is_superuser and order.user != request.user:
        messages.error(request, "คุณไม่มีสิทธิ์ดูรายการสั่งซื้อนี้")
        return redirect('book_list')

    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__book')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def my_library(request):
    """
    Shows all purchased e-books for the current user
    """
    purchased_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='completed'
    ).select_related('book', 'order').distinct()

    books = [item.book for item in purchased_items]
    return render(request, 'orders/my_library.html', {'books': books})


@login_required
def download_book(request, pk):
    """
    Secure file download: verifies that user actually purchased the book, or is the author, or is superuser
    """
    book = get_object_or_404(Book, pk=pk)

    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status='completed',
        book=book
    ).exists()

    is_author = (book.seller == request.user)
    is_admin = request.user.is_superuser

    if not (has_purchased or is_author or is_admin):
        messages.error(request, "คุณยังไม่ได้สั่งซื้อหนังสือเล่มนี้ หรือไม่มีสิทธิ์เข้าถึงไฟล์")
        return redirect('book_detail', pk=book.pk)

    if not book.pdf_file:
        raise Http404("ไม่พบไฟล์หนังสือในระบบ")

    file_path = book.pdf_file.path
    if not os.path.exists(file_path):
        raise Http404("ไฟล์ไม่ได้อยู่บนเซิร์ฟเวอร์")

    filename = os.path.basename(file_path)
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    return response
