from pymongo import MongoClient

MONGO_URI = "mongodb+srv://cedric:gh336699@cluster0.onzmatc.mongodb.net/oneminews?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=false"

try:
    client = MongoClient(MONGO_URI)
    db = client["oneminews"]
    collections = db.list_collection_names()
    print("✅ Success! Connected to MongoDB.")
    print("📂 Collections:", collections)
except Exception as e:
    print("❌ Failed to connect to MongoDB:")
    print(e)