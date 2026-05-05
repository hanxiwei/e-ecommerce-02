import pytest
from playwright.sync_api import sync_playwright, expect
from tests.ui.pages.base_page import LoginPage, ProductPage

pytestmark = pytest.mark.ui

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context()
    context.add_init_script("window.localStorage.setItem('auth_token', 'your-test-token')")
    page = context.new_page()
    yield page
    context.close()

def test_api_docs_elements_visible(page):
    """UI 自动化：验证 API 文档页关键元素可见"""
    login_page = LoginPage(page)
    login_page.navigate()
    
    # 使用最可靠的页面标题断言
    expect(page).to_have_title("E-Commerce API - Swagger UI")
    expect(page.locator("#operations-tag-Users")).to_be_visible()
    expect(page.locator("#operations-tag-Products")).to_be_visible()

def test_product_page_interaction(page):
    """UI 自动化：模拟与产品页面的交互"""
    product_page = ProductPage(page)
    # 假设跳转到产品列表页
    # page.goto("http://localhost:3000/products") 
    # 
    # # 断言页面上至少有一个产品
    # expect(product_page.product_list).to_have_count.greater_than(0)
    pass # 实际需要前端页面支持
