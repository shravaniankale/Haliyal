import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import BASE_DIR

# Database path (SQLite for local development, easy switch to PostgreSQL)
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "krishi_mitra.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# For SQLite, check_same_thread needs to be False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def run_migrations():
    """Ensures dynamic SQLite column migrations if tables pre-exist."""
    if not DATABASE_URL.startswith("sqlite"):
        return

    db_path = DEFAULT_DB_PATH
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

        # Migrate schemes columns
        if "schemes" in tables:
            existing_schemes = [col[1] for col in c.execute("PRAGMA table_info(schemes)").fetchall()]
            schemes_cols = [
                ("scheme_code", "VARCHAR(50)"),
                ("eligibility_rule_json", "TEXT"),
                ("record_type", "VARCHAR(50) DEFAULT 'real_scheme'"),
                ("rag_document_id", "VARCHAR(100)"),
                ("benefit_amount", "FLOAT"),
                ("benefit_frequency", "VARCHAR(100)"),
                ("benefit_type", "VARCHAR(100)"),
                ("exclusion_conditions", "TEXT"),
                ("source_document_title", "VARCHAR(255)"),
                ("source_published_date", "VARCHAR(50)"),
                ("source_last_verified", "VARCHAR(50)")
            ]
            for col_name, col_type in schemes_cols:
                if col_name not in existing_schemes:
                    try:
                        c.execute(f"ALTER TABLE schemes ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

        # Migrate users columns
        if "users" in tables:
            existing_users = [col[1] for col in c.execute("PRAGMA table_info(users)").fetchall()]
            users_cols = [
                ("username", "VARCHAR(50)"),
                ("email", "VARCHAR(100)"),
                ("theme_preference", "VARCHAR(20) DEFAULT 'light'"),
                ("voice_gender_preference", "VARCHAR(20) DEFAULT 'female'"),
                ("voice_assistant_enabled", "BOOLEAN DEFAULT 1"),
                ("auto_voice_response", "BOOLEAN DEFAULT 1"),
                ("voice_input_enabled", "BOOLEAN DEFAULT 1"),
                ("speech_speed", "FLOAT DEFAULT 1.0")
            ]
            for col_name, col_type in users_cols:
                if col_name not in existing_users:
                    try:
                        c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

        # Migrate farmer_profiles columns
        if "farmer_profiles" in tables:
            existing_farmer = [col[1] for col in c.execute("PRAGMA table_info(farmer_profiles)").fetchall()]
            farmer_cols = [
                ("email", "VARCHAR(100)"),
                ("confirmed_fields", "TEXT"),
                ("missing_fields", "TEXT"),
                ("conversation_state", "VARCHAR(50) DEFAULT 'collecting_information'"),
                ("consent_for_audio_storage", "VARCHAR(50) DEFAULT 'not_collected'"),
                ("agricultural_season", "VARCHAR(50)"),
                ("soil_type", "VARCHAR(100)"),
                ("theme_preference", "VARCHAR(20) DEFAULT 'light'"),
                ("voice_gender_preference", "VARCHAR(20) DEFAULT 'female'"),
                ("voice_assistant_enabled", "BOOLEAN DEFAULT 1"),
                ("auto_voice_response", "BOOLEAN DEFAULT 1"),
                ("voice_input_enabled", "BOOLEAN DEFAULT 1"),
                ("speech_speed", "FLOAT DEFAULT 1.0"),
                ("primary_crop", "VARCHAR(100)"),
                ("secondary_crops", "TEXT DEFAULT '[]'"),
                ("land_unit", "VARCHAR(20) DEFAULT 'acres'"),
                ("sowing_date", "VARCHAR(50)"),
                ("crop_stage", "VARCHAR(100)")
            ]
            for col_name, col_type in farmer_cols:
                if col_name not in existing_farmer:
                    try:
                        c.execute(f"ALTER TABLE farmer_profiles ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

        # Migrate conversations columns
        if "conversations" in tables:
            existing_conv = [col[1] for col in c.execute("PRAGMA table_info(conversations)").fetchall()]
            conv_cols = [
                ("title", "VARCHAR(200) DEFAULT 'ಕೃಷಿ ಸಂವಾದ'"),
                ("topic", "VARCHAR(100) DEFAULT 'General Agriculture'"),
                ("selected_language", "VARCHAR(10) DEFAULT 'kn'"),
                ("selected_voice", "VARCHAR(20) DEFAULT 'female'"),
                ("current_stage", "VARCHAR(50) DEFAULT 'idle'"),
                ("confirmed_details", "TEXT DEFAULT '{}'"),
                ("missing_details", "TEXT DEFAULT '[]'"),
                ("is_active", "BOOLEAN DEFAULT 1")
            ]
            for col_name, col_type in conv_cols:
                if col_name not in existing_conv:
                    try:
                        c.execute(f"ALTER TABLE conversations ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

        # Migrate chat_messages columns
        if "chat_messages" in tables:
            existing_msgs = [col[1] for col in c.execute("PRAGMA table_info(chat_messages)").fetchall()]
            msg_cols = [
                ("transcript", "TEXT"),
                ("topic", "VARCHAR(100)")
            ]
            for col_name, col_type in msg_cols:
                if col_name not in existing_msgs:
                    try:
                        c.execute(f"ALTER TABLE chat_messages ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass

        # Ensure analysis_history table exists
        c.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id INTEGER,
                topic VARCHAR(100) NOT NULL,
                crop_information VARCHAR(100),
                season_information VARCHAR(100),
                weather_used TEXT,
                recommendations TEXT,
                eligibility_results TEXT,
                source_references TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        conn.commit()
        conn.close()

def get_db():
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
