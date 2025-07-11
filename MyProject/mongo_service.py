from pymongo import MongoClient

# Establish MongoDB connection
client = MongoClient("mongodb://emmanuel:K7154muhell@localhost:27017/?authSource=admin")

# Define database and collection
db = client["LearningSystem"]
learning_paths = db["learning_paths"]

def store_learning_path(user, path_list):
    # Remove existing path for user if exists 
    learning_paths.delete_many({"user_id": user.id})
    learning_paths.insert_one({
        "user_id": user.id,
        "recommended_path": path_list
    })

def get_learning_path(user):
    record = learning_paths.find_one({"user_id": user.id})
    if record:
        return record.get("recommended_path", [])
    return []
