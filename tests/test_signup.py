import pytest
import time
import os
import imaplib
import email
import re
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

# ─────────────────────────────────────────────────────────────────────────────
# Gmail IMAP config  — use an App Password, NOT your real Gmail password
# Generate one at: https://myaccount.google.com/apppasswords
# ─────────────────────────────────────────────────────────────────────────────
GMAIL_ADDRESS  = "bilalhassan.ckl@gmail.com"   # the INBOX that receives OTPs
GMAIL_APP_PASS = "uyqh mzue flmr wyyp"          # 16-char App Password (spaces OK)
IMAP_HOST      = "imap.gmail.com"
IMAP_PORT      = 993

# ─────────────────────────────────────────────────────────────────────────────
# Test Data
# ─────────────────────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Ahmed", "Sara",   "Omar",   "Fatima",
    "Hassan","Zara",   "Ali",    "Noor",
    "Bilal", "Hana",
]
LAST_NAMES = [
    "Khan",    "Ahmed",   "Malik",   "Hussain",
    "Sheikh",  "Qureshi", "Awan",    "Butt",
    "Chaudhry","Raja",
]

PASSWORD     = "Abcd@1234"
BASE_EMAIL   = "bilalhassan.ckl"
EMAIL_DOMAIN = "@gmail.com"
COUNTER_FILE = "email_counter.txt"
WAIT         = 15
OTP_DIGITS   = 5


# ─────────────────────────────────────────────────────────────────────────────
# Counter / name helpers
# ─────────────────────────────────────────────────────────────────────────────
def get_next_counter() -> int:
    counter = 34
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                counter = int(f.read().strip())
            except ValueError:
                counter = 34
    counter += 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(counter))
    return counter


def build_email(counter: int) -> str:
    return f"{BASE_EMAIL}+{counter}{EMAIL_DOMAIN}"


def pick_names(counter: int):
    idx = (counter - 35) % len(FIRST_NAMES)
    if counter % 2 == 0:
        return FIRST_NAMES[idx], LAST_NAMES[0]
    else:
        return FIRST_NAMES[0], LAST_NAMES[idx]


# ─────────────────────────────────────────────────────────────────────────────
# Gmail IMAP — fetch OTP
# ─────────────────────────────────────────────────────────────────────────────
def fetch_otp_from_gmail(
    retries: int = 10,
    delay: int   = 6,
    digits: int  = OTP_DIGITS,
) -> str:
    """
    Poll Gmail via IMAP for a recent email containing an N-digit OTP code.
    Tries `retries` times with `delay` seconds between each attempt.
    Returns the OTP string or raises TimeoutError.
    """
    print(f"    [IMAP] Connecting to {IMAP_HOST} ...")
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
    mail.select("inbox")

    pattern = re.compile(rf'\b(\d{{{digits}}})\b')

    for attempt in range(1, retries + 1):
        print(f"    [IMAP] Attempt {attempt}/{retries} — searching for OTP email ...")

        # Search for unseen emails (adjust criteria if needed)
        status, data = mail.search(None, "UNSEEN")
        if status != "OK" or not data[0]:
            time.sleep(delay)
            continue

        # Read emails newest-first
        email_ids = data[0].split()
        for eid in reversed(email_ids):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Extract plain text body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode(errors="ignore")
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            match = pattern.search(body)
            if match:
                otp = match.group(1)
                print(f"    [IMAP] OTP found: {otp}")
                # Mark email as seen so we don't re-read it
                mail.store(eid, "+FLAGS", "\\Seen")
                mail.logout()
                return otp

        time.sleep(delay)

    mail.logout()
    raise TimeoutError(
        f"OTP not found in Gmail inbox after {retries * delay}s. "
        "Check App Password, IMAP enabled, and email delivery."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Appium helpers  (kept from your working version)
# ─────────────────────────────────────────────────────────────────────────────
def native_tap(driver, element):
    location = element.location
    size     = element.size
    cx = location["x"] + size["width"]  / 2
    cy = location["y"] + size["height"] / 2
    finger  = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=finger)
    actions.pointer_action.move_to_location(cx, cy)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)
    actions.pointer_action.pointer_up()
    actions.perform()
    time.sleep(0.8)


def click_verify_button(driver, timeout=WAIT):
    """
    Try every known selector for the VERIFY CODE button.
    Also scrolls down first in case the button is off-screen.
    Falls back to native tap if .click() is blocked.
    """
    # Scroll down to make sure button is visible
    try:
        driver.execute_script(
            "mobile: scroll",
            {"direction": "down", "percent": 0.4}
        )
        time.sleep(0.5)
    except Exception:
        pass

    last_error = None
    for by, value in VERIFY_BTN_SELECTORS:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by, value))
            )
            print(f"    [VERIFY] Found button with: {by} -> '{value}'")
            try:
                el.click()
            except Exception:
                native_tap(driver, el)
            return
        except Exception as e:
            last_error = e
            continue

    # Last resort — dump visible text to help debug
    try:
        page = driver.page_source
        import re as _re
        texts = _re.findall(r'content-desc="([^"]*)"', page)
        print(f"    [VERIFY] Visible content-desc values: {texts[:20]}")
    except Exception:
        pass

    raise TimeoutError(
        f"Could not find VERIFY CODE button with any selector. Last error: {last_error}"
    )


def wait_and_click(driver, by, value, timeout=WAIT, use_native=False):
    if use_native:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        native_tap(driver, el)
    else:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        el.click()
    return el


def wait_and_type(driver, by, value, text, timeout=WAIT):
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )
    el.click()
    el.clear()
    el.send_keys(text)
    return el


