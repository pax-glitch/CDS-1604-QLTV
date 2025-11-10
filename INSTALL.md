# Hướng dẫn Cài đặt Nhanh - Thư viện MGX

## Bước 1: Cài đặt Dependencies

```powershell
# Kích hoạt virtual environment (nếu chưa có thì tạo)
python -m venv venv
.\venv\Scripts\activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

## Bước 2: Khởi tạo Database

```powershell
# Khởi tạo database và bảng
python manage.py initdb

# Seed dữ liệu mẫu (bao gồm tài khoản admin/staff)
python manage.py seed
```

## Bước 3: Chạy ứng dụng

```powershell
python run.py
```

Mở trình duyệt và truy cập: **http://127.0.0.1:5000**

## Tài khoản đăng nhập mặc định

### Admin (Toàn quyền)
- Username: `admin`
- Password: `admin123`

### Staff (Nhân viên)
- Username: `staff`
- Password: `staff123`

## Lệnh quản lý database

```powershell
# Reset toàn bộ database (xóa và tạo lại + seed)
python manage.py reset

# Chỉ xóa database
python manage.py dropdb
```

## Cấu trúc thư mục quan trọng

```
e:\cds\
├── app/                    # Source code chính
├── templates/              # HTML templates
├── static/uploads/         # Thư mục chứa file upload
├── database/               # Database SQLite
├── instance/.env           # Cấu hình môi trường
├── run.py                  # File chạy ứng dụng
├── manage.py               # Lệnh quản lý
└── requirements.txt        # Dependencies
```

## Ghi chú

- Database sẽ được tạo tại: `database/library.db`
- Upload avatars: `static/uploads/avatars/`
- Upload book covers: `static/uploads/covers/`
- Mọi thay đổi cấu hình: chỉnh file `config.py` hoặc `instance/.env`

## Troubleshooting

**Lỗi module không tìm thấy:**
```powershell
pip install -r requirements.txt --force-reinstall
```

**Lỗi database:**
```powershell
Remove-Item database\library.db
python manage.py reset
```

**Lỗi quyền truy cập file:**
- Chạy terminal/PowerShell với quyền Administrator
- Kiểm tra folder `static/uploads/` có quyền ghi

---
Chúc bạn sử dụng ứng dụng thành công! 🎉
