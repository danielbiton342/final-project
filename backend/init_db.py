import pymongo
import os


def initialize_database():
    # Get MongoDB URI from the environment
    mongo_uri = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri)

    # Connect to the database
    db = client.get_database("musicDB")
    singers_collection = db["singers"]

    # Insert initial data if the collection is empty
    if singers_collection.count_documents({}) == 0:
        singers_collection.insert_many(
            [
                {
                    "name": "Freddie Mercury",
                    "songs": [
                        "Bohemian Rhapsody",
                        "We Will Rock You",
                        "Don't Stop Me Now",
                    ],
                },
                {
                    "name": "Michael Jackson",
                    "songs": ["Thriller", "Billie Jean", "Beat It"],
                },
                {
                    "name": "Whitney Houston",
                    "songs": [
                        "I Will Always Love You",
                        "I Wanna Dance with Somebody",
                        "Greatest Love of All",
                    ],
                },
            ]
        )
        print("Database initialized successfully with singers and songs.")
    else:
        print("Database already initialized.")


if __name__ == "__main__":
    initialize_database()
