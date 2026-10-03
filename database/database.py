from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def init_db(app):
    """
    Initialize SQLAlchemy database extension and automatically create tables if they do not exist.
    Also ensures SQLite schema columns (e.g. password column in users table) are synchronized.
    """
    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy registers them with metadata before create_all
        import database.models  # noqa: F401
        db.create_all()

        # Automatic schema sync for SQLite to ensure password column and image_analysis table exist
        try:
            with db.engine.connect() as conn:
                res = conn.execute(text("PRAGMA table_info(users)"))
                cols = [r[1] for r in res.fetchall()]
                if 'password' not in cols and 'password_hash' in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password VARCHAR(255)"))
                    conn.execute(text("UPDATE users SET password = password_hash WHERE password IS NULL"))
                    conn.commit()
                elif 'password_hash' not in cols and 'password' in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                    conn.execute(text("UPDATE users SET password_hash = password WHERE password_hash IS NULL"))
                    conn.commit()
        except Exception as e:
            app.logger.warning(f"Database schema sync notice: {e}")
