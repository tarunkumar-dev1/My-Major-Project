from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")

def seed_database():
    """Seeds the MongoDB 'careers' collection with mock requirements."""
    client = MongoClient(MONGO_URI)
    db = client.get_database() if client.get_database().name else client['skillgap_db']
    careers_col = db['careers']
    
    print("Clearing old careers...")
    careers_col.delete_many({})
    
    datasets = [
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
            "required_skills": ["Python", "Node.js", "SQL", "NoSQL", "Docker", "REST APIs", "AWS"],
            "difficulty_level": "Intermediate"
        },
        {
            "career_name": "Full Stack Developer",
            "required_skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL", "Docker", "Git"],
            "difficulty_level": "Advanced"
        },
        {
            "career_name": "Product Manager",
            "required_skills": ["Agile", "Scrum", "Data Analysis", "Wireframing", "Jira", "A/B Testing", "Communication"],
            "difficulty_level": "Intermediate"
        }
    ]
    
    print("Inserting new career datasets...")
    careers_col.insert_many(datasets)
    print("Seeding successful!")

if __name__ == "__main__":
    seed_database()
