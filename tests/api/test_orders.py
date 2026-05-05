import pytest
import allure

@allure.feature("Order API")
@allure.story("Order Processing & Management")
@pytest.mark.regression
class TestOrderAPI:

    @allure.title("Create Order Parameterized Tests")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("status, total, expected_status", [
        ("pending", 99.99, 200),
        ("shipped", 150.00, 200),
    ])
    def test_create_order(self, api_client, auth_headers, status, total, expected_status):
        """测试创建订单"""
        me_res = api_client.get("/auth/users/me", headers=auth_headers)
        assert me_res.status_code == 200
        user_id = me_res.json()["id"]

        params = {
            "user_id": user_id,
            "status": status,
            "total": total,
            "shipping_address": "456 Order Ave"
        }
        
        response = api_client.post("/orders", params=params)
        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json()["status"] == status
            assert response.json()["total"] == total
            assert response.json()["user_id"] == user_id

    @allure.title("Get All Orders")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_all_orders(self, api_client):
        """测试获取所有订单列表"""
        response = api_client.get("/orders")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @allure.title("Get Single Order By ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_single_order(self, api_client, auth_headers):
        """测试根据 ID 获取单个订单"""
        me_res = api_client.get("/auth/users/me", headers=auth_headers)
        user_id = me_res.json()["id"]

        params = {
            "user_id": user_id,
            "status": "pending",
            "total": 50.0,
            "shipping_address": "Query Addr"
        }
        create_res = api_client.post("/orders", params=params)
        order_id = create_res.json()["id"]

        get_res = api_client.get(f"/orders/{order_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == order_id
        assert get_res.json()["status"] == "pending"

    @allure.title("Update Order By ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_order(self, api_client, auth_headers):
        """测试更新订单状态和金额"""
        me_res = api_client.get("/auth/users/me", headers=auth_headers)
        user_id = me_res.json()["id"]

        params = {
            "user_id": user_id,
            "status": "pending",
            "total": 100.0,
            "shipping_address": "Update Addr"
        }
        create_res = api_client.post("/orders", params=params)
        order_id = create_res.json()["id"]

        update_params = {
            "status": "delivered",
            "total": 85.0
        }
        update_res = api_client.put(f"/orders/{order_id}", params=update_params)
        assert update_res.status_code == 200
        assert update_res.json()["status"] == "delivered"
        assert update_res.json()["total"] == 85.0
