"""
Seed script to populate demo data
Run: python seed_data.py
"""
import sys
from datetime import date, timedelta
import random

# Add app to path
sys.path.insert(0, '.')

from app.database import SessionLocal, init_db
from app import models, security

def seed_database():
    """Create demo data"""

    # Initialize database tables
    init_db()

    db = SessionLocal()

    try:
        # Clear existing data (optional)
        # db.query(models.Sale).delete()
        # db.query(models.Product).delete()
        # db.query(models.User).delete()
        # db.commit()

        # Create demo user
        print("Creating demo user...")
        demo_user = models.User(
            email="demo@example.com",
            full_name="Demo Retailer",
            hashed_password=security.hash_password("demo123"),
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✓ Created user: {demo_user.email}")

        # Create demo products
        print("\nCreating demo products...")
        products_data = [
            ("T-Shirt", "Clothing", 50, 10, 12.99),
            ("Jeans", "Clothing", 30, 8, 34.99),
            ("Shoes", "Footwear", 20, 5, 49.99),
            ("Jacket", "Clothing", 15, 3, 79.99),
            ("Hat", "Accessories", 100, 20, 8.99),
        ]

        products = []
        for name, category, stock, reorder, price in products_data:
            product = models.Product(
                owner_id=demo_user.id,
                name=name,
                category=category,
                stock=stock,
                reorder_level=reorder,
                price=price
            )
            db.add(product)
            products.append(product)
            print(f"✓ Created product: {name} (stock: {stock})")

        db.commit()

        # Create demo sales (last 30 days)
        print("\nCreating demo sales...")
        sales_count = 0
        for _ in range(40):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            days_ago = random.randint(0, 30)

            sale = models.Sale(
                user_id=demo_user.id,
                product_id=product.id,
                quantity=quantity,
                sold_on=date.today() - timedelta(days=days_ago)
            )
            db.add(sale)
            sales_count += 1

        db.commit()
        print(f"✓ Created {sales_count} demo sales")

        # Print summary
        print("\n" + "="*50)
        print("✅ Demo data created successfully!")
        print("="*50)
        print(f"\n📧 Demo Account:")
        print(f"   Email:    demo@example.com")
        print(f"   Password: demo123")
        print(f"\n📊 Demo Data:")
        print(f"   Users:    1")
        print(f"   Products: {len(products)}")
        print(f"   Sales:    {sales_count}")
        print(f"\n🚀 Next Steps:")
        print(f"   1. Start server: uvicorn app.main:app --reload")
        print(f"   2. Visit: http://localhost:8000/docs")
        print(f"   3. Use credentials above to login")
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
