import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestDebug:

    def test_dump_page_source_after_google_click(self, driver):
        """Dump screen source after clicking Google button to find real element IDs"""
        wait = WebDriverWait(driver, 15)
        time.sleep(2)

        # Click Google Sign In
        google_btn = driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "SIGN IN WITH GOOGLE"
        )
        google_btn.click()
        print("✅ Google button clicked!")
        time.sleep(6)  # wait for popup to fully appear

        # ── Dump full page source so we can see what Google is showing ──────
        page_source = driver.page_source
        print("\n" + "="*60)
        print("PAGE SOURCE AFTER GOOGLE CLICK:")
        print("="*60)
        print(page_source)
        print("="*60 + "\n")

        # ── Also print all visible text on screen ────────────────────────────
        try:
            all_elements = driver.find_elements(AppiumBy.XPATH, '//*[@text!=""]')
            print("VISIBLE TEXT ELEMENTS ON SCREEN:")
            for el in all_elements:
                txt  = el.get_attribute("text")
                rid  = el.get_attribute("resource-id")
                cls  = el.get_attribute("class")
                print(f"  text='{txt}'  resource-id='{rid}'  class='{cls}'")
        except Exception as e:
            print(f"Could not list elements: {e}")

        assert True  # always pass — this is just for inspection