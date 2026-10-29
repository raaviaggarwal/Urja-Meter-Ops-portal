from fastapi.testclient import TestClient

from app import app, dataset


client = TestClient(app)


def _matches_requested_filters(record: dict, params: dict[str, str]) -> bool:
    hierarchy = record["hierarchy"]
    return (
        record["installStatus"] == params["status"]
        and record["phaseType"] == params["phase_type"]
        and record["build"] == params["build"]
        and hierarchy["zone"]["code"] == params["zone_code"]
        and hierarchy["division"]["code"] == params["division_code"]
        and record["dtCode"] == params["dt_code"]
        and (
            params.get("search", "").lower() in record["meterId"].lower()
            or params.get("search", "").lower()
            in record["serialNo"].lower()
        )
    )


def test_list_meters_combines_all_filters_and_search_with_and() -> None:
    sample = dataset[0]
    params = {
        "status": sample["installStatus"],
        "phase_type": sample["phaseType"],
        "build": sample["build"],
        "zone_code": sample["hierarchy"]["zone"]["code"],
        "division_code": sample["hierarchy"]["division"]["code"],
        "dt_code": sample["dtCode"],
    }

    expected_ids = {
        record["meterId"]
        for record in dataset
        if _matches_requested_filters(record, params)
    }
    response = client.get("/api/meters", params=params)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == len(expected_ids)
    assert {record["meterId"] for record in body["meters"]} == expected_ids

    search_params = {**params, "search": "SYNTH-"}
    expected_search_ids = {
        record["meterId"]
        for record in dataset
        if _matches_requested_filters(record, search_params)
    }
    search_response = client.get("/api/meters", params=search_params)

    assert search_response.status_code == 200
    search_body = search_response.json()
    assert search_body["total"] == len(expected_search_ids)
    assert {
        record["meterId"] for record in search_body["meters"]
    } == expected_search_ids
