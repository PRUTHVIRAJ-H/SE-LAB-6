
import pytest

from pet_walking_service import (
    process_walking_routes,
    inspect_gps_collars
)


# --------------------------------------------------
# PROCESS WALKING ROUTES TESTS
# --------------------------------------------------

def test_single_standard_30_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": False,
        "walks": [{
            "num_pets": 1,
            "aggression_alert": False,
            "needs_meds": False
        }]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result == {
        "total_revenue": 27.0,
        "status": "COMPLETED"
    }


def test_all_session_types():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [{"num_pets": 1}]
        },
        {
            "route_confirmed": True,
            "session_type": "standard_60",
            "walks": [{"num_pets": 1}]
        },
        {
            "route_confirmed": True,
            "session_type": "express_15",
            "walks": [{"num_pets": 1}]
        }
    ]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 86.0
    assert result["status"] == "COMPLETED"


def test_weekend_and_medication():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": True,
        "walks": [{
            "num_pets": 2,
            "aggression_alert": False,
            "needs_meds": True
        }]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 43.0
    assert result["status"] == "COMPLETED"


def test_more_than_three_pets():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{"num_pets": 4}]
    }]

    result = process_walking_routes(routes, 5.0)

    expected = round((22 + 4 * 8) * 0.90, 2)

    assert result["total_revenue"] == expected
    assert result["status"] == "COMPLETED"


def test_unconfirmed_route():
    routes = [{
        "route_confirmed": False,
        "session_type": "standard_30",
        "walks": [{"num_pets": 1}]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


def test_invalid_session_type():
    routes = [{
        "route_confirmed": True,
        "session_type": "unknown",
        "walks": [{"num_pets": 1}]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


def test_zero_pets():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{"num_pets": 0}]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_standard_60_break():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_60",
        "walks": [{
            "num_pets": 2,
            "aggression_alert": True
        }]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_standard_30():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{
            "num_pets": 2,
            "aggression_alert": True
        }]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


def test_incident_audit():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "bad_type",
            "walks": [{"num_pets": 1}]
        }
        for _ in range(5)
    ]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "INCIDENT_AUDIT"


def test_invalid_input():
    with pytest.raises(ValueError):
        process_walking_routes("invalid", 5.0)

    with pytest.raises(ValueError):
        process_walking_routes([], -1)


# --------------------------------------------------
# ADDITIONAL ROUTE EDGE CASES
# --------------------------------------------------

def test_exactly_four_incidents():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "bad_type"
        }
        for _ in range(4)
    ]

    result = process_walking_routes(routes, 5.0)

    assert result["status"] == "ZERO_EARNINGS"


def test_negative_pet_count():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{"num_pets": -1}]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["status"] == "ZERO_EARNINGS"


def test_missing_optional_fields():
    routes = [{
        "route_confirmed": True,
        "walks": [{"num_pets": 1}]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 27.0
    assert result["status"] == "COMPLETED"


def test_weekend_without_walks():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": True,
        "walks": []
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 5.0
    assert result["status"] == "COMPLETED"


def test_aggression_with_medication():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{
            "num_pets": 2,
            "aggression_alert": True,
            "needs_meds": True
        }]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 6.0
    assert result["status"] == "COMPLETED"


def test_large_group_with_medication():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "walks": [{
            "num_pets": 4,
            "aggression_alert": False,
            "needs_meds": True
        }]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 48.6
    assert result["status"] == "COMPLETED"


def test_standard_60_aggression_after_first_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_60",
        "walks": [
            {"num_pets": 1},
            {"num_pets": 2, "aggression_alert": True},
            {"num_pets": 1}
        ]
    }]

    result = process_walking_routes(routes, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


# --------------------------------------------------
# GPS COLLAR TESTS
# --------------------------------------------------

def test_gps_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


def test_gps_lost_signal():
    collars = [[50, 15, 10]]

    assert inspect_gps_collars(collars) == "LOST_SIGNAL_ALERT"


def test_gps_signal_recovery():
    collars = [[15, 50, 15, 50]]

    assert inspect_gps_collars(collars) == "ONLINE"


def test_gps_normal():
    collars = [[80, 75, 90, 60]]

    assert inspect_gps_collars(collars) == "ONLINE"


def test_gps_single_weak_signal():
    collars = [[15, 50, 60]]

    assert inspect_gps_collars(collars) == "ONLINE"


def test_gps_two_consecutive_weak_signals():
    collars = [[50, 19, 19, 80]]

    assert inspect_gps_collars(collars) == "LOST_SIGNAL_ALERT"


def test_gps_streak_reset():
    collars = [[15, 50, 15, 60, 15]]

    assert inspect_gps_collars(collars) == "ONLINE"


def test_gps_multiple_collars():
    collars = [
        [15, 50, 15],
        [80, 75, 90]
    ]

    assert inspect_gps_collars(collars) == "ONLINE"


def test_gps_empty_collar():
    collars = [[]]

    assert inspect_gps_collars(collars) == "ONLINE"


def test_gps_threshold_boundary():
    collars = [[20, 19, 20, 19]]

    assert inspect_gps_collars(collars) == "ONLINE"
