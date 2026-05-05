from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-btn")

    def navigate(self):
        self.page.goto("http://localhost:8000/docs")

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

class ProductPage:
    def __init__(self, page: Page):
        self.page = page
        self.product_list = page.locator(".product-item")

    def get_product_count(self):
        return self.product_list.count()
