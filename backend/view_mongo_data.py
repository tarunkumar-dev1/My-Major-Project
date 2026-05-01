"""
Utility to inspect a running MongoDB instance used by the project.

This small script connects to the MongoDB instance specified by
`MONGO_URI` (or the default local instance) and prints sample documents from
the `users`, `careers`, and `roadmaps` collections. It intentionally masks
the `hashed_password` field when printing users for safety.

Usage:
    python backend/view_mongo_data.py
"""

import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient


# Load optional environment variables from .env
load_dotenv()

# MongoDB connection settings with sensible defaults for local development
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")
DB_NAME = os.getenv("MONGO_DB_NAME", "skillgap_db")


def main():
    """Connect to MongoDB, list collections, and print example documents.

    The function uses a short server selection timeout so it fails quickly if
    the database is not available rather than hanging indefinitely.
    """

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    # Quick liveness check
    client.admin.command("ping")

    db = client[DB_NAME]
    print(f"Connected to MongoDB database: {DB_NAME}")
    print("Collections:", db.list_collection_names())

    # Iterate over the most useful collections and print a sample of docs.
    for collection_name in ["users", "careers", "roadmaps"]:
        if collection_name not in db.list_collection_names():
            print(f"\n{collection_name}: collection not found")
            continue

        print(f"\n{collection_name} documents:")
        # Exclude sensitive fields when printing
        docs = list(db[collection_name].find({}, {"hashed_password": 0}).limit(20))
        for doc in docs:
            # Ensure `_id` is serializable for pretty printing
            doc["_id"] = str(doc["_id"])
            pprint(doc)


if __name__ == "__main__":
    main()
