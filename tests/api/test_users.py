import pytest
import allure

@allure.feature("User API")
@allure.story("Authentication & Registration")
@pytest.mark.regression
class TestUserAPI:
    
    @allure.title("User Registration Parameterized Tests")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("scenario, email_prefix, username_prefix, password, expected_status", [
        ("Valid registration", "valid", "valid", "securePwd123", 200),
        ("Duplicate email", "dup", "user1", "securePwd123", 400), # 假设之前已经存在
    ])
    def test_register_user(self, api_client, case_id, scenario, email_prefix, username_prefix, password, expected_status):
        """测试用户注册的多种场景"""
        email = f"{email_prefix}_{case_id}@example.com"
        username = f"{username_prefix}_{case_id}"
        phone = f"138{case_id}0"
        
        user_data = {
            "email": email,
            "username": username,
            "phone": phone,
            "address": "123 Test St",
            "password": password,
            "first_name": "Test",
            "last_name": "User",
            "type": "customer"
        }
        
        # 第一次注册
        response = api_client.post("/auth/register", json=user_data)
        if scenario == "Valid registration":
            assert response.status_code == 200
            assert response.json()["email"] == email
        elif scenario == "Duplicate email":
            assert response.status_code == 200 # 第一次成功
            user_data["username"] = f"diff_user_{case_id}"
            user_data["phone"] = f"139{case_id}0"
            response2 = api_client.post("/auth/register", json=user_data)
            assert response2.status_code == 400

    @allure.title("User Login Parameterized Tests")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("username_type, password_type, expected_status", [
        ("valid", "valid", 200),
        ("invalid", "valid", 400),
        ("valid", "invalid", 400),
    ])
    def test_login(self, api_client, case_id, username_type, password_type, expected_status):
        """测试多种登录场景（用户名错误、密码错误等）"""
        valid_username = f"login_user_{case_id}"
        valid_password = "CorrectPassword1!"
        
        api_client.post("/auth/register", json={
            "email": f"{valid_username}@example.com",
            "username": valid_username,
            "phone": f"137{case_id}0",
            "address": "123 Test St",
            "password": valid_password,
            "first_name": "Test",
            "last_name": "User",
            "type": "customer"
        })

        test_username = valid_username if username_type == "valid" else f"wrong_{case_id}"
        test_password = valid_password if password_type == "valid" else "WrongPassword1!"
        
        login_data = {"username": test_username, "password": test_password}
        response = api_client.post("/auth/token", data=login_data)
        
        assert response.status_code == expected_status
        if expected_status == 200:
            assert "access_token" in response.json()

    @allure.title("Get Current User Info (/users/me)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_users_me(self, api_client, auth_headers):
        """测试获取当前登录用户信息"""
        response = api_client.get("/auth/users/me", headers=auth_headers)
        assert response.status_code == 200
        assert "username" in response.json()
        assert "email" in response.json()

    @allure.title("List all users (/auth/)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_all_users(self, api_client):
        """测试获取用户列表接口"""
        response = api_client.get("/auth/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
