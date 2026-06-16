"""Automated tests for the enhanced AnimalShelter database module."""

import mongomock
import pytest

from animal_shelter import AnimalShelter


@pytest.fixture
def shelter() -> AnimalShelter:
    """Create an AnimalShelter object backed by a temporary test collection."""

    test_client = mongomock.MongoClient()
    test_shelter = AnimalShelter.__new__(AnimalShelter)
    test_shelter.client = test_client
    test_shelter.database = test_client["aac"]
    test_shelter.collection = test_shelter.database["animals"]

    test_shelter.collection.insert_many(
        [
            {
                "animal_id": "A100",
                "animal_type": "Dog",
                "breed": "Labrador Retriever Mix",
                "sex_upon_outcome": "Intact Female",
                "age_upon_outcome_in_weeks": 52,
            },
            {
                "animal_id": "A101",
                "animal_type": "Dog",
                "breed": "Labrador Retriever Mix",
                "sex_upon_outcome": "Intact Female",
                "age_upon_outcome_in_weeks": 80,
            },
            {
                "animal_id": "A102",
                "animal_type": "Dog",
                "breed": "German Shepherd",
                "sex_upon_outcome": "Intact Male",
                "age_upon_outcome_in_weeks": 60,
            },
            {
                "animal_id": "A103",
                "animal_type": "Cat",
                "breed": "Domestic Shorthair Mix",
                "sex_upon_outcome": "Spayed Female",
                "age_upon_outcome_in_weeks": 40,
            },
        ]
    )

    return test_shelter


def test_water_rescue_query_contains_expected_requirements() -> None:
    """Confirm that the water rescue filter targets qualified dogs."""

    query = AnimalShelter._build_rescue_query("Water Rescue")

    assert query["animal_type"] == "Dog"
    assert "Labrador Retriever Mix" in query["breed"]["$in"]
    assert query["sex_upon_outcome"] == "Intact Female"
    assert query["age_upon_outcome_in_weeks"] == {"$gte": 26, "$lte": 156}


def test_all_selection_returns_open_query() -> None:
    """Confirm that the All selection allows all records to be retrieved."""

    query = AnimalShelter._build_rescue_query("All")

    assert query == {}


def test_invalid_rescue_type_raises_error() -> None:
    """Confirm that an unsupported filter value is rejected."""

    with pytest.raises(ValueError):
        AnimalShelter._build_rescue_query("Unknown Rescue Type")


def test_create_adds_new_animal_record(shelter: AnimalShelter) -> None:
    """Confirm that a new animal record can be inserted."""

    new_record = {
        "animal_id": "A104",
        "animal_type": "Dog",
        "breed": "Newfoundland Mix",
        "sex_upon_outcome": "Intact Female",
        "age_upon_outcome_in_weeks": 70,
    }

    assert shelter.create(new_record) is True
    assert shelter.collection.count_documents({"animal_id": "A104"}) == 1


def test_read_retrieves_matching_animals(shelter: AnimalShelter) -> None:
    """Confirm that records can be retrieved by query."""

    results = shelter.read({"animal_type": "Cat"})

    assert len(results) == 1
    assert results[0]["animal_id"] == "A103"


def test_update_modifies_selected_record(shelter: AnimalShelter) -> None:
    """Confirm that one selected animal record can be updated."""

    modified_count = shelter.update(
        {"animal_id": "A102"},
        {"breed": "German Shepherd Mix"},
    )

    updated_record = shelter.read({"animal_id": "A102"})[0]

    assert modified_count == 1
    assert updated_record["breed"] == "German Shepherd Mix"


def test_delete_removes_selected_record(shelter: AnimalShelter) -> None:
    """Confirm that one selected animal record can be deleted."""

    deleted_count = shelter.delete({"animal_id": "A103"})

    assert deleted_count == 1
    assert shelter.read({"animal_id": "A103"}) == []


def test_find_rescue_candidates_returns_water_rescue_matches(
    shelter: AnimalShelter,
) -> None:
    """Confirm that water rescue selection retrieves qualified candidates."""

    results = shelter.find_rescue_candidates("Water Rescue")

    assert len(results) == 2
    assert all(record["breed"] == "Labrador Retriever Mix" for record in results)


def test_breed_summary_aggregates_matching_candidates(
    shelter: AnimalShelter,
) -> None:
    """Confirm that breed reporting summarizes rescue candidates."""

    results = shelter.breed_summary("Water Rescue")

    assert results == [{"count": 2, "_id": "Labrador Retriever Mix"}]


def test_empty_update_query_is_blocked(shelter: AnimalShelter) -> None:
    """Confirm that an update cannot accidentally affect all records."""

    with pytest.raises(ValueError):
        shelter.update({}, {"breed": "Labrador Retriever Mix"}, many=True)


def test_empty_delete_query_is_blocked(shelter: AnimalShelter) -> None:
    """Confirm that a delete cannot accidentally remove all records."""

    with pytest.raises(ValueError):
        shelter.delete({}, many=True)


def test_empty_create_record_is_blocked(shelter: AnimalShelter) -> None:
    """Confirm that an empty animal record cannot be inserted."""

    with pytest.raises(ValueError):
        shelter.create({})
