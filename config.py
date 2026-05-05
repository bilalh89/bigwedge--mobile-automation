# Test Account
TEST_EMAIL = "fahad@gitwork.co.uk"
TEST_PASSWORD = "Password123!!"
WRONG_PASSWORD = "WrongPass@999"
INVALID_EMAIL = "notanemail"

# Device & App
# DEVICE_ID = "2857ada0"
# APP_PACKAGE = "com.bigwedgegolf.app"
# APP_ACTIVITY = "com.bigwedgegolf.app.MainActivity"
# APPIUM_URL = "http://127.0.0.1:4723"

DEVICE_ID = "2857ada0"
APPIUM_URL = "http://127.0.0.1:4723"

ACTIVE_APP = "bigwedge_staging"

APPS = {
    "bigwedge": {
        "package": "com.bigwedgegolf.app",
        "activity": "com.bigwedgegolf.app.MainActivity",
    },
    "bigwedge_staging": {
        "package": "com.bigwedgegolf.app.staging",
        "activity": "com.bigwedgegolf.app.MainActivity",
    },
}

APP_PACKAGE = APPS[ACTIVE_APP]["package"]
APP_ACTIVITY = APPS[ACTIVE_APP]["activity"]
