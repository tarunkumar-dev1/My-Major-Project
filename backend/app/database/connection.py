"""
Database connection helpers for the application.

This module abstracts the logic of connecting to a real MongoDB server and
falls back to an in-memory `mongomock` instance when a live server is
unreachable. It also provides a small seeding routine for sample data which
is convenient for development and tests.
"""

import logging
import bcrypt
from pymongo import MongoClient


db = None


def init_db(mongo_uri):
    """Initializes the MongoDB connection.

    Uses a real MongoDB server when available, otherwise falls back to
    `mongomock` for local demo mode. The function seeds a small amount of
    example data if collections are empty to make the development experience
    smoother.

    Args:
        mongo_uri (str): Connection URI for MongoDB. If falsy, `mongomock` is
            used automatically.
    """
    global db

    client = None
    # Attempt to connect to a real MongoDB if a URI is provided
    if mongo_uri:
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            logging.info(f"Connected to MongoDB: {mongo_uri}")
        except Exception as exc:
            # If remote DB is not reachable, fall back to in-memory DB for
            # development and testing. The exception is logged for debugging.
            logging.warning(f"Real MongoDB connection failed, falling back to mongomock: {exc}")
            client = None

    # Ensure we have a client; use mongomock as a reliable fallback
    if client is None:
        try:
            import mongomock
        except ImportError as exc:
            logging.error("mongomock fallback requested, but mongomock is not installed: %s", exc)
            raise
        client = mongomock.MongoClient()
        logging.info("Using mongomock in-memory database")

    db = client['skillgap_db']

    # Seed demo data (best-effort; failures won't prevent the app from running)
    try:
        if not db.users.find_one({"email": "ultimate@gmail.com"}):
            hashed = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({
                "name": "Ultimate Tester",
                "email": "ultimate@gmail.com",
                "hashed_password": hashed,
                "role": "student"
            })

        if db.careers.count_documents({}) == 0:
            # Insert a small set of canonical career documents to bootstrap the
            # local/demo database. This list is intentionally limited and can be
            # extended as needed.
            db.careers.insert_many([
                {"career_name": "Machine Learning Engineer", "required_skills": ["Python", "TensorFlow", "PyTorch", "SQL", "MLOps", "Data Structures", "Algorithms"], "difficulty_level": "Advanced"},
                {"career_name": "Data Scientist", "required_skills": ["Python", "R", "SQL", "Statistics", "Machine Learning", "Data Visualization", "pandas"], "difficulty_level": "Advanced"},
                {"career_name": "Frontend Developer", "required_skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Responsive Design", "Git"], "difficulty_level": "Intermediate"},
                {"career_name": "Backend Developer", "required_skills": ["Python", "Node.js", "Java", "SQL", "Docker", "REST APIs", "Microservices"], "difficulty_level": "Intermediate"},
                {"career_name": "Full Stack Developer", "required_skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Docker"], "difficulty_level": "Advanced"},
                {"career_name": "DevOps Engineer", "required_skills": ["Linux", "Bash", "Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Ansible"], "difficulty_level": "Advanced"},
                {"career_name": "Cloud Architect", "required_skills": ["AWS", "Azure", "GCP", "Networking", "Security", "System Design", "Kubernetes"], "difficulty_level": "Expert"},
                {"career_name": "Cybersecurity Analyst", "required_skills": ["Network Security", "Ethical Hacking", "Linux", "Cryptography", "Risk Assessment", "Python"], "difficulty_level": "Advanced"}
            ])

        if db.courses.count_documents({}) == 0:
            db.courses.insert_many([
                {
                    "title": "Deep Learning Specialization",
                    "url": "https://www.coursera.org/specializations/deep-learning",
                    "difficulty_level": "Advanced",
                    "career_name": "Machine Learning Engineer",
                },
                {
                    "title": "MLOps Fundamentals",
                    "url": "https://www.coursera.org/learn/mlops-fundamentals",
                    "difficulty_level": "Intermediate",
                    "career_name": "Machine Learning Engineer",
                },
            ])

        logging.info(f"Database ready: {db.name}")
    except Exception as e:
        # Log seeding problems but do not abort initialization; this keeps the
        # application usable even if example data could not be created.
        logging.exception(f"Error seeding database: {e}")


def get_db():
    """
    Returns the initialized database instance.

    Raises:
        Exception: If `init_db` has not been called prior to this function.
    """
    if db is None:
        raise Exception("Database connection is not initialized. Please check MongoDB.")
    return db
