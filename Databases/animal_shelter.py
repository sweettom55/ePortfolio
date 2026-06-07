"""Enhanced MongoDB access module for the Grazioso Salvare dashboard."""

import os
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient, errors


load_dotenv()


class AnimalShelter:
    """Provide secure and validated database operations for animal records."""

    def __init__(self) -> None:
        """Create and verify the MongoDB database connection."""

        database_name = os.getenv("MONGO_DB_NAME", "aac")
        collection_name = os.getenv("MONGO_COLLECTION_NAME", "animals")
        mongo_uri = os.getenv("MONGO_URI")

        if not mongo_uri:
            username = os.getenv("MONGO_USERNAME")
            password = os.getenv("MONGO_PASSWORD")
            host = os.getenv("MONGO_HOST", "localhost")
            port = os.getenv("MONGO_PORT", "27017")

            if not username or not password:
                raise ValueError(
                    "Database credentials are missing. Configure the environment variables before running the application."
                )

            mongo_uri = (
                f"mongodb://{username}:{password}@{host}:{port}/"
                f"{database_name}?authSource=admin"
            )

        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
        except errors.PyMongoError as exc:
            raise ConnectionError(
                "The application could not connect to the MongoDB database."
            ) from exc

    @staticmethod
    def _validate_dictionary(value: Any, value_name: str) -> None:
        """Confirm that a database argument is a dictionary."""

        if not isinstance(value, dict):
            raise TypeError(f"{value_name} must be provided as a dictionary.")

    @staticmethod
    def _protect_against_empty_query(query: dict[str, Any], action: str) -> None:
        """Prevent accidental updates or deletes involving the full collection."""

        if not query:
            raise ValueError(
                f"{action} requires a specific query to protect the full collection."
            )

    def create(self, data: dict[str, Any]) -> bool:
        """Insert a new animal record and report whether the insert succeeded."""

        self._validate_dictionary(data, "Data")

        if not data:
            raise ValueError("Data cannot be empty when creating a record.")

        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
        except errors.PyMongoError as exc:
            raise RuntimeError("The animal record could not be created.") from exc

    def read(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Retrieve animal records matching the supplied query."""

        if query is None:
            query = {}

        self._validate_dictionary(query, "Query")

        try:
            return list(self.collection.find(query))
        except errors.PyMongoError as exc:
            raise RuntimeError("Animal records could not be retrieved.") from exc

    def update(
        self,
        query: dict[str, Any],
        fields: dict[str, Any],
        many: bool = False,
    ) -> int:
        """Update matching records and return the number of modified records."""

        self._validate_dictionary(query, "Query")
        self._validate_dictionary(fields, "Fields")
        self._protect_against_empty_query(query, "An update")

        if not fields:
            raise ValueError("Update fields cannot be empty.")

        try:
            update_values = {"$set": fields}

            if many:
                result = self.collection.update_many(query, update_values)
            else:
                result = self.collection.update_one(query, update_values)

            return result.modified_count
        except errors.PyMongoError as exc:
            raise RuntimeError("Animal records could not be updated.") from exc

    def delete(self, query: dict[str, Any], many: bool = False) -> int:
        """Delete matching records and return the number of deleted records."""

        self._validate_dictionary(query, "Query")
        self._protect_against_empty_query(query, "A delete")

        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)

            return result.deleted_count
        except errors.PyMongoError as exc:
            raise RuntimeError("Animal records could not be deleted.") from exc

    @staticmethod
    def _build_rescue_query(rescue_type: str) -> dict[str, Any]:
        """Return the database query associated with a rescue category."""

        rescue_queries = {
            "Water Rescue": {
                "animal_type": "Dog",
                "breed": {
                    "$in": [
                        "Labrador Retriever Mix",
                        "Chesapeake Bay Retriever Mix",
                        "Newfoundland Mix",
                    ]
                },
                "sex_upon_outcome": "Intact Female",
                "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
            },
            "Mountain or Wilderness Rescue": {
                "animal_type": "Dog",
                "breed": {
                    "$in": [
                        "German Shepherd",
                        "Alaskan Malamute",
                        "Old English Sheepdog",
                        "Siberian Husky",
                        "Rottweiler",
                    ]
                },
                "sex_upon_outcome": "Intact Male",
                "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
            },
            "Disaster or Individual Tracking": {
                "animal_type": "Dog",
                "breed": {
                    "$in": [
                        "Doberman Pinscher",
                        "German Shepherd",
                        "Golden Retriever",
                        "Bloodhound",
                        "Rottweiler",
                    ]
                },
                "sex_upon_outcome": {"$in": ["Intact Male", "Intact Female"]},
                "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
            },
        }

        if rescue_type == "All":
            return {}

        if rescue_type not in rescue_queries:
            raise ValueError("The selected rescue type is not recognized.")

        return rescue_queries[rescue_type]

    def find_rescue_candidates(self, rescue_type: str) -> list[dict[str, Any]]:
        """Retrieve animal records suitable for the selected rescue category."""

        query = self._build_rescue_query(rescue_type)
        return self.read(query)

    def breed_summary(self, rescue_type: str) -> list[dict[str, Any]]:
        """Summarize the number of matching rescue candidates by breed."""

        query = self._build_rescue_query(rescue_type)

        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
            {"$sort": {"count": -1, "_id": 1}},
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except errors.PyMongoError as exc:
            raise RuntimeError("The breed summary could not be generated.") from exc

    def close(self) -> None:
        """Close the active MongoDB client connection."""

        self.client.close()