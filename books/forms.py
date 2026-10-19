import os
from django import forms
from .models import Book, Category

ALLOWED_COVER_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
ALLOWED_BOOK_EXTENSIONS = ['.pdf', '.epub']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'category', 'price', 
            'pages', 'isbn', 'description', 
            'cover_image', 'pdf_file', 'sample_file', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อหนังสือ E-book'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อผู้แต่ง หรือ สำนักพิมพ์'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น 978-616-xxx-xxx-x'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'เรื่องย่อ / ข้อมูลสารบัญ'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'sample_file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("ราคาหนังสือต้องไม่ติดลบ (ระบุ 0 ได้หากต้องการแจกฟรี)")
        return price

    def clean_cover_image(self):
        cover = self.cleaned_data.get('cover_image')
        if cover and hasattr(cover, 'name'):
            ext = os.path.splitext(cover.name)[1].lower()
            if ext not in ALLOWED_COVER_EXTENSIONS:
                raise forms.ValidationError(f"ไฟล์รูปภาพปกต้องเป็นนามสกุล {', '.join(ALLOWED_COVER_EXTENSIONS)} เท่านั้น")
            # 5MB limit
            if cover.size > 5 * 1024 * 1024:
                raise forms.ValidationError("ขนาดไฟล์รูปภาพต้องไม่เกิน 5 MB")
        return cover

    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if file and hasattr(file, 'name'):
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_BOOK_EXTENSIONS:
                raise forms.ValidationError(f"ไฟล์ E-Book ต้องเป็นนามสกุล {', '.join(ALLOWED_BOOK_EXTENSIONS)} เท่านั้น")
            # 50MB limit
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("ขนาดไฟล์ E-Book ต้องไม่เกิน 50 MB")
        return file

    def clean_sample_file(self):
        file = self.cleaned_data.get('sample_file')
        if file and hasattr(file, 'name'):
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_BOOK_EXTENSIONS:
                raise forms.ValidationError(f"ไฟล์ตัวอย่างต้องเป็นนามสกุล {', '.join(ALLOWED_BOOK_EXTENSIONS)} เท่านั้น")
        return file


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อหมวดหมู่'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'slug-name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'คำอธิบายหมวดหมู่'}),
        }