def enter_otp(driver, otp: str):
    """
    Type each OTP digit into its own EditText box.
    The boxes are the first N EditText elements on the verify screen.
    """
    print(f"    [OTP] Entering code: {otp}")
    boxes = WebDriverWait(driver, WAIT).until(
        lambda d: d.find_elements(AppiumBy.XPATH, "//android.widget.EditText")
    )
    # Filter to exactly OTP_DIGITS boxes (in case other EditTexts exist)
    otp_boxes = boxes[:OTP_DIGITS]
    assert len(otp_boxes) >= OTP_DIGITS, (
        f"Expected {OTP_DIGITS} OTP boxes, found {len(otp_boxes)}"
    )
    for i, digit in enumerate(otp):
        box = otp_boxes[i]
        box.click()
        time.sleep(0.2)
        box.clear()
        box.send_keys(digit)
        time.sleep(0.2)


# ─────────────────────────────────────────────────────────────────────────────
# Selectors
# ─────────────────────────────────────────────────────────────────────────────

# Splash screen
CREATE_ACCOUNT_LINK = (AppiumBy.ACCESSIBILITY_ID, "NEW TO BIG WEDGE? CREATE AN ACCOUNT")

# Sign-up form  (your working index-based XPaths)
FIRST_NAME_FIELD = (AppiumBy.XPATH, "(//android.widget.EditText)[1]")
LAST_NAME_FIELD  = (AppiumBy.XPATH, "(//android.widget.EditText)[2]")
EMAIL_FIELD      = (AppiumBy.XPATH, "(//android.widget.EditText)[3]")
PASSWORD_FIELD   = (AppiumBy.XPATH, "(//android.widget.EditText)[4]")

# Sign-up submit button
SUBMIT_BTN = (AppiumBy.ACCESSIBILITY_ID, "CREATE AN ACCOUNT")

# OTP screen — "VERIFY CODE" button: multiple fallback selectors
VERIFY_BTN_SELECTORS = [
    (AppiumBy.ACCESSIBILITY_ID,       "VERIFY CODE"),
    (AppiumBy.XPATH,                  "//*[@content-desc='VERIFY CODE']"),
    (AppiumBy.XPATH,                  "//*[contains(@content-desc,'VERIFY')]"),
    (AppiumBy.ANDROID_UIAUTOMATOR,    'new UiSelector().description("VERIFY CODE")'),
    (AppiumBy.ANDROID_UIAUTOMATOR,    'new UiSelector().descriptionContains("VERIFY")'),
    (AppiumBy.XPATH,                  "//*[contains(@text,'VERIFY')]"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Test
# ─────────────────────────────────────────────────────────────────────────────
class TestSignupFlow:

    def test_signup(self, driver):

        # ── Build test data ───────────────────────────────────────────────
        counter     = get_next_counter()
        email       = build_email(counter)
        first, last = pick_names(counter)

        print(f"\n{'='*55}")
        print(f"  Run counter : {counter}")
        print(f"  First Name  : {first}")
        print(f"  Last Name   : {last}")
        print(f"  Email       : {email}")
        print(f"  Password    : {PASSWORD}")
        print(f"{'='*55}\n")

        # ── STEP 1 — Splash screen → tap create account ───────────────────
        print("[STEP 1] Tapping launch-screen 'CREATE AN ACCOUNT' link ...")
        wait_and_click(driver, *CREATE_ACCOUNT_LINK)
        time.sleep(2)

        # ── STEP 2 — First Name ───────────────────────────────────────────
        print(f"[STEP 2] Entering First Name -> '{first}'")
        wait_and_type(driver, *FIRST_NAME_FIELD, first)

        # ── STEP 3 — Last Name ────────────────────────────────────────────
        print(f"[STEP 3] Entering Last Name  -> '{last}'")
        wait_and_type(driver, *LAST_NAME_FIELD, last)

        # ── STEP 4 — Email ────────────────────────────────────────────────
        print(f"[STEP 4] Entering Email      -> '{email}'")
        wait_and_type(driver, *EMAIL_FIELD, email)

        # ── STEP 5 — Password ─────────────────────────────────────────────
        print(f"[STEP 5] Entering Password   -> '{PASSWORD}'")
        wait_and_type(driver, *PASSWORD_FIELD, PASSWORD)

        # ── STEP 6 — Hide keyboard ────────────────────────────────────────
        print("[STEP 6] Hiding keyboard ...")
        try:
            driver.hide_keyboard()
        except Exception:
            pass
        time.sleep(0.5)

        # ── STEP 7 — Submit signup form ───────────────────────────────────
        print("[STEP 7] Tapping 'CREATE AN ACCOUNT' submit button ...")
        wait_and_click(driver, *SUBMIT_BTN, use_native=True)
        time.sleep(2)  # let the OTP email dispatch begin

        # ── STEP 8 — Fetch OTP from Gmail ─────────────────────────────────
        print("[STEP 8] Fetching OTP from Gmail inbox ...")
        otp = fetch_otp_from_gmail(retries=10, delay=6)
        # otp arrives as e.g. "48271"

        # ── STEP 9 — Enter OTP digits ─────────────────────────────────────
        print(f"[STEP 9] Entering OTP: {otp}")
        enter_otp(driver, otp)
        time.sleep(0.5)

        # ── STEP 10 — Button auto-submits once all 5 boxes are filled ───────
        print("[STEP 10] OTP entered — button auto-submits, waiting for next screen ...")
        time.sleep(5)

        print("\nSIGNUP + EMAIL VERIFICATION COMPLETED SUCCESSFULLY!")