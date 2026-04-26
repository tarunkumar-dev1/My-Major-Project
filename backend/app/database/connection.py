import logging
import bcrypt

import mongomock
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

db = None

def init_db(mongo_uri):
    """
    Initializes the MongoDB connection.
    Uses a real MongoDB server when available, otherwise falls back to mongomock for local demo mode.
    """
    global db
    try:
        client = None

        if mongo_uri:
            try:
                client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
                client.admin.command("ping")
                logging.info(f"Connected to MongoDB: {mongo_uri}")
            except (ConfigurationError, ServerSelectionTimeoutError, Exception) as exc:
                logging.warning(f"Real MongoDB connection failed, falling back to mongomock: {exc}")

        if client is None:
            client = mongomock.MongoClient()
            logging.info("Using mongomock in-memory database")

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
            
        # Seed careers for test_full_flow.py logic and general usage
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
                },
                {
                    "career_name": "Frontend Developer",
                    "required_skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Responsive Design", "Git"],
                    "difficulty_level": "Intermediate"
                },
                {
                    "career_name": "Backend Developer",
                    "required_skills": ["Python", "Node.js", "Java", "SQL", "Docker", "REST APIs", "Microservices"],
                    "difficulty_level": "Intermediate"
                },
                {
                    "career_name": "Full Stack Developer",
                    "required_skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Docker"],
                    "difficulty_level": "Advanced"
                },
                {
                    "career_name": "DevOps Engineer",
                    "required_skills": ["Linux", "Bash", "Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Ansible"],
                    "difficulty_level": "Advanced"
                },
                {
                    "career_name": "Cloud Architect",
                    "required_skills": ["AWS", "Azure", "GCP", "Networking", "Security", "System Design", "Kubernetes"],
                    "difficulty_level": "Expert"
                },
                {
                    "career_name": "Cybersecurity Analyst",
                    "required_skills": ["Network Security", "Ethical Hacking", "Linux", "Cryptography", "Risk Assessment", "Python"],
                    "difficulty_level": "Advanced"
                }
            ])
            
        logging.info(f"Database ready: {db.name}")
        
    except Exception as e:
        logging.error(f"Failed to initialize database connection: {str(e)}")
        db = None

def get_db():
    """
    Returns the initialized database instance.
    Throws an Exception if not initialized.
    """
    if db is None:
        raise Exception("Database connection is not initialized. Please check MongoDB.")
    return db
