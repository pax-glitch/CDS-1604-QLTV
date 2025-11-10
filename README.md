# Hệ thống Quản lý Thư viện MGX

Ứng dụng web quản lý thư viện hoàn chỉnh được xây dựng bằng Flask (Python) với SQLite database. Hệ thống bao gồm quản lý sách, tác giả, thể loại, nhà xuất bản, độc giả, mượn/trả sách, báo cáo thống kê và phân quyền người dùng.

## ✨ Tính năng chính

### 🔐 Xác thực & Phân quyền
- **4 vai trò người dùng**: Superadmin, Admin, Staff, Reader
- Đăng nhập/Đăng ký với mã hóa bcrypt
- Session-based authentication với Flask-Login
- Phân quyền truy cập theo vai trò

### 📚 Quản lý Tài liệu
- **Sách**: CRUD đầy đủ với upload ảnh bìa, quản lý số lượng
- **Tác giả**: Quản lý thông tin tác giả
- **Thể loại**: Phân loại sách theo thể loại
- **Nhà xuất bản**: Quản lý thông tin NXB
- Mối quan hệ many-to-many giữa sách-tác giả và sách-thể loại
- Tìm kiếm và lọc nâng cao
- Phân trang server-side

### 👥 Quản lý Độc giả
- Thẻ thư viện với mã số duy nhất
- Quản lý thông tin cá nhân, ngày hết hạn thẻ
- Trạng thái: active, blocked, expired
- Lịch sử mượn trả của từng độc giả
- Export danh sách độc giả ra CSV

### 📖 Mượn/Trả sách
- Tạo phiếu mượn với kiểm tra số lượng sách
- Xác nhận trả sách
- Gia hạn sách (tối đa 2 lần)
- Tự động phát hiện sách quá hạn
- Trạng thái: Borrowed, Returned, Overdue, Cancelled
- Quản lý số lượng sách tự động

### 👨‍💼 Quản lý Nhân viên
- Quản lý tài khoản nhân viên
- Phân quyền vai trò
- Kích hoạt/vô hiệu hóa tài khoản
- Theo dõi hoạt động của nhân viên

### 📊 Dashboard & Báo cáo
- Thống kê tổng quan: tổng sách, độc giả, sách mượn, quá hạn
- Biểu đồ mượn sách theo tháng (Chart.js)
- Top sách được mượn nhiều nhất
- Danh sách sách quá hạn cần xử lý
- Hoạt động gần đây
- API endpoints cho charts và reports

### 🎨 Giao diện
- Thiết kế hiện đại với Bootstrap 5
- Responsive design cho mobile/tablet
- Dark sidebar với gradient effects
- Animations với Animate.css
- Font Awesome icons
- Toast notifications
- Modal confirmations

## 🚀 Cài đặt & Chạy ứng dụng

### Yêu cầu hệ thống
- Python 3.9 trở lên
- pip (Python package manager)

### Bước 1: Clone/Download dự án
```bash
cd e:\cds
```

### Bước 2: Tạo môi trường ảo (Virtual Environment)
```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\activate
```

### Bước 3: Cài đặt dependencies
```powershell
pip install -r requirements.txt
```

### Bước 4: Cấu hình môi trường
File `instance/.env` đã được tạo sẵn. Bạn có thể chỉnh sửa nếu cần:
```env
SECRET_KEY=dev-secret-key-please-change-in-production
FLASK_ENV=development
FLASK_APP=run.py
DATABASE_URL=sqlite:///database/library.db
```

### Bước 5: Khởi tạo database và seed dữ liệu mẫu
```powershell
# Khởi tạo database
python manage.py initdb

# Seed dữ liệu mẫu (bao gồm tài khoản admin)
python manage.py seed
```

### Bước 6: Chạy ứng dụng
```powershell
python run.py
```

Ứng dụng sẽ chạy tại: **http://127.0.0.1:5000**

## 👤 Tài khoản đăng nhập mặc định

Sau khi seed dữ liệu, bạn có thể đăng nhập với:

### Superadmin
- **Username**: `admin`
- **Password**: `admin123`
- **Quyền**: Toàn quyền quản trị hệ thống

### Staff
- **Username**: `staff`
- **Password**: `staff123`
- **Quyền**: Quản lý mượn/trả, CRUD sách, tác giả, độc giả

## 📁 Cấu trúc dự án

```
library_app/
├── app/
│   ├── __init__.py           # App factory
│   ├── models.py             # Database models
│   ├── forms/                # WTForms
│   │   ├── auth_forms.py
│   │   ├── library_forms.py
│   │   ├── book_forms.py
│   │   ├── reader_forms.py
│   │   └── borrow_forms.py
│   ├── routes/               # Blueprint routes
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── authors.py
│   │   ├── genres.py
│   │   ├── publishers.py
│   │   ├── books.py
│   │   ├── readers.py
│   │   ├── staff.py
│   │   ├── borrows.py
│   │   ├── profile.py
│   │   └── reports.py
│   └── utils/                # Utilities
│       ├── decorators.py     # Role decorators
│       ├── helpers.py        # Helper functions
│       └── filters.py        # Jinja filters
├── templates/
│   ├── layout/
│   │   ├── base.html
│   │   ├── sidebar.html
│   │   └── header.html
│   ├── auth/
│   ├── dashboard/
│   ├── authors/
│   ├── genres/
│   ├── publishers/
│   ├── books/
│   ├── readers/
│   ├── borrows/
│   ├── staff/
│   ├── profile/
│   └── reports/
├── static/
│   └── uploads/
│       ├── avatars/          # User avatars
│       └── covers/           # Book covers
├── database/
│   └── library.db            # SQLite database
├── instance/
│   └── .env                  # Environment config
├── config.py                 # App configuration
├── requirements.txt          # Dependencies
├── run.py                    # Application entry point
├── manage.py                 # Management commands
└── README.md                 # This file
```

