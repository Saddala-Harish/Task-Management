from app.crud import create_user
from app.schemas import UserCreate
from app.models import UserRole
from app.database import SessionLocal

def init_db():
    db = SessionLocal()
    try:
        # Create admin user
        admin = UserCreate(
            email="admin@example.com",
            password="admin123",  # Change this!
            full_name="Admin User",
            role=UserRole.admin
        )
        create_user(db, admin)
        print("Admin user created successfully!")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()