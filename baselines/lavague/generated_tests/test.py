
import pytest
from pytest_bdd import scenarios, given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Constants
BASE_URL = 'https://www.saucedemo.com/v1/inventory.html'

# Scenarios
scenarios('test.feature')

# Fixtures
@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

# Steps
@given('I am on the product page')
def i_am_on_the_product_page(browser: webdriver.Chrome):
    browser.get(BASE_URL)
@when('I click a product to view details')
def i_click_a_product_to_view_details(browser: webdriver.Chrome):
    element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div[2]/div/div[2]/div/div/div/a/img'))
    )
    browser.execute_script('arguments[0].click();', element)

@when('I add the product to the shopping cart')
def i_add_the_product_to_the_shopping_cart(browser: webdriver.Chrome):
    element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div[2]/div/div/div/button'))
    )
    browser.execute_script('arguments[0].click();', element)

@then('the product count on the shopping cart icon should increase')
def the_product_count_on_the_shopping_cart_icon_should_increase(browser: webdriver.Chrome):
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Assuming the expected product count is provided as a fixture or variable
    expected_product_count = 2  # Example expected count
    
    shopping_cart_badge_element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='fa-layers-counter shopping_cart_badge']"))
    )
    actual_product_count = int(shopping_cart_badge_element.text.strip())
    assert actual_product_count == expected_product_count
