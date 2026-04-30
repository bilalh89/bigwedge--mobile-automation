import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import (
    TEST_EMAIL,
    TEST_PASSWORD,
    DEVICE_ID,
    APP_PACKAGE,
    APP_ACTIVITY,
    APPIUM_URL,
)
import time
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.action_chains import ActionChains


def native_tap(driver, element):
    """Helper to perform a native W3C coordinate tap on an element's center"""
    location = element.location
    size = element.size
    center_x = location["x"] + (size["width"] / 2)
    center_y = location["y"] + (size["height"] / 2)

    finger = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=finger)
    actions.pointer_action.move_to_location(center_x, center_y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)
    actions.pointer_action.pointer_up()
    actions.perform()
    time.sleep(1)


def native_type(driver, element, text):
    """Helper to tap an element to focus it, then send keys via W3C action chains"""
    native_tap(driver, element)
    ActionChains(driver).send_keys(text).perform()
    time.sleep(1)


@pytest.fixture(scope="function")
def fresh_driver():
    """Fresh driver for each test - starts from scratch"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.udid = DEVICE_ID
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.no_reset = True
    options.auto_grant_permissions = True
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    options.set_capability("appium:skipDeviceInitialization", True)

    driver = webdriver.Remote(command_executor=APPIUM_URL, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


class TestLoginFlow:

    def test_full_login_flow(self, fresh_driver):
        """
        Complete flow:
        1. App launches on landing screen
        2. Click Continue with Email
        3. Enter email and password
        4. Click Login
        5. Verify home screen loads
        """
        driver = fresh_driver
        wait = WebDriverWait(driver, 15)

        # ── Step 1: Verify landing screen loaded ──
        print("\n:iphone: Step 1: Checking landing screen...")
        continue_btn = wait.until(
            EC.presence_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, "CONTINUE WITH EMAIL")
            )
        )
        assert continue_btn.is_displayed(), ":x: Landing screen not showing!"
        print(":white_check_mark: Landing screen loaded!")

        # ── Step 2: Click Continue with Email ──
        print(":iphone: Step 2: Clicking Continue with Email...")
        continue_btn.click()
        time.sleep(3)
        print(":white_check_mark: Navigated to login screen!")

        # ── Step 3: Verify login screen loaded ──
        print(":iphone: Step 3: Verifying login screen...")
        email_field = wait.until(
            EC.presence_of_element_located(
                (AppiumBy.XPATH, "(//android.widget.EditText)[1]")
            )
        )
        assert email_field.is_displayed(), ":x: Login screen not showing!"
        print(":white_check_mark: Login screen loaded!")

        # ── Step 4: Enter Email ──
        print(f":iphone: Step 4: Entering email: {TEST_EMAIL}")
        email_field.click()
        email_field.clear()
        email_field.send_keys(TEST_EMAIL)

        # Dismiss keyboard
        try:
            driver.hide_keyboard()
        except:
            pass
        print(":white_check_mark: Email entered!")

        # ── Step 5: Enter Password ──
        print(":iphone: Step 5: Entering password...")
        password_field = wait.until(
            EC.visibility_of_element_located(
                (AppiumBy.XPATH, "(//android.widget.EditText)[2]")
            )
        )
        password_field.click()
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)

        try:
            driver.hide_keyboard()
        except:
            pass
        print(":white_check_mark: Password entered!")

        # ── Step 6: Click Login ──
        print(":iphone: Step 6: Clicking Login button...")
        login_btn = wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, '//android.widget.Button[@content-desc="LOGIN"]')
            )
        )
        native_tap(driver, login_btn)
        time.sleep(6)
        print(":white_check_mark: Login button clicked!")

        # ── Step 7: Verify Home Screen ──
        print(":iphone: Step 7: Verifying home screen...")

        # Check page source to confirm login screen views are gone
        page_source = driver.page_source

        assert (
            "LOGIN" not in page_source
        ), ":x: Login button still visible in page layout! Login failed silently."

        print(":white_check_mark: Successfully logged in and reached home screen!")
        print(":tada: FULL LOGIN FLOW PASSED!")
