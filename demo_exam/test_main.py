from fastapi.testclient import TestClient
from .main import app
# from .main_solved import app, items
from pytest import fixture

client = TestClient(app)

test_items = [
    {
        "id": 1,
        "title": "Book 1",
        "description": "Book 1 description",
        "category": "Book",
        "price": 100.0,
        "discount": None,
        "quantity": 10
    },
    {
        "id": 2,
        "title": "Book 2",
        "description": "Book 2 description",
        "category": "Book",
        "price": 200.0,
        "discount": 10.0,
        "quantity": 5
    },
    {
        "id": 3,
        "title": "Magazine 1",
        "description": "Magazine 1 description",
        "category": "Magazine",
        "price": 300.0,
        "discount": None,
        "quantity": 20
    }
]


@fixture()
def create_items():
    for item in test_items:
        response = client.post("/items", json=item)
        assert response.status_code == 200
        assert response.json() == item
    
    yield

    items = client.get("/items").json()
    for item in items:
        response = client.delete(f"/items/{item['id']}")
        assert response.status_code == 200
    
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_get_items_1():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []
    
    
def test_get_items_2(create_items):
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == test_items

def test_get_item(create_items):
    response = client.get("/items/100")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == test_items[0]

def test_create_item(create_items):
    response = client.post("/items", json=test_items[0])
    response_dict = response.json()
    response_dict.pop("id", None)
    test_item = test_items[0].copy()
    test_item.pop("id", None)
    assert response.status_code == 200
    assert response_dict == test_item


def test_update_item(create_items):
    
    test_item = {
        "id": 1,
        "title": "Book 1 upd",
        "description": "Book 1 description",
        "category": "Book upd",
        "price": 110.0,
        "discount": 5.0,
        "quantity": 1
    }

    response = client.put(f"/items/{test_item['id']}", json=test_item)
    assert response.status_code == 200
    assert response.json() == test_item


def test_delete_item(create_items):
    response = client.delete("/items/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Item deleted"}

    response = client.get("/items/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_filter_items(create_items):
    response = client.get("/items/filter/")
    assert response.status_code == 200
    assert response.json() == test_items

    response = client.get("/items/filter/?title=Book")
    assert response.status_code == 200
    assert response.json() == test_items[:2]

    response = client.get("/items/filter/?category=Book")
    assert response.status_code == 200
    assert response.json() == test_items[:2]

    response = client.get("/items/filter/?price_from=150")
    assert response.status_code == 200
    assert response.json() == test_items[1:]

    response = client.get("/items/filter/?price_to=250")
    assert response.status_code == 200
    assert response.json() == test_items[:2]

    response = client.get("/items/filter/?discount_from=5")
    assert response.status_code == 200
    assert response.json() == [test_items[1]]

    response = client.get("/items/filter/?discount_to=8")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/items/filter/?quantity_from=10")
    assert response.status_code == 200
    assert response.json() == test_items[::2]

    response = client.get("/items/filter/?quantity_to=10")
    assert response.status_code == 200
    assert response.json() == test_items[:2]

    response = client.get("/items/filter/?title=Book&category=Book")
    assert response.status_code == 200
    assert response.json() == test_items[:2]

    response = client.get("/items/filter/?price_from=150&price_to=250")
    assert response.status_code == 200
    assert response.json() == [test_items[1]]

    response = client.get("/items/filter/?discount_from=5&discount_to=8")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/items/filter/?quantity_from=10&quantity_to=10")
    assert response.status_code == 200
    assert response.json() == [test_items[0]]

    response = client.get("/items/filter/?title=Book&category=Book&price_from=150&price_to=250&discount_from=5&discount_to=8&quantity_from=10&quantity_to=10")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/items/filter/?category=book&category=some")
    assert response.status_code == 200
    assert response.json() == test_items[:2]

    response = client.get("/items/filter/?category=book&category=MAGAZINE")
    assert response.status_code == 200
    assert response.json() == test_items


def test_get_sale(create_items):
    response = client.put("/sale/?id=100")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

    response = client.put("/sale/?id=1")
    assert response.status_code == 200
    assert response.json()["message"] == "Item sold"
    assert response.json()["items"][0]["id"] == 1
    assert response.json()["items"][0]["quantity"] == test_items[0]["quantity"]-1


    response = client.put("/sale/?id=1&id=2")
    assert response.status_code == 200
    assert response.json()["message"] == "Item sold"
    assert response.json()["items"][0]["id"] == 1
    assert response.json()["items"][0]["quantity"] == test_items[0]["quantity"]-2
    assert response.json()["items"][1]["id"] == 2
    assert response.json()["items"][1]["quantity"] == test_items[1]["quantity"]-1

    new_item = test_items[0].copy()
    new_item["quantity"] = 0
    response = client.put("/items/1", json=new_item)
    assert response.status_code == 200
    assert response.json() == new_item

    response = client.put("/sale/?id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Insufficient stock", "items": [new_item]}

    response = client.put("/sale/?id=1&id=2")
    assert response.status_code == 200
    assert response.json() == {"message": "Insufficient stock", "items": [new_item]}


def test_increase_quantity(create_items):
    response = client.put("/increment/?id=100&quantity=10")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

    response = client.put("/increment/?id=100&quantity=10&id=1&quantity=5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

    response = client.put("/increment/?id=1&quantity=10")
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["quantity"] == test_items[0]["quantity"]+10

    response = client.put("/increment/?id=1&quantity=10&id=2&quantity=5")
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["quantity"] == test_items[0]["quantity"]+20
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["quantity"] == test_items[1]["quantity"]+5