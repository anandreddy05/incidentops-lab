import uuid


def create_customer_token(client, email="customer@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Test Customer",
            "password": "CustomerPassword123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "CustomerPassword123!",
        },
    )

    return response.json()["access_token"]


def create_product(client, admin_token, stock_quantity=10):
    return client.post(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Gaming Laptop",
            "description": "High-performance gaming laptop",
            "sku": "LAPTOP-001",
            "price": "74999.99",
            "stock_quantity": stock_quantity,
            "category": "Electronics",
        },
    )


def test_unauthenticated_user_cannot_access_cart(client):
    response = client.get("/api/v1/cart")

    assert response.status_code == 401


def test_get_empty_cart(client):
    token = create_customer_token(client)

    response = client.get(
        "/api/v1/cart",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total_items"] == 0
    assert response.json()["total_price"] == "0.00"


def test_add_product_to_cart(client, admin_token):
    admin = admin_token()
    product_response = create_product(client, admin)

    product_id = product_response.json()["id"]
    token = create_customer_token(client)

    response = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "quantity": 2,
        },
    )

    assert response.status_code == 200
    assert response.json()["total_items"] == 2
    assert response.json()["total_price"] == "149999.98"
    assert len(response.json()["items"]) == 1


def test_adding_same_product_increases_quantity(client, admin_token):
    admin = admin_token()
    product_response = create_product(client, admin)

    product_id = product_response.json()["id"]
    token = create_customer_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    first_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product_id, "quantity": 2},
    )

    second_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product_id, "quantity": 3},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["total_items"] == 5
    assert len(second_response.json()["items"]) == 1
    assert second_response.json()["items"][0]["quantity"] == 5


def test_adding_product_with_insufficient_stock(client, admin_token):
    admin = admin_token()
    product_response = create_product(client, admin, stock_quantity=3)

    product_id = product_response.json()["id"]
    token = create_customer_token(client)

    response = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "quantity": 5,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Requested quantity exceeds available stock"


def test_update_cart_item_quantity(client, admin_token):
    admin = admin_token()
    product_response = create_product(client, admin)

    product_id = product_response.json()["id"]
    token = create_customer_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    add_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product_id, "quantity": 2},
    )

    item_id = add_response.json()["items"][0]["id"]

    response = client.patch(
        f"/api/v1/cart/items/{item_id}",
        headers=headers,
        json={"quantity": 4},
    )

    assert response.status_code == 200
    assert response.json()["total_items"] == 4
    assert response.json()["items"][0]["quantity"] == 4


def test_remove_cart_item(client, admin_token):
    admin = admin_token()
    product_response = create_product(client, admin)

    product_id = product_response.json()["id"]
    token = create_customer_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    add_response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product_id, "quantity": 2},
    )

    item_id = add_response.json()["items"][0]["id"]

    response = client.delete(
        f"/api/v1/cart/items/{item_id}",
        headers=headers,
    )

    assert response.status_code == 204

    cart_response = client.get("/api/v1/cart", headers=headers)

    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []
    assert cart_response.json()["total_items"] == 0


def test_user_cannot_modify_another_users_cart_item(client, admin_token):
    admin = admin_token()
    product_response = create_product(client, admin)

    product_id = product_response.json()["id"]

    first_token = create_customer_token(
        client,
        "first@example.com",
    )
    second_token = create_customer_token(
        client,
        "second@example.com",
    )

    first_response = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"product_id": product_id, "quantity": 2},
    )

    item_id = first_response.json()["items"][0]["id"]

    update_response = client.patch(
        f"/api/v1/cart/items/{item_id}",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"quantity": 5},
    )

    delete_response = client.delete(
        f"/api/v1/cart/items/{item_id}",
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert update_response.status_code == 404
    assert delete_response.status_code == 404


def test_cart_rejects_nonexistent_product(client):
    token = create_customer_token(client)

    response = client.post(
        "/api/v1/cart/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": str(uuid.uuid4()),
            "quantity": 1,
        },
    )

    assert response.status_code == 404
