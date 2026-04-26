import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/skillgap_db")
DB_NAME = os.getenv("MONGO_DB_NAME", "skillgap_db")


def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")

    db = client[DB_NAME]
    print(f"Connected to MongoDB database: {DB_NAME}")
    print("Collections:", db.list_collection_names())

    for collection_name in ["users", "careers", "roadmaps"]:
        if collection_name not in db.list_collection_names():
            print(f"\n{collection_name}: collection not found")
            continue

        print(f"\n{collection_name} documents:")
        docs = list(db[collection_name].find({}, {"hashed_password": 0}).limit(20))
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            pprint(doc)


if __name__ == "__main__":
    main()
