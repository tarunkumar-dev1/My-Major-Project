import mongomock
from pymongo.errors import ConfigurationError
import logging
import bcrypt

db = None

def init_db(mongo_uri):
    """
    Initializes the MongoDB connection using mongomock and seeds data.
    """
    global db
    try:
        client = mongomock.MongoClient()
        db = client['skillgap_db']
        
        # Seed test user
        if not db.users.find_one({"email": "ultimate@example.com"}):
            hashed = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({
                "name": "Ultimate Tester",
                "email": "ultimate@example.com",
                "hashed_password": hashed,
                "role": "student"
            })
            
        # Seed careers for test_full_flow.py logic
        if db.careers.count_documents({}) == 0:
            db.careers.insert_many([
                {
                    "career_name": "Machine Learning Engineer",
                    "required_skills": ["Python", "TensorFlow", "PyTorch", "SQL", "MLOps", "Data Structures", "Algorithms"],
                    "difficulty_level": "Advanced"
                },
                {
                    "career_name": "Data Scientist",
                    "required_skills": ["Python", "R", "SQL", "Statistics", "Machine Learning", "Data Visualization", "pandas"],
                    "difficulty_level": "Advanced"
                }
            ])
            
        logging.info(f"Successfully connected to mongomock database: {db.name}")
        
    except Exception as e:
        logging.error(f"Failed to connect to mongomock: {str(e)}")
        db = None

def get_db():
    """
    Returns the initialized database instance.
    Throws an Exception if not initialized.
    """
    if db is None:
        raise Exception("Database connection is not initialized. Please check MongoDB.")
    return db
