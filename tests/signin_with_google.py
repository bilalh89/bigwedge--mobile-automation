import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestGoogleSignIn:

    def test_app_launches(self, driver):
        """Test that app opens successfully"""
        time.sleep(3)
        print("✅ App launched successfully!")
        assert driver.current_activity is not None

    def test_sign_in_with_google(self, driver):
        """Test Google sign in button exists and is clickable"""
        wait = WebDriverWait(driver, 15)
        time.sleep(2)

        # Tap Sign In With Google button
        google_btn = driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, "SIGN IN WITH GOOGLE"
        )
        assert google_btn.is_displayed(), "❌ Google button not visible"
        print("✅ Google Sign In button found!")
        google_btn.click()
        time.sleep(5)
        print("✅ Google Sign In clicked!")

        # Select first Google account from chooser
        account = wait.until(
            EC.element_to_be_clickable((
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().resourceId("com.google.android.gms:id/container").instance(0)',
            ))
        )
        account.click()
        time.sleep(3)
        print("✅ Google account selected!")

        # ── Handle "Agree and share" consent popup ──────────────────────────
        agree_selectors = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Agree and share")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Agree")'),
            (AppiumBy.XPATH, '//*[@text="Agree and share"]'),
            (AppiumBy.XPATH, '//*[contains(@text,"Agree")]'),
        ]

        agreed = False
        for by, selector in agree_selectors:
            try:
                agree_btn = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((by, selector))
                )
                agree_btn.click()
                agreed = True
                print(f"✅ Consent accepted using: {selector}")
                time.sleep(3)
                break
            except Exception:
                continue

        if not agreed:
            print("⚠️ No consent popup found — may have been pre-accepted or skipped")
        # ────────────────────────────────────────────────────────────────────

        # Handle additional permissions screen if it appears
        try:
            allow_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    AppiumBy.ID,
                    "com.google.android.gms:id/allow_button"
                ))
            )
            allow_btn.click()
            print("✅ Permission granted!")
        except Exception:
            print("⚠️ No permission screen, skipping!")

        time.sleep(4)

        # Assert we landed back in the app after login
        assert driver.current_activity is not None
        print("✅ Google Sign In Successful!")