## 🎯 Các chức năng chi tiết

### 1. Quản lý Sách
- Thêm/sửa/xóa sách
- Upload ảnh bìa sách (jpg/png, max 2MB)
- Gán tác giả và thể loại (multiple select)
- Quản lý số lượng sách tổng và số lượng có sẵn
- Tìm kiếm theo tên, ISBN, tác giả
- Lọc theo thể loại, nhà xuất bản, trạng thái có sẵn

### 2. Quản lý Độc giả
- Tự động tạo mã thẻ thư viện (LIBYYYYnnnnn)
- Quản lý thông tin: họ tên, email, SĐT, địa chỉ, ngày sinh
- Ngày cấp thẻ và ngày hết hạn
- Trạng thái thẻ: active/blocked/expired
- Xem lịch sử mượn trả của độc giả
- Export danh sách ra CSV

### 3. Mượn/Trả sách
- Kiểm tra số lượng sách có sẵn trước khi cho mượn
- Kiểm tra trạng thái thẻ độc giả và ngày hết hạn
- Tự động giảm/tăng số lượng sách khi mượn/trả
- Gia hạn sách (tối đa 2 lần)
- Tự động cập nhật trạng thái quá hạn
- Hủy phiếu mượn
- Độc giả xem lịch sử mượn của mình

### 4. Dashboard
- Thống kê tổng quan hệ thống
- Top sách được mượn nhiều nhất
- Hoạt động mượn/trả gần đây
- Cảnh báo sách quá hạn
- Biểu đồ và charts (Chart.js)

### 5. Báo cáo
- Biểu đồ mượn sách theo tháng (12 tháng gần nhất)
- Top sách được mượn nhiều nhất
- Phân bố trạng thái mượn trả
- Export dữ liệu ra CSV

### 6. Phân quyền
- **Superadmin**: Toàn quyền
- **Admin**: Quản lý nhân viên, xem báo cáo
- **Staff**: CRUD sách/tác giả/thể loại/NXB/độc giả, mượn/trả
- **Reader**: Xem sách, xem lịch sử mượn của mình

## 🛠️ Các lệnh quản lý

```powershell
# Khởi tạo database
python manage.py initdb

# Seed dữ liệu mẫu
python manage.py seed

# Xóa tất cả dữ liệu
python manage.py dropdb

# Reset database (xóa và tạo lại + seed)
python manage.py reset
```

## 📝 Database Schema

### Users
- id, username, email, password, full_name, role, avatar, is_active, created_at

### Authors
- id, name, bio, created_at

### Genres
- id, name, description, created_at

### Publishers
- id, name, address, contact, created_at

### Books
- id, title, isbn, publisher_id, published_year, cover_image, description
- total_quantity, available_quantity, created_at

### Readers
- id, user_id, card_number, full_name, email, phone, address
- date_of_birth, card_issue_date, card_expiry_date, status, created_at

### Staff
- id, user_id, position, branch, created_at

### Borrows
- id, reader_id, book_id, staff_id, borrow_date, due_date, return_date
- status, renew_count, created_at

### BookAuthors (Many-to-Many)
- book_id, author_id

### BookGenres (Many-to-Many)
- book_id, genre_id

### Logs
- id, user_id, action, detail, created_at

## 🔧 Tùy chỉnh cấu hình

Chỉnh sửa file `config.py` để thay đổi:
- `SECRET_KEY`: Khóa bí mật cho session
- `DEFAULT_BORROW_DAYS`: Số ngày mượn mặc định (14 ngày)
- `MAX_RENEW_COUNT`: Số lần gia hạn tối đa (2 lần)
- `ITEMS_PER_PAGE`: Số items trên mỗi trang (10)
- `MAX_CONTENT_LENGTH`: Kích thước file upload tối đa (2MB)

## 🌟 Mở rộng tính năng

### Gợi ý mở rộng:
1. **Email notifications**: Gửi email nhắc trả sách
2. **QR Code**: Tạo mã QR cho thẻ độc giả và sách
3. **Đặt sách trước**: Cho phép đặt sách đang được mượn
4. **Fine management**: Quản lý phí phạt quá hạn
5. **Mobile app**: Tạo REST API cho mobile app
6. **Advanced search**: Tìm kiếm nâng cao với Elasticsearch
7. **Book recommendations**: Gợi ý sách dựa trên lịch sử
8. **Multi-language**: Hỗ trợ đa ngôn ngữ

## 🐛 Troubleshooting

### Lỗi khi chạy lần đầu:
```powershell
# Đảm bảo đã kích hoạt virtual environment
.\venv\Scripts\activate

# Cài lại dependencies
pip install -r requirements.txt

# Khởi tạo lại database
python manage.py reset
```

### Lỗi upload file:
- Kiểm tra folder `static/uploads/avatars` và `static/uploads/covers` tồn tại
- Kiểm tra quyền ghi file
- Đảm bảo file < 2MB và định dạng jpg/png/jpeg

### Lỗi database:
```powershell
# Xóa file database cũ
Remove-Item database\library.db

# Tạo lại
python manage.py initdb
python manage.py seed
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log trong terminal
2. Đảm bảo đã cài đặt đúng Python version
3. Kiểm tra tất cả dependencies đã được cài đặt

## 📄 License

MIT License - Tự do sử dụng cho mục đích học tập và thương mại.

## 🎉 Credits

- **Flask**: Web framework
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icons
- **Chart.js**: Charts and graphs
- **Animate.css**: CSS animations

---

**Developed with ❤️ by MGX Team**

Phiên bản: 1.0.0 | Cập nhật: 2024
