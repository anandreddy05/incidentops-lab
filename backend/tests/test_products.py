
def create_product(client, token, sku="LAPTOP-001"):
    return client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Gaming Laptop",
            "description": "High-performance gaming laptop",
            "sku": sku,
            "price": "74999.99",
            "stock_quantity": 10,
            "category": "Electronics",
        },
    )


def create_customer_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "customer@example.com",
            "full_name": "Test Customer",
            "password": "CustomerPassword123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "customer@example.com",
            "password": "CustomerPassword123!",
        },
    )

    return response.json()["access_token"]


def test_list_products_publicly(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_create_product_as_admin(client, admin_token):
    token = admin_token()

    response = create_product(client, token)

    assert response.status_code == 201
    assert response.json()["name"] == "Gaming Laptop"
    assert response.json()["sku"] == "LAPTOP-001"
    assert response.json()["price"] == "74999.99"
    assert response.json()["stock_quantity"] == 10


def test_customer_cannot_create_product(client):
    token = create_customer_token(client)

    response = create_product(client, token)

    assert response.status_code == 403


def test_unauthenticated_user_cannot_create_product(client):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Gaming Laptop",
            "sku": "LAPTOP-001",
            "price": "74999.99",
            "stock_quantity": 10,
            "category": "Electronics",
        },
    )

    assert response.status_code == 401


def test_create_product_with_duplicate_sku(client, admin_token):
    token = admin_token()

    first_response = create_product(client, token)
    second_response = create_product(client, token)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_get_product_by_id(client, admin_token):
    token = admin_token()
    create_response = create_product(client, token)

    product_id = create_response.json()["id"]

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_get_nonexistent_product(client):
    import uuid

    response = client.get(f"/api/v1/products/{uuid.uuid4()}")

    assert response.status_code == 404


def test_update_product_as_admin(client, admin_token):
    token = admin_token()
    create_response = create_product(client, token)

    product_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"price": "69999.99", "stock_quantity": 5},
    )

    assert response.status_code == 200
    assert response.json()["price"] == "69999.99"
    assert response.json()["stock_quantity"] == 5


def test_customer_cannot_update_product(client, admin_token):
    admin = admin_token()
    create_response = create_product(client, admin)

    product_id = create_response.json()["id"]
    customer = create_customer_token(client)

    response = client.patch(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {customer}"},
        json={"price": "100.00"},
    )

    assert response.status_code == 403


def test_invalid_product_price(client, admin_token):
    token = admin_token()

    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Gaming Laptop",
            "sku": "LAPTOP-002",
            "price": "-100.00",
            "stock_quantity": 10,
            "category": "Electronics",
        },
    )

    assert response.status_code == 422


def test_invalid_product_stock(client, admin_token):
    token = admin_token()

    response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Gaming Laptop",
            "sku": "LAPTOP-003",
            "price": "74999.99",
            "stock_quantity": -5,
            "category": "Electronics",
        },
    )

    assert response.status_code == 422


def test_product_search_and_pagination(client, admin_token):
    token = admin_token()

    create_product(client, token, "LAPTOP-001")

    second_response = client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Wireless Mouse",
            "sku": "MOUSE-001",
            "price": "1499.00",
            "stock_quantity": 20,
            "category": "Accessories",
        },
    )
    assert second_response.status_code == 201

    search_response = client.get(
        "/api/v1/products",
        params={"search": "laptop"},
    )

    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1
    assert search_response.json()["items"][0]["name"] == "Gaming Laptop"

    pagination_response = client.get(
        "/api/v1/products",
        params={"skip": 0, "limit": 1},
    )

    assert pagination_response.status_code == 200
    assert len(pagination_response.json()["items"]) == 1
    assert pagination_response.json()["total"] == 2
