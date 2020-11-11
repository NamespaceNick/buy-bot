#!/usr/bin/env python3
# My program to purchase a specific item on a website
import os
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from dotenv import load_dotenv

import pickle

load_dotenv()
PICKUP_BUTTON_NAME = "orderPickupButton"
CART_URL = os.getenv("CART_URL")
PRODUCT_URL = os.getenv("PRODUCT_URL")
COOKIE_FILE = os.getenv("COOKIEFILE")
username = os.getenv("USERNAME")
passwd = os.getenv("PASSWD")


# Saves session cookie
def save_cookie(driver, path):
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


# Loads session cookie from file
def load_cookie(driver, path):
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


# For debugging purposes. Pauses execution until arbitrary input is sent
def wait_here():
    prompt = input("Waiting here.\n")


# Acquires web element from website with the given value for the
# "data-test" attribute
def acquire_target_button(data_test_value):
    button_present = presence_of_element_located(
        (By.XPATH, f"//*[@data-test='{data_test_value}']")
    )
    WebDriverWait(driver, 10).until(button_present)
    button_to_return = driver.find_element_by_xpath(
        f"//*[@data-test='{data_test_value}']"
    )
    return button_to_return


# Handles login popup for website
# DEPRECATED - Now loading session cookies
def handle_login_popup(driver):
    username_field_element = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element_by_id("username")
    )
    passwd_field_element = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element_by_id("password")
    )
    login_button_element = WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element_by_id("login")
    )

    username_field_element.clear()
    username_field_element.send_keys(username)

    passwd_field_element.clear()
    passwd_field_element.send_keys(passwd)

    login_button_element.click()


# Start browser with default login info
start_time = time.time()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
# Initialize window on right side of screen
# driver.set_window_position(1280, 0)
driver.get(PRODUCT_URL)

try:
    load_cookie(driver, COOKIE_FILE)
    # Find the pickup button
    pickup_button = acquire_target_button(PICKUP_BUTTON_NAME)

    pickup_button.click()

    # Go to cart
    driver.get(CART_URL)

    # TODO: Checkout
    checkout_button = acquire_target_button("checkout-button")
    checkout_button.click()

    # Order item
    # place_order_button = acquire_target_button("placeOrderButton")
    # place_order_button.click()
    # wait_here()

except:
    driver.close()
    raise

end_time = time.time()
print(f"Time elapsed: {end_time - start_time}")
driver.close()
