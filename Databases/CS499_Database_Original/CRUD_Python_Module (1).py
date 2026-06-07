from pymongo import MongoClient, errors
from bson.objectid import ObjectId

class AnimalShelter(object):
    """CRUD operations for Animal collection in MongoDB"""

    def __init__(
        self,
        username="aacuser",
        password="password",
        host="localhost",
        port=27017,
        db_name="aac",
        collection_name="animals",
    ):
        """Initialize MongoDB client and connect to database."""

        try:
            uri = "mongodb://{0}:{1}@{2}:{3}/{4}?authSource=admin".format(
                username, password, host, port, db_name
            )
            self.client = MongoClient(uri)
            self.database = self.client[db_name]
            self.collection = self.database[collection_name]
        except errors.PyMongoError as e:
            raise Exception("Failed to connect to MongoDB: {0}".format(e))

    def create(self, data):
        """Insert a new document. Return True if successful, False otherwise."""

        if data is None or not isinstance(data, dict):
            raise Exception("Invalid data. Must be a dictionary.")

        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
        except errors.PyMongoError as e:
            print("Create failed:", e)
            return False

    def read(self, query):
        """Return list of matching documents."""

        if query is None:
            query = {}

        if not isinstance(query, dict):
            raise Exception("Query must be a dictionary.")

        try:
            cursor = self.collection.find(query)
            return list(cursor)
        except errors.PyMongoError as e:
            print("Read failed:", e)
            return []

    def update(self, query, fields, many=False):
        """
        Update one or many documents.
        query: filter dictionary
        fields: dictionary of fields to update
        many: whether to update many docs (default False)
        Return: number of modified documents
        """

        if not isinstance(query, dict) or not isinstance(fields, dict):
            raise Exception("Query and update must be dictionaries.")

        try:
            update_data = {"$set": fields}
            if many:
                result = self.collection.update_many(query, update_data)
            else:
                result = self.collection.update_one(query, update_data)

            return result.modified_count
        except errors.PyMongoError as e:
            print("Update failed:", e)
            return 0

    def delete(self, query, many=False):
        """
        Delete one or many documents.
        query: filter dictionary
        many: whether to delete many docs (default False)
        Return: number of removed documents
        """

        if not isinstance(query, dict):
            raise Exception("Query must be a dictionary.")

        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
            return result.deleted_count
        except errors.PyMongoError as e:
            print("Delete failed:", e)
            return 0
