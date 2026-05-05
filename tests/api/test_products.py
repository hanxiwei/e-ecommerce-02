import pytest
import allure
import uuid

@allure.feature("Product API")
@allure.story("Product Management")
@pytest.mark.regression
class TestProductAPI:

    @allure.title("Create Product Parameterized Tests")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("name, desc, price, stock, category, expected_status", [
        ("Test Product 1", "A great product", 99.99, 100, 1, 200),
        ("Test Product 2", "Another product", 49.50, 50, 2, 200),
    ])
    def test_create_product(self, api_client, name, desc, price, stock, category, expected_status):
        """测试创建商品"""
        params = {
            "name": f"{name}_{str(uuid.uuid4())[:4]}",
            "description": desc,
            "price": price,
            "stock": stock,
            "category": category,
            "image_url": "http://example.com/image.jpg"
        }

        response = api_client.post("/products/", params=params)
        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json()["name"] == params["name"]
            assert response.json()["price"] == price

    @allure.title("Get All Products")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_all_products(self, api_client):
        """测试获取所有商品列表"""
        response = api_client.get("/products/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @allure.title("Get Single Product By ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_single_product(self, api_client):
        """测试根据 ID 获取单个商品"""
        params = {
            "name": f"Query Product {str(uuid.uuid4())[:4]}",
            "description": "To be queried",
            "price": 10.0,
            "stock": 5,
            "category": 1,
            "image_url": "http://example.com/query.jpg"
        }
        create_res = api_client.post("/products/", params=params)
        assert create_res.status_code == 200
        product_id = create_res.json()["id"]

        get_res = api_client.get(f"/products/{product_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == product_id
        assert get_res.json()["name"] == params["name"]

    @allure.title("Update Product By ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_product(self, api_client):
        """测试更新商品信息"""
        params = {
            "name": f"Update Product {str(uuid.uuid4())[:4]}",
            "description": "Before update",
            "price": 10.0,
            "stock": 5,
            "category": 1,
            "image_url": "http://example.com/query.jpg"
        }
        create_res = api_client.post("/products/", params=params)
        product_id = create_res.json()["id"]

        update_params = {
            "description": "After update",
            "price": 25.5
        }
        update_res = api_client.put(f"/products/{product_id}", params=update_params)
        assert update_res.status_code == 200
        assert update_res.json()["description"] == "After update"
        assert update_res.json()["price"] == 25.5
