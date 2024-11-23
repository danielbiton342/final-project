from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
import os

app = Flask(__name__)


# Configure CORS properly
# CORS(
#    app,
#    resources={
#        r"/*": {
#            "origins": [
#                "http://localhost:3000",  # For local development
#                f"http://localhost:30000",  # For NodePort local access
#                f"http://{os.getenv('NODE_IP', '*')}:30000",  # For NodePort production access
#            ],
#            "methods": ["GET", "POST", "PUT", "DELETE"],
#            "allow_headers": ["Content-Type"],
#        }
#    },
# )

# Configure MongoDB URI
mongo_uri = os.environ.get(
    "MONGO_URI",
    "mongodb://MONGO_USER:MONGO_PASSWORD@my-mongodb.mongodb.svc.cluster.local:27017/musicDB",
)
app.config["MONGO_URI"] = mongo_uri

# Initialize MongoDB with error handling
try:
    mongo = PyMongo(app)
    # Test the connection
    mongo.db.command("ping")
    print("Connected successfully to MongoDB")
except Exception as e:
    print(f"Failed to connect to MongoDB: {str(e)}")
    raise e


# Add request logging
@app.before_request
def log_request_info():
    print(f"Request Method: {request.method}")
    print(f"Request URL: {request.url}")
    print(f"Request Headers: {dict(request.headers)}")
    if request.get_json(silent=True):
        print(f"Request Body: {request.get_json()}")


@app.after_request
def log_response_info(response):
    print(f"Response Status: {response.status}")
    print(f"Response Headers: {dict(response.headers)}")
    return response


# Rest of your routes remain the same...
# Collections
singers_collection = mongo.db.singers


def convert_objectid(doc):
    """Convert ObjectId to string for JSON serialization"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route("/singers", methods=["POST"])
def add_singer():
    data = request.get_json()
    name = data.get("name")
    songs = data.get("songs", [])
    if not name:
        return jsonify({"error": "Name is required"}), 400

    singer_id = singers_collection.insert_one(
        {"name": name, "songs": songs}
    ).inserted_id
    return jsonify({"message": "Singer added", "id": str(singer_id)})


@app.route("/singers", methods=["GET"])
def get_singers():
    singers = []
    for singer in singers_collection.find():
        singer_dict = convert_objectid(singer)
        singers.append(singer_dict)
    return jsonify(singers)


@app.route("/singers/<id>", methods=["GET"])
def get_singer(id):
    try:
        singer = singers_collection.find_one({"_id": ObjectId(id)})
        if not singer:
            return jsonify({"error": "Singer not found"}), 404
        singer = convert_objectid(singer)
        return jsonify(singer)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/singers/<id>/songs", methods=["GET"])
def get_singer_songs(id):
    try:
        singer = singers_collection.find_one({"_id": ObjectId(id)})
        if not singer:
            return jsonify({"error": "Singer not found"}), 404
        return jsonify(singer["songs"])
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/singers/<id>/name", methods=["PUT"])
def update_singer_name(id):
    try:
        data = request.get_json()
        name = data.get("name")
        if not name:
            return jsonify({"error": "Name is required"}), 400

        result = singers_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": {"name": name}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Singer not found"}), 404

        return jsonify({"message": "Singer name updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/singers/<id>", methods=["PUT"])
def update_singer(id):
    try:
        data = request.get_json()
        new_songs = data.get("songs")

        if not new_songs:
            return jsonify({"error": "Songs are required"}), 400

        # Update the existing singer's songs by appending new songs to the current list
        result = singers_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$addToSet": {"songs": {"$each": new_songs}}
            },  # Use $addToSet to avoid duplicates
        )

        if result.matched_count == 0:
            return jsonify({"error": "Singer not found"}), 404

        return jsonify({"message": "Singer updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/singers/<id>", methods=["DELETE"])
def delete_singer(id):
    try:
        result = singers_collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            return jsonify({"error": "Singer not found"}), 404

        return jsonify({"message": "Singer deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/singers/<singer_id>/songs/<song_name>", methods=["DELETE"])
def delete_song(singer_id, song_name):
    try:
        result = singers_collection.update_one(
            {"_id": ObjectId(singer_id)},
            {"$pull": {"songs": song_name}},  # Remove the specified song
        )

        if result.matched_count == 0:
            return jsonify({"error": "Singer not found"}), 404

        if result.modified_count == 0:
            return jsonify({"error": "Song not found in singer's list"}), 404

        return jsonify({"message": "Song deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Run in debug mode for development
