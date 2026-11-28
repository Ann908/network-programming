import pytest
from werkzeug.exceptions import BadRequest

from lab3_v2 import Products, User, app, db, get_product, initialized_db, verify_password


@pytest.mark.parametrize("username", ["Nick", "Tom"])
def test_user_repr_returns_username(username):
    user = User(username=username)
    assert repr(user) == username


@pytest.mark.parametrize(
    "product_id, cost, weight, color",
    [(1, 100, 70, "blue"), (2, 0, 0, "green")],
)
def test_product_to_dict(product_id, cost, weight, color):
    product = Products(id=product_id, cost=cost, weight=weight, color=color)

    assert product.to_dict() == {
        "id": product_id,
        "cost": cost,
        "weight": weight,
        "color": color,
    }


def test_get_product_accepts_valid_data():
    payload = {"cost": 100, "weight": 70, "color": "blue"}

    with app.test_request_context("/items", method="POST", json=payload):
        assert get_product() == payload


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"cost": 100, "weight": 70},
        {"cost": -1, "weight": 70, "color": "blue"},
        {"cost": 100, "weight": -1, "color": "blue"},
        {"cost": 100, "weight": 70, "color": "   "},
    ],
)
def test_get_product_rejects_invalid_data(payload):
    with app.test_request_context("/items", method="POST", json=payload):
        with pytest.raises(BadRequest):
            get_product()

@pytest.fixture
def empty_db():
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

    try:
        yield
    finally:
        with app.app_context():
            db.session.remove()
            db.drop_all()


@pytest.fixture
def client(empty_db):
    with app.app_context():
        db.drop_all()

    initialized_db()
    return app.test_client()


@pytest.mark.parametrize(
    "username, password, expected_username",
    [
        ("Nick", "python", "Nick"),
        ("Nick", "wrong-password", None),
        ("Unknown", "python", None),
    ],
)
def test_verify_password(client, username, password, expected_username):
    with app.app_context():
        user = verify_password(username, password)

        if expected_username is None:
            assert user is None
        else:
            assert user.username == expected_username


def test_task_products_get(client):
    response = client.get("/items", auth=("Nick", "python"))

    assert response.status_code == 200
    assert [product["id"] for product in response.get_json()["products"]] == [1, 2, 3]


def test_task_products_post(client):
    response = client.post(
        "/items",
        auth=("Nick", "python"),
        json={"cost": 120, "weight": 50, "color": " red "},
    )

    assert response.status_code == 201
    product = response.get_json()["product"]
    assert product["cost"] == 120
    assert product["weight"] == 50
    assert product["color"] == "red"

AUTH = ("Nick", "python")


def test_initialized_db_creates_initial_records(client):
    with app.app_context():
        users = db.session.scalars(db.select(User.username)).all()
        product_ids = db.session.scalars(db.select(Products.id)).all()

    assert sorted(users) == ["John", "Nick", "Tom"]
    assert sorted(product_ids) == [1, 2, 3]


def test_initialized_db_does_not_duplicate_initial_records(client):
    initialized_db()

    with app.app_context():
        users = db.session.scalars(db.select(User.username)).all()
        product_ids = db.session.scalars(db.select(Products.id)).all()

    assert sorted(users) == ["John", "Nick", "Tom"]
    assert sorted(product_ids) == [1, 2, 3]


def test_get_product_by_id(client):
    response = client.get("/items/1", auth=AUTH)

    assert response.status_code == 200
    assert response.get_json() == {
        "product": {"id": 1, "cost": 100, "weight": 70, "color": "blue"}
    }


@pytest.mark.parametrize(
    "url, id_in_body",
    [
        ("/items", {"id": 1}),
        ("/items/1", {}),
    ],
)
def test_update_product_with_valid_data(client, url, id_in_body):
    fields = {"cost": 150, "weight": 80, "color": "red"}

    response = client.put(url, auth=AUTH, json={**id_in_body, **fields})

    assert response.status_code == 200
    assert response.get_json() == {"product": {"id": 1, **fields}}
    saved = client.get("/items/1", auth=AUTH)
    assert saved.status_code == 200
    assert saved.get_json() == response.get_json()


@pytest.mark.parametrize(
    "url, request_options, expected_message",
    [
        ("/items", {"json": {"id": 1}}, "Product deleted"),
        ("/items/1", {}, "Product is deleted"),
    ],
)
def test_delete_existing_product(client, url, request_options, expected_message):
    response = client.delete(url, auth=AUTH, **request_options)

    assert response.status_code == 200
    assert response.get_json() == {"message": expected_message}
    assert client.get("/items/1", auth=AUTH).status_code == 404


@pytest.mark.parametrize(
    "method, url, payload",
    [
        ("POST", "/items", {"cost": 100, "color": "blue"}),
        ("PUT", "/items", {"id": "1", "cost": 100, "weight": 70, "color": "blue"}),
        ("PUT", "/items/1", {"cost": -10, "weight": 70, "color": "blue"}),
    ],
)
def test_product_request_rejects_invalid_data(client, method, url, payload):
    response = client.open(url, method=method, auth=AUTH, json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Bad request"}


@pytest.mark.parametrize(
    "method, url, request_options",
    [
        ("GET", "/items/999", {}),
        ("DELETE", "/items", {"json": {"id": 999}}),
    ],
)
def test_request_for_missing_product_returns_404(client, method, url, request_options):
    response = client.open(url, method=method, auth=AUTH, **request_options)

    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}


@pytest.mark.parametrize(
    "request_options",
    [
        {},
        {"auth": ("Nick", "wrong-password")},
    ],
    ids=["no-credentials", "wrong-password"],
)
def test_items_rejects_request_without_valid_credentials(client, request_options):
    response = client.get("/items", **request_options)

    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized access"}

def test_health():
    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

@pytest.mark.parametrize(
    "query, expected_status, expected_body",
    [
        ("", 400, {"error": "Немає значень"}),
        (
            "v=4",
            200,
            {"count": 1, "mean": 4.0, "min": 4.0, "max": 4.0, "variance": 0.0},
        ),
        (
            "v=2&v=4",
            200,
            {"count": 2, "mean": 3.0, "min": 2.0, "max": 4.0, "variance": 2.0},
        ),
    ],
)
def test_stats(query, expected_status, expected_body):
    response = app.test_client().get("/api/stats", query_string=query)

    assert response.status_code == expected_status
    assert response.get_json() == expected_body

#For run in the terminal
#$env:PRODUCTS_DATABASE_URI = "sqlite:///:memory:"
#python -m pytest test_lab3_v2.py --cov=lab3_v2 --cov-report=term-missing --cov-report=html --cov-fail-under=85