import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from accounts.models import UserProfile
from books.models import Category, Book
from PIL import Image, ImageDraw, ImageFont
import io

def generate_book_cover(title, author, bg_color):
    """Generates an attractive book cover image in memory using Pillow"""
    img = Image.new('RGB', (600, 850), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Decorative inner border
    draw.rectangle([25, 25, 575, 825], outline=(255, 255, 255, 180), width=3)
    draw.rectangle([35, 35, 565, 815], outline=(255, 255, 255, 100), width=1)

    # Header label
    draw.text((300, 80), "E-BOOK SPECIAL EDITION", fill=(255, 255, 255), anchor="mm")
    draw.line([(200, 110), (400, 110)], fill=(255, 255, 255), width=2)

    # Title & Author
    draw.text((300, 360), title[:25], fill=(255, 255, 255), anchor="mm")
    if len(title) > 25:
        draw.text((300, 410), title[25:50], fill=(255, 255, 255), anchor="mm")
    draw.text((300, 520), f"โดย {author}", fill=(240, 240, 240), anchor="mm")

    # Bottom badge
    draw.rectangle([180, 720, 420, 770], fill=(255, 255, 255))
    draw.text((300, 745), "BEST SELLER", fill=bg_color, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    return ContentFile(buf.getvalue(), name=f"{title[:10].strip()}.jpg")

def generate_dummy_pdf(title, author):
    """Creates a basic valid PDF file with sample text"""
    content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 160 >>
stream
BT
/F1 20 Tf
50 700 Td
(Online E-Book Store Sample Document) Tj
/F1 14 Tf
0 -40 Td
(Thank you for reading this digital book.) Tj
0 -30 Td
(Django Web Application E-Book Store) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000227 00000 n 
0000000441 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
513
%%EOF
"""
    return ContentFile(content.encode('latin1'), name=f"sample_book.pdf")



def seed():
    print("🌱 Starting Seed Process...")

    # 1. Create Superuser (Admin)
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
        admin_user.first_name = "ผู้ดูแล"
        admin_user.last_name = "ระบบ"
        admin_user.save()
        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.role = UserProfile.ROLE_SELLER
        admin_profile.save()
        print("✅ Superuser created: admin / admin1234")

    # 2. Create Seller Test Account
    seller_user, created = User.objects.get_or_create(username='seller1', defaults={
        'email': 'seller1@example.com',
        'first_name': 'สมชาย',
        'last_name': 'นักเขียน'
    })
    if created:
        seller_user.set_password('seller1234')
        seller_user.save()
    seller_profile, _ = UserProfile.objects.get_or_create(user=seller_user)
    seller_profile.role = UserProfile.ROLE_SELLER
    seller_profile.save()
    print("✅ Seller account ready: seller1 / seller1234")

    # 3. Create Customer Test Account
    customer_user, created = User.objects.get_or_create(username='reader1', defaults={
        'email': 'reader1@example.com',
        'first_name': 'กิตติ',
        'last_name': 'รักอ่าน'
    })
    if created:
        customer_user.set_password('reader1234')
        customer_user.save()
    customer_profile, _ = UserProfile.objects.get_or_create(user=customer_user)
    customer_profile.role = UserProfile.ROLE_CUSTOMER
    customer_profile.save()
    print("✅ Customer account ready: reader1 / reader1234")

    # 4. Create Categories
    categories_data = [
        {"name": "เทคโนโลยีและโปรแกรมมิ่ง", "slug": "technology-programming", "desc": "รวมหนังสือ Python, Django, Web Dev และ AI"},
        {"name": "การเงินและการลงทุน", "slug": "finance-investment", "desc": "เทคนิคการเงิน หุ้น การลงทุน และอิสรภาพทางการเงิน"},
        {"name": "พัฒนาตนเองและจิตวิทยา", "slug": "self-improvement", "desc": "สร้างนิสัยที่ดี การบริหารเวลา และความเป็นผู้นำ"},
        {"name": "วรรณกรรมและนวนิยาย", "slug": "novels-literature", "desc": "เรื่องแต่ง นวนิยายแฟนตาซี สืบสวน และเรื่องสั้น"},
    ]

    cat_map = {}
    for c_data in categories_data:
        cat, _ = Category.objects.get_or_create(
            slug=c_data["slug"],
            defaults={"name": c_data["name"], "description": c_data["desc"]}
        )
        cat_map[cat.slug] = cat
    print("✅ Categories created")

    # 5. Create Sample Books
    sample_books = [
        {
            "title": "คู่มือพัฒนาเว็บด้วย Django 6 ฉบับสมบูรณ์",
            "author": "ดร. กิตติพงษ์ โค้ดดิ้ง",
            "category": cat_map["technology-programming"],
            "price": 299.00,
            "pages": 380,
            "isbn": "978-616-101-001-1",
            "desc": "เจาะลึกการพัฒนา Web Application ด้วย Django Framework และ Python ตั้งแต่พื้นฐานสถาปัตยกรรม MVT, ORM, Database Models, Authentication ไปจนถึงการ Deploy บน Cloud อย่างมืออาชีพ",
            "color": (28, 78, 128)
        },
        {
            "title": "ก้าวแรกสู่วิศวกรปัญญาประดิษฐ์ (AI & Machine Learning)",
            "author": "อรุณ เลิศปัญญา",
            "category": cat_map["technology-programming"],
            "price": 350.00,
            "pages": 420,
            "isbn": "978-616-101-002-8",
            "desc": "ปูพื้นฐานคณิตศาสตร์และอัลกอริทึม Deep Learning, LLM, Computer Vision พร้อมตัวอย่างโค้ดใช้งานจริงในภาคอุตสาหกรรม",
            "color": (15, 23, 42)
        },
        {
            "title": "อิสรภาพทางการเงินด้วย Passive Income ฉบับทำได้จริง",
            "author": "ธนภัทร รวยยั่งยืน",
            "category": cat_map["finance-investment"],
            "price": 240.00,
            "pages": 260,
            "isbn": "978-616-202-003-5",
            "desc": "แนวทางการวางแผนสร้างกระแสเงินสดจากอสังหาริมทรัพย์ หุ้นปันผล และธุรกิจดิจิทัล เพื่อก้าวสู่อิสรภาพทางการเงินก่อนวัยเกษียณ",
            "color": (22, 101, 52)
        },
        {
            "title": "Atomic Focus: ศิลปะแห่งการมีสมาธิในยุคดิจิทัล",
            "author": "พิมลดา สุขจิต",
            "category": cat_map["self-improvement"],
            "price": 199.00,
            "pages": 210,
            "isbn": "978-616-303-004-2",
            "desc": "คู่มือฝึกสติและสร้างโฟกัส ตัดสิ่งรบกวนในยุคโซเชียลมีเดีย เพิ่มประสิทธิภาพการทำงาน (Productivity) ได้มากกว่าเดิม 3 เท่า",
            "color": (147, 51, 234)
        },
        {
            "title": "ปฐมบทแห่งดวงดาว: สงครามอวกาศข้ามมิติ",
            "author": "จักรภพ สตาร์ไลท์",
            "category": cat_map["novels-literature"],
            "price": 180.00,
            "pages": 310,
            "isbn": "978-616-404-005-9",
            "desc": "นวนิยายไซไฟแฟนตาซี การเดินทางข้ามกาแล็กซีเพื่อค้นหาพลังงานทดแทนที่สูญหาย และความลับของอารยธรรมโบราณที่ซ่อนอยู่หลังหลุมดำ",
            "color": (194, 65, 12)
        },
        {
            "title": "Python 101 สำหรับผู้เริ่มต้น (แจกฟรี)",
            "author": "ศูนย์การเรียนรู้โอเพนซอร์ส",
            "category": cat_map["technology-programming"],
            "price": 0.00,
            "pages": 120,
            "isbn": "978-616-101-006-6",
            "desc": "เอกสารและคู่มือการเรียนภาษา Python พื้นฐาน สำหรับนักเรียน นิสิต นักศึกษา และผู้ที่สนใจเริ่มต้นเขียนโปรแกรมเล่มแรก ฟรีไม่มีค่าใช้จ่าย",
            "color": (2, 132, 199)
        },
        {
            "title": "จิตวิทยาสื่อสารเพื่อชนะใจคนในที่ทำงาน",
            "author": "ดนัย บุญฤทธิ์",
            "category": cat_map["self-improvement"],
            "price": 220.00,
            "pages": 240,
            "isbn": "978-616-303-007-3",
            "desc": "เทคนิคการเจรจา การฟังอย่างลึกซึ้ง และการโน้มน้าวใจเพื่อนร่วมงานและหัวหน้างานอย่างมีศิลปะ",
            "color": (79, 70, 229)
        }
    ]

    for b in sample_books:
        book, created = Book.objects.get_or_create(
            title=b["title"],
            defaults={
                "seller": seller_user,
                "category": b["category"],
                "author": b["author"],
                "price": b["price"],
                "pages": b["pages"],
                "isbn": b["isbn"],
                "description": b["desc"],
                "is_active": True
            }
        )
        if created:
            # Generate cover and PDF
            cover_file = generate_book_cover(b["title"], b["author"], b["color"])
            pdf_file = generate_dummy_pdf(b["title"], b["author"])
            book.cover_image.save(cover_file.name, cover_file, save=False)
            book.pdf_file.save(pdf_file.name, pdf_file, save=False)
            book.save()
            print(f"📖 Book created: {book.title} (฿{book.price})")

    print("\n🎉 Seeding complete! All test data and sample books are ready.")

if __name__ == '__main__':
    seed()
