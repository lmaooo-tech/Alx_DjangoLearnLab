"""
Test script to demonstrate and validate search, filtering, and ordering functionality.
This can be run using: python manage.py shell < test_query_features.py
"""

from api.models import Author, Book

# Create sample data for testing
print("=" * 60)
print("CREATING SAMPLE DATA")
print("=" * 60)

# Create authors
author1, _ = Author.objects.get_or_create(name="John Smith")
author2, _ = Author.objects.get_or_create(name="Jane Doe")
author3, _ = Author.objects.get_or_create(name="Robert Johnson")

# Create books
books_data = [
    {"title": "Django for Beginners", "publication_year": 2020, "author": author1},
    {"title": "Python Programming", "publication_year": 2019, "author": author2},
    {"title": "Advanced Django", "publication_year": 2022, "author": author1},
    {"title": "REST API Design", "publication_year": 2021, "author": author3},
    {"title": "Web Development with Python", "publication_year": 2023, "author": author2},
]

for book_data in books_data:
    Book.objects.get_or_create(
        title=book_data["title"],
        defaults={
            "publication_year": book_data["publication_year"],
            "author": book_data["author"]
        }
    )

print(f"✓ Created {Author.objects.count()} authors")
print(f"✓ Created {Book.objects.count()} books")
print()

# Display all books
print("=" * 60)
print("ALL BOOKS IN DATABASE")
print("=" * 60)
for book in Book.objects.all().order_by('title'):
    print(f"- {book.title} ({book.publication_year}) by {book.author.name}")
print()

print("=" * 60)
print("API ENDPOINT TESTING GUIDE")
print("=" * 60)
print("""
Now you can test the following API endpoints:

1. FILTERING EXAMPLES:
   ▪ /api/books/?title=django
   ▪ /api/books/?author_name=smith
   ▪ /api/books/?publication_year=2022
   ▪ /api/books/?publication_year_min=2020
   ▪ /api/books/?publication_year_max=2021
   ▪ /api/books/?publication_year_min=2020&publication_year_max=2022

2. SEARCH EXAMPLES:
   ▪ /api/books/?search=python
   ▪ /api/books/?search=django
   ▪ /api/books/?search=jane

3. ORDERING EXAMPLES:
   ▪ /api/books/?ordering=title
   ▪ /api/books/?ordering=-title
   ▪ /api/books/?ordering=publication_year
   ▪ /api/books/?ordering=-publication_year

4. COMBINED QUERIES:
   ▪ /api/books/?author_name=smith&ordering=-publication_year
   ▪ /api/books/?search=python&ordering=title
   ▪ /api/books/?publication_year_min=2020&search=django

Start the development server with:
    python manage.py runserver

Then test the endpoints using:
    - Web browser
    - curl commands
    - Postman/Insomnia
    - Django REST Framework browsable API
""")
print("=" * 60)
