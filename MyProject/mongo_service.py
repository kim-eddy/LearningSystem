from pymongo import MongoClient

client = MongoClient("mongodb://emmanuel:K7154muhell@localhost:27017/?authSource=admin")

db = client["LearningSystem"]
learning_paths = db["learning_paths"]

def store_learning_path(student_id, path_list):
    learning_paths.insert_one({
        "student_id": student_id,
        "recommended_path": path_list
    })

def get_learning_path(student_id):
    return learning_paths.find_one({"student_id": student_id})
