import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app import create_app
from app.extensions import db

app = create_app()

def alter_schema():
    with app.app_context():
        db.create_all()
        conn = db.engine.connect()

        # Users table updates
        columns = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("needs_password_reset", "BOOLEAN DEFAULT FALSE"),
            ("two_factor_enabled", "BOOLEAN DEFAULT FALSE"),
            ("session_version", "INTEGER DEFAULT 1")
        ]
        
        for col, definition in columns:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {definition}"))
                conn.commit()
                print(f"Added {col} to users")
            except Exception as e:
                print(f"{col} already exists or error: {e}")
                conn.rollback()

        # Jobs table
        try:
            conn.execute(text("""
            CREATE TABLE background_jobs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                last_run_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """))
            conn.commit()
            print("Created background_jobs table")
        except Exception as e:
            print("background_jobs already exists or error:", e)
            conn.rollback()
            
        conn.close()

if __name__ == '__main__':
    alter_schema()
