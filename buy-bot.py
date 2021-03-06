#!/usr/bin/env python3
# My program to purchase a specific item on a website
import os
import sys
import time
import datetime
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException

from dotenv import load_dotenv

import pickle
import ezgmail

load_dotenv()
LOGFILE = os.getenv("LOGFILE")
PICKUP_BUTTON_NAME = "orderPickupButton"
CART_URL = os.getenv("CART_URL")
PRODUCT_URL = os.getenv("PRODUCT_URL")
COOKIE_FILE = os.getenv("COOKIEFILE")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")
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


# Logs error in logfile
def log(message):
    with open(LOGFILE, "a") as logfile:
        logfile.write(f"{message}\n\n\n")


# For debugging purposes. Pauses execution until arbitrary input is sent
def wait_here():
    prompt = input("Waiting here.\n")


# Acquires web element from website with the given value for the
# "data-test" attribute
def acquire_target_button(data_test_value):
    button_present = presence_of_element_located(
        (By.XPATH, f"//*[@data-test='{data_test_value}']")
    )
    try:
        WebDriverWait(driver, 10).until(button_present)
    except TimeoutException:
        return None
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


def initialize_driver(headless: bool = True):
    if headless:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        return webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome()
        driver.set_window_position(1280, 0)
        return driver


# Finds & presses the "Place Order" button on the webpage
def place_order():
    place_order_button = acquire_target_button("placeOrderButton")
    place_order_button.click()


# Start browser with default login info
driver = initialize_driver(headless=True)
# Initialize window on right side of screen
driver.get(PRODUCT_URL)

# Erase existing logfile
open(LOGFILE, "w").close()

try:
    # load_cookie(driver, COOKIE_FILE)
    # log("Cookie loaded")
    # Find the pickup button
    pickup_button = acquire_target_button(PICKUP_BUTTON_NAME)
    while pickup_button is None:
        driver.refresh()
        pickup_button = acquire_target_button(PICKUP_BUTTON_NAME)

    # Send message that item is available
    log(f"Item became available at {datetime.datetime.now().time()}")
    ezgmail.send(
        TARGET_EMAIL,
        "Item has become available!",
        "The item you have been waiting for has become available!",
    )

    # Add item to cart
    pickup_button.click()
    log("Clicked pickup button")

    # Go to cart
    driver.get(CART_URL)
    log("Navigated to cart")

    # Checkout
    checkout_button = acquire_target_button("checkout-button")
    checkout_button.click()
    log("Selected 'Checkout'")

    handle_login_popup(driver)
    log("Handled login popup")

    # TODO: Check to make sure there wasn't an error
    # Order item
    place_order()
    log("Order successfully placed. Yay!")

    # Send message to indicate successful purchase of item
    ezgmail.send(
        TARGET_EMAIL,
        "[SUCCESS] Item successfully purchased!",
        "The item you were waiting for has been purchased for you!",
    )
    # wait_here()

except:
    log(f"===AN ERROR OCCURRED===\n\n{traceback.format_exc()}")
    ezgmail.send(
        TARGET_EMAIL,
        "[FAILURE] Item purchase failed",
        "An error occured during script execution. Your purchase most likely failed",
    )
    driver.close()
    raise

driver.close()
