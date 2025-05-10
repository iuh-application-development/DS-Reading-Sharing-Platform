import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def upgrade():
    try:
        with create_app().app_context():
            # Add image_url column to posts table
            db.engine.execute('ALTER TABLE posts ADD COLUMN image_url VARCHAR(500)')
            print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    upgrade() 