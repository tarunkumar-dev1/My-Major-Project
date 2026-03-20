from pymongo import MongoClient
from pymongo.errors import ConfigurationError
import logging

db = None

def init_db(mongo_uri):
    """
    Initializes the MongoDB connection and tests it.
    """
    global db
    try:
        # Connect to MongoDB with a 5 second timeout for quick failure reporting
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.server_info() 
        
        # Get specified database or default to skillgap_db
        try:
            db = client.get_database()
        except ConfigurationError:
            db = client['skillgap_db']
            
        logging.info(f"Successfully connected to MongoDB database: {db.name}")
        
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {str(e)}")
        db = None

def get_db():
    """
    Returns the initialized database instance.
    Throws an Exception if not initialized.
    """
    if db is None:
        raise Exception("Database connection is not initialized. Please check MongoDB.")
    return db
