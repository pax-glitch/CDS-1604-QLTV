#!/usr/bin/env python
"""
Management script for Library Management System
"""
import click
from app import create_app, db, bcrypt
from app.models import User, Author, Genre, Publisher, Book, Reader, Staff, BookAuthor, BookGenre, Borrow
from datetime import datetime, timedelta
import random

app = create_app()

@click.group()
def cli():
    """Library Management System - Management Commands"""
    pass

@cli.command()
def initdb():
    """Initialize the database"""
    with app.app_context():
        click.echo('Creating database tables...')
        db.create_all()
        click.echo('✓ Database tables created successfully!')

@cli.command()
def dropdb():
    """Drop all database tables"""
    with app.app_context():
        if click.confirm('Are you sure you want to drop all tables?'):
            click.echo('Dropping all tables...')
            db.drop_all()
            click.echo('✓ All tables dropped!')

@cli.command()
def seed():
    """Seed the database with sample data"""
    with app.app_context():
        click.echo('Seeding database...')
        
        # Create superadmin
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@library.com',
                full_name='Super Admin',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                role='superadmin',
                is_active=True
            )
            db.session.add(admin)
            db.session.flush()
            
            staff_admin = Staff(user_id=admin.id, position='Quản trị viên', branch='Trụ sở chính')
            db.session.add(staff_admin)
            click.echo('✓ Created superadmin (username: admin, password: admin123)')
        
        # Create staff user
        if not User.query.filter_by(username='staff').first():
            staff_user = User(
                username='staff',
                email='staff@library.com',
                full_name='Nhân viên thư viện',
                password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
                role='staff',
                is_active=True
            )
            db.session.add(staff_user)
            db.session.flush()
            
            staff_info = Staff(user_id=staff_user.id, position='Thủ thư', branch='Trụ sở chính')
            db.session.add(staff_info)
            click.echo('✓ Created staff (username: staff, password: staff123)')
        
        # Create reader user
        if not User.query.filter_by(username='reader').first():
            reader_user = User(
                username='reader',
                email='reader@example.com',
                full_name='Nguyễn Văn A',
                password=bcrypt.generate_password_hash('reader123').decode('utf-8'),
                role='reader',
                is_active=True
            )
            db.session.add(reader_user)
            db.session.flush()
            
            reader_info = Reader(
                user_id=reader_user.id,
                card_number='LIB2024001',
                full_name='Nguyễn Văn A',
                email='reader@example.com',
                phone='0901234567',
                address='123 Đường ABC, Hà Nội',
                card_issue_date=datetime.now().date(),
                card_expiry_date=(datetime.now() + timedelta(days=365)).date(),
                status='active'
            )
            db.session.add(reader_info)
            click.echo('✓ Created reader (username: reader, password: reader123)')
        
        # Create sample authors
        authors_data = [
            {'name': 'Nguyễn Nhật Ánh', 'bio': 'Nhà văn Việt Nam nổi tiếng'},
            {'name': 'Tô Hoài', 'bio': 'Nhà văn, nhà thơ Việt Nam'},
            {'name': 'Ngô Tất Tố', 'bio': 'Nhà văn hiện thực Việt Nam'},
            {'name': 'Dale Carnegie', 'bio': 'Tác giả người Mỹ, chuyên gia phát triển bản thân'},
            {'name': 'Paulo Coelho', 'bio': 'Nhà văn người Brazil'},
        ]
        
        authors = []
        for data in authors_data:
            if not Author.query.filter_by(name=data['name']).first():
                author = Author(**data)
                db.session.add(author)
                authors.append(author)
        db.session.flush()
        click.echo(f'✓ Created {len(authors_data)} authors')
        
        # Create genres
        genres_data = [
            {'name': 'Văn học Việt Nam', 'description': 'Sách văn học trong nước'},
            {'name': 'Văn học nước ngoài', 'description': 'Sách văn học dịch'},
            {'name': 'Kỹ năng sống', 'description': 'Sách phát triển bản thân'},
            {'name': 'Kinh tế', 'description': 'Sách về kinh doanh và kinh tế'},
            {'name': 'Thiếu nhi', 'description': 'Sách dành cho trẻ em'},
            {'name': 'Khoa học', 'description': 'Sách khoa học và công nghệ'},
            {'name': 'Lịch sử', 'description': 'Sách lịch sử'},
            {'name': 'Triết học', 'description': 'Sách triết học và tư tưởng'},
        ]
        
        genres = []
        for data in genres_data:
            if not Genre.query.filter_by(name=data['name']).first():
                genre = Genre(**data)
                db.session.add(genre)
                genres.append(genre)
        db.session.flush()
        click.echo(f'✓ Created {len(genres_data)} genres')
        
        # Create publishers
        publishers_data = [
            {'name': 'NXB Trẻ', 'address': 'Hà Nội', 'contact': '024-xxx-xxxx'},
            {'name': 'NXB Kim Đồng', 'address': 'TP.HCM', 'contact': '028-xxx-xxxx'},
            {'name': 'NXB Văn học', 'address': 'Hà Nội', 'contact': '024-xxx-xxxx'},
        ]
        
        publishers = []
        for data in publishers_data:
            if not Publisher.query.filter_by(name=data['name']).first():
                publisher = Publisher(**data)
                db.session.add(publisher)
                publishers.append(publisher)
        db.session.flush()
        click.echo(f'✓ Created {len(publishers_data)} publishers')
        
        # Create sample books with real cover images
        books_data = [
            {
                'title': 'Tôi thấy hoa vàng trên cỏ xanh', 
                'isbn': '9786041012345', 
                'published_year': 2010, 
                'description': 'Truyện kể về tuổi thơ nghèo khó nhưng đầy ắp những ước mơ của hai anh em Thiều và Tường tại một vùng quê miền Trung Việt Nam.',
                'total_quantity': 5,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/5e/18/24/2a6154ba08df6ce6161c13f4303fa19e.jpg.webp'
            },
            {
                'title': 'Dế Mèn phiêu lưu ký', 
                'isbn': '9786041012346', 
                'published_year': 1941,
                'description': 'Tác phẩm văn học thiếu nhi kinh điển của Tô Hoài, kể về cuộc phiêu lưu của chú dế mèn nhỏ bé.',
                'total_quantity': 8,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/be/6e/6b/890dea5600e43e1d1de6f0ca1ffa3fd6.jpg.webp'
            },
            {
                'title': 'Tắt đèn', 
                'isbn': '9786041012347', 
                'published_year': 1939,
                'description': 'Tiểu thuyết hiện thực phê phán của Ngô Tất Tố về cuộc sống khốn khó của nông dân Việt Nam đầu thế kỷ 20.',
                'total_quantity': 3,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/f3/be/82/01c6c657c54ff82ee616e2f7a0c0685a.jpg.webp'
            },
            {
                'title': 'Đắc nhân tâm', 
                'isbn': '9786041012348', 
                'published_year': 1936,
                'description': 'Cuốn sách kinh điển về kỹ năng giao tiếp và xây dựng mối quan hệ của Dale Carnegie.',
                'total_quantity': 10,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/d7/d7/d7/3b37e7a7dcb8d7770b0f9c40b82ff6ca.jpg.webp'
            },
            {
                'title': 'Nhà giả kim', 
                'isbn': '9786041012349', 
                'published_year': 1988,
                'description': 'Cuốn tiểu thuyết triết lý nổi tiếng của Paulo Coelho về hành trình tìm kiếm kho báu và bản thân.',
                'total_quantity': 7,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/45/3b/fc/aa81d0a534b45706be383c8d0f8a8b41.jpg.webp'
            },
            {
                'title': 'Sapiens: Lược sử loài người',
                'isbn': '9786041012350',
                'published_year': 2011,
                'description': 'Tác phẩm nghiên cứu lịch sử tiến hóa của loài người từ thời nguyên thủy đến hiện đại.',
                'total_quantity': 6,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/5e/19/61/b6dfd51be378c8f85c4ad88f536e81a5.jpg.webp'
            },
            {
                'title': 'Tuổi trẻ đáng giá bao nhiêu',
                'isbn': '9786041012351',
                'published_year': 2017,
                'description': 'Sách kỹ năng sống về cách trân trọng và tận dụng thời gian tuổi trẻ.',
                'total_quantity': 8,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/93/7e/1f/62bd5e8f0ffcce36e4a5bd0a88c5547d.jpg.webp'
            },
            {
                'title': 'Cà phê cùng Tony',
                'isbn': '9786041012352',
                'published_year': 2018,
                'description': 'Tập hợp những bài viết truyền cảm hứng về khởi nghiệp và kinh doanh.',
                'total_quantity': 5,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/d3/c0/8e/9f5cb11c139e668ddb0f6e6c5f50a174.jpg.webp'
            },
            {
                'title': 'Ngôi nhà nhỏ trên thảo nguyên',
                'isbn': '9786041012353',
                'published_year': 1935,
                'description': 'Câu chuyện về cuộc sống của gia đình nhỏ trên vùng đất hoang sơ nước Mỹ.',
                'total_quantity': 4,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/0e/b4/7b/d4c07e8f8e2d5c3e1563fba0b4f6ca68.jpg.webp'
            },
            {
                'title': 'Mắt biếc',
                'isbn': '9786041012354',
                'published_year': 1990,
                'description': 'Truyện tình lãng mạn của Nguyễn Nhật Ánh về tình yêu tuổi học trò.',
                'total_quantity': 9,
                'cover_image': 'https://salt.tikicdn.com/cache/750x750/ts/product/d8/96/1e/6357a6b9f1b268225b46056af017a8bf.jpg.webp'
            },
        ]
        
        all_authors = Author.query.all()
        all_genres = Genre.query.all()
        all_publishers = Publisher.query.all()
        
        books_created = 0
        for data in books_data:
            if not Book.query.filter_by(isbn=data['isbn']).first():
                book = Book(
                    title=data['title'],
                    isbn=data['isbn'],
                    published_year=data['published_year'],
                    description=data['description'],
                    total_quantity=data['total_quantity'],
                    available_quantity=data['total_quantity'],
                    cover_image=data.get('cover_image'),
                    publisher_id=random.choice(all_publishers).id if all_publishers else None
                )
                db.session.add(book)
                db.session.flush()
                
                # Add authors (unique)
                selected_authors = random.sample(all_authors, min(random.randint(1, 2), len(all_authors)))
                for author in selected_authors:
                    book_author = BookAuthor(book_id=book.id, author_id=author.id)
                    db.session.add(book_author)
                
                # Add genres (unique)
                selected_genres = random.sample(all_genres, min(random.randint(1, 2), len(all_genres)))
                for genre in selected_genres:
                    book_genre = BookGenre(book_id=book.id, genre_id=genre.id)
                    db.session.add(book_genre)
                
                books_created += 1
        
        click.echo(f'✓ Created {books_created} books')
        
        # Create sample readers
        readers_data = []
        for i in range(1, 11):
            card_number = f"LIB2024{i:05d}"
            if not Reader.query.filter_by(card_number=card_number).first():
                reader = Reader(
                    card_number=card_number,
                    full_name=f'Độc giả {i}',
                    email=f'reader{i}@example.com',
                    phone=f'090000000{i}',
                    address=f'Địa chỉ {i}, Hà Nội',
                    card_issue_date=datetime.now().date(),
                    card_expiry_date=(datetime.now() + timedelta(days=365)).date(),
                    status='active'
                )
                db.session.add(reader)
                readers_data.append(reader)
        
        db.session.flush()
        click.echo(f'✓ Created {len(readers_data)} readers')
        
        # Create sample borrows
        all_books = Book.query.all()
        all_readers = Reader.query.all()
        staff_obj = Staff.query.first()
        
        borrows_created = 0
        for reader in all_readers[:5]:
            for _ in range(random.randint(1, 3)):
                book = random.choice(all_books)
                if book.available_quantity > 0:
                    borrow_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    due_date = borrow_date + timedelta(days=14)
                    
                    borrow = Borrow(
                        reader_id=reader.id,
                        book_id=book.id,
                        staff_id=staff_obj.id if staff_obj else None,
                        borrow_date=borrow_date,
                        due_date=due_date,
                        status='borrowed'
                    )
                    
                    book.available_quantity -= 1
                    db.session.add(borrow)
                    borrows_created += 1
        
        click.echo(f'✓ Created {borrows_created} borrow records')
        
        db.session.commit()
        click.echo('\n✓ Database seeded successfully!')
        click.echo('\n=== Login Credentials ===')
        click.echo('Superadmin: admin / admin123')
        click.echo('Staff: staff / staff123')
        click.echo('Reader: reader / reader123')

@cli.command()
def reset():
    """Drop and recreate database with sample data"""
    with app.app_context():
        if click.confirm('This will delete all data. Continue?'):
            click.echo('Dropping all tables...')
            db.drop_all()
            click.echo('Creating tables...')
            db.create_all()
            click.echo('Seeding data...')
            ctx = click.Context(seed)
            ctx.invoke(seed)
            click.echo('\n✓ Database reset complete!')

if __name__ == '__main__':
    cli()
