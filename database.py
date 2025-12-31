from sqlmodel import SQLModel, create_engine, Session

# This creates a file named 'finance.db' in your folder
sqlite_file_name = "finance.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False is needed only for SQLite
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Creates the tables if they don't exist yet."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency: Provides a database session for each request."""
    with Session(engine) as session:
        yield session