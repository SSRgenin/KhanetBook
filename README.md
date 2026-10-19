# ระบบขายหนังสือออนไลน์ E-Book (Django Web Application)

เว็บแอปพลิเคชันร้านขายหนังสือออนไลน์ดิจิทัล (E-Book Store) พัฒนาด้วย **Django Framework 6.1** และ **Bootstrap 5.3** ครอบคลุมคุณสมบัติตามข้อกำหนดโครงงานอย่างสมบูรณ์แบบ

---

## 🎯 ตารางสรุปฟังก์ชันตามข้อกำหนดโครงงาน 10 ประการ

| ข้อกำหนด | สถานะ | ฟังก์ชันที่พัฒนาในระบบ |
| :--- | :---: | :--- |
| **1. ระบบสมัครสมาชิก เข้าสู่ระบบ และออกจากระบบ** |  ครบถ้วน | มีระบบ Register, Login, Logout พร้อมการเข้ารหัสรหัสผ่าน และแจ้งเตือนข้อความ (Flash Messages) |
| **2. ผู้ใช้งานอย่างน้อย 2 บทบาท พร้อมกำหนดสิทธิ์จริง** |  ครบถ้วน | - **Customer (ลูกค้า/ผู้อ่าน)**: สั่งซื้อหนังสือ, ดูคลังหนังสือดิจิทัล, ดาวน์โหลด PDF, ดูประวัติคำสั่งซื้อ<br>- **Seller / Admin (ผู้ขาย)**: จัดการหนังสือ (CRUD), ดูสถิติยอดจำหน่าย มีสิทธิ์เข้าถึง Seller Dashboard<br>ตรวจสอบสิทธิ์จริงผ่าน Decorator `@role_required` |
| **3. CRUD ข้อมูลด้วย Django Model** |  ครบถ้วน | หน้าสำหรับผู้ขายในการ เพิ่ม (Create), ดูรายละเอียด (Read), แก้ไข (Update) และลบ (Delete) ข้อมูลหนังสือและไฟล์ ผ่าน Web UI จริง |
| **4. ระบบค้นหาข้อมูล** |  ครบถ้วน | ค้นหาตามชื่อหนังสือ, ผู้แต่ง, คำอธิบาย, รหัส ISBN พร้อมตัวกรองตามหมวดหมู่ (Category Filter) และการเรียงลำดับราคา |
| **5. อัปโหลดรูปภาพหรือไฟล์** |  ครบถ้วน | - ภาพหน้าปกหนังสือ (`ImageField` ผ่าน Pillow)<br>- ไฟล์หนังสือดิจิทัล PDF/EPUB (`FileField`) พร้อมระบบรักษาความปลอดภัยอนุญาตเฉพาะผู้ซื้อดาวน์โหลด |
| **6. การแบ่งหน้ารายการข้อมูล (Pagination)** |  ครบถ้วน | ใช้ Django `Paginator` แบ่งหน้าแสดงผลหนังสือ หน้าละ 6 เล่ม รองรับการคงค่าคำค้นหาและตัวกรอง |
| **7. ความสัมพันธ์ระหว่าง Model** |  ครบถ้วน | - **One-to-One**: `User` ⟷ `UserProfile`<br>- **One-to-Many**: `Category` ⟷ `Book`<br>- **Many-to-Many**: `Order` ⟷ `Book` ผ่าน `OrderItem` |
| **8. การตรวจสอบความถูกต้อง (Form Validation)** |  ครบถ้วน | - ตรวจสอบราคาห้ามติดลบ (`clean_price`)<br>- ตรวจสอบนามสกุลไฟล์ (.jpg/.png สำหรับปก และ .pdf/.epub สำหรับหนังสือ)<br>- ตรวจสอบขนาดไฟล์ และรหัสผ่านตรงกัน |
| **9. ส่วนติดต่อผู้ใช้สม่ำเสมอ อ่านง่าย ใช้งานได้จริง** |  ครบถ้วน | ออกแบบด้วย **Bootstrap 5.3**, ฟอนต์ **Google Prompt**, Responsive รองรับมือถือและคอมพิวเตอร์อย่างสวยงาม |
| **10. พร้อมนำขึ้น Cloud Hosting** |  ครบถ้วน | มี `Procfile`, `requirements.txt`, `build.sh`, `render.yaml` และตั้งค่า `WhiteNoise` รองรับการ Deploy บน Render.com และ PythonAnywhere |

