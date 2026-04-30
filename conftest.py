import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import DEVICE_ID, APP_PACKAGE, APP_ACTIVITY, APPIUM_URL
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

@pytest.fixture(scope="session")
def driver():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.udid = DEVICE_ID
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    
    # --- CRITICAL FIXES FOR PHYSICAL DEVICES ---
    # Setting no_reset to True prevents the 'pm clear' command which causes the SecurityException
    options.no_reset = True 
    options.auto_grant_permissions = True

    # Force the app to launch fresh even with no_reset=True
    options.set_capability('appium:forceAppLaunch', True)
    options.set_capability('appium:shouldTerminateApp', True)
    
    # Fix for permission and hidden API errors
    options.set_capability('appium:ignoreHiddenApiPolicyError', True)
    options.set_capability('appium:noSign', True) # Prevents re-signing which can cause permission issues
    options.set_capability('appium:skipDeviceInitialization', False)
    options.set_capability('appium:skipServerInstallation', False)
    
    # Ensure the device stays awake during testing
    options.set_capability('appium:newCommandTimeout', 300)

    driver = webdriver.Remote(
        command_executor=APPIUM_URL,
        options=options
    )

    # Implicit wait for element stability
    driver.implicitly_wait(15)

    # Force the app to the foreground immediately after connection
    driver.activate_app(APP_PACKAGE)

    yield driver

    driver.quit()

def take_screenshot(driver, name):
    os.makedirs("screenshots", exist_ok=True)
    path = f"screenshots/{name}.png"
    driver.save_screenshot(path)
    print(f"📸 Screenshot saved: {path}")