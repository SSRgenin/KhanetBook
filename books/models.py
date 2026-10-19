from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="ชื่อหมวดหมู่")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="คำอธิบายหมวดหมู่")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "หมวดหมู่หนังสือ"
        verbose_name_plural = "หมวดหมู่หนังสือ"
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', verbose_name="ผู้ขาย")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books', verbose_name="หมวดหมู่")
    title = models.CharField(max_length=200, verbose_name="ชื่อหนังสือ")
    author = models.CharField(max_length=150, verbose_name="ผู้แต่ง / สำนักพิมพ์")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา (บาท)")
    description = models.TextField(verbose_name="เนื้อหาโดยย่อ / คำอธิบาย")
    pages = models.PositiveIntegerField(default=100, verbose_name="จำนวนหน้า")
    isbn = models.CharField(max_length=30, blank=True, verbose_name="ISBN / รหัสหนังสือ")
    
    # File & Image Uploads
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name="ภาพหน้าปก")
    pdf_file = models.FileField(upload_to='book_files/', verbose_name="ไฟล์ E-Book (PDF/EPUB)")
    sample_file = models.FileField(upload_to='book_samples/', blank=True, null=True, verbose_name="ไฟล์ตัวอย่างทดลองอ่าน")

    is_active = models.BooleanField(default=True, verbose_name="พร้อมขาย")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ลงขาย")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    class Meta:
        verbose_name = "หนังสือ E-Book"
        verbose_name_plural = "หนังสือ E-Book ทั้งหมด"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author} (฿{self.price})"

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.pk})