---

## 🔑 บัญชีทดสอบที่ติดตั้งไว้ล่วงหน้า (Demo Accounts)

ระบบมีข้อมูลทดสอบพร้อมให้ทดลองใช้งานได้ทันที:

| บทบาท (Role) | Username | Password | สิทธิ์และหน้าที่ในระบบ |
| :--- | :--- | :--- | :--- |
| **Superuser / Admin** | `*****` | `*******` | สิทธิ์สูงสุด ดูแลจัดการระบบและเข้าหลังบ้าน Django Admin |
| **Seller (ผู้ขาย/นักเขียน)** | `seller1` | `seller1234` | เพิ่ม/แก้ไข/ลบหนังสือ E-Book, ดูยอดขายใน Seller Dashboard |
| **Customer (ลูกค้า/ผู้อ่าน)** | `reader1` | `reader1234` | สั่งซื้อหนังสือ, ดาวน์โหลดไฟล์ PDF ในคลังหนังสือของฉัน |

*(สามารถกดสมัครสมาชิกใหม่ผ่านหน้าเว็บ และเลือกบทบาทที่ต้องการได้เองเช่นกัน)*

---

## 🚀 วิธีการรันบนเครื่องคอมพิวเตอร์ (Local Development)

### 1. ติดตั้งไลบรารีที่จำเป็น
```bash
py -m pip install django pillow whitenoise gunicorn
```

### 2. นำเข้าฐานข้อมูลและสร้างข้อมูลทดสอบ
```bash
py manage.py migrate
py seed_data.py
```
### 3. รัน Development Server
```bash
py manage.py runserver
```
เข้าใช้งานผ่านเบราว์เซอร์ที่: **`http://127.0.0.1:8000/`**

---

## ☁️ คู่มือการนำระบบขึ้น Cloud Hosting (Deployment Guide)

### ตัวเลือกที่ 1: Deploy บน Render.com (ฟรีและแนะนำที่สุด)
1. **สร้างบัญชี GitHub และสร้าง Repository ใหม่**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Django E-book Store"
   git branch -M main
   git remote add origin <URL_REPOSITORY_ของท่าน>
   git push -u origin main
   ```
2. **เข้าสู่ระบบที่ [Render.com](https://render.com/)**
3. คลิก **New +** และเลือก **Web Service**
4. เชื่อมต่อกับ GitHub Repository ของท่าน
5. กำหนดการตั้งค่า:
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
6. เพิ่มตัวแปร **Environment Variables**:
   - `PYTHON_VERSION` = `3.11.9`
   - `DEBUG` = `False`
   - `SECRET_KEY` = (คลิก Generate หรือตั้งสตริงยาวๆ)
7. คลิก **Create Web Service** ระบบจะทำการ Deploy อัตโนมัติและมอบ URL สาธารณะให้เข้าถึงได้ผ่านอินเทอร์เน็ตทันที

---

### ตัวเลือกที่ 2: Deploy บน PythonAnywhere.com
1. สมัครสมาชิกฟรีที่ [PythonAnywhere.com](https://www.pythonanywhere.com/)
2. เปิด **Bash Console** แล้วโคลนโค้ดโปรเจกต์ลงมา
3. สร้าง Virtualenv และติดตั้งแพ็กเกจ:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   python manage.py migrate
   python seed_data.py
   python manage.py collectstatic
   ```
4. ในแท็บ **Web** กดเลือก **Add a new web app** -> **Manual configuration** -> **Python 3.10**
5. ตั้งค่า **Virtualenv path** และแก้ไฟล์ **WSGI configuration file** ให้ชี้มาที่ `config.wsgi`
6. กำหนด Static files:
   - URL: `/static/` -> Directory: `/home/<username>/ebook_store/staticfiles/`
   - URL: `/media/` -> Directory: `/home/<username>/ebook_store/media/`
7. คลิกปุ่ม **Reload Web App** เข้าใช้งานผ่านโดเมน `<username>.pythonanywhere.com`
#   K h a n e t B o o k 
 
 #   K h a n e t B o o k 
 
 #   K h a n e t B o o k 
 
 #   K h a n e t B o o k 
 
 
