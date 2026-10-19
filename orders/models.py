from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'รอดำเนินการ'),
        (STATUS_COMPLETED, 'ชำระเงินสำเร็จ (พร้อมอ่าน)'),
        (STATUS_CANCELLED, 'ยกเลิกคำสั่งซื้อ'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="ผู้สั่งซื้อ")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="ยอดรวม (บาท)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COMPLETED, verbose_name="สถานะคำสั่งซื้อ")
    payment_method = models.CharField(max_length=50, default='PromptPay / QR Code', verbose_name="ช่องทางชำระเงิน")
    notes = models.TextField(blank=True, verbose_name="หมายเหตุ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่สั่งซื้อ")

    class Meta:
        verbose_name = "คำสั่งซื้อ"
        verbose_name_plural = "คำสั่งซื้อทั้งหมด"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} (฿{self.total_price})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="รหัสคำสั่งซื้อ")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='order_items', verbose_name="หนังสือ")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาขณะสั่งซื้อ")

    class Meta:
        verbose_name = "รายการหนังสือในคำสั่งซื้อ"
        verbose_name_plural = "รายการหนังสือในคำสั่งซื้อ"

    def __str__(self):
        return f"{self.book.title} (Order #{self.order.id})"
