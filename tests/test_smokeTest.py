import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5500"  # change if needed

class TestSmokeAdmin:
    def setup_method(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_method(self):
        self.driver.quit()

    def test_admin_login_error(self):
        # 1) open /admin.html
        self.driver.get(f"{BASE_URL}/admin.html")

        # 2) assert element present: css=input[name='username']
        user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))

        # 3–4) type wrong creds
        user.clear(); user.send_keys("wronguser")
        pw = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
        pw.clear(); pw.send_keys("wrongpass")

        # 5) click submit
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        # 6) assertTextPresent "Invalid" (case-insensitive, anywhere on page)
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(translate(., 'INVALID', 'invalid'), 'invalid')]")
            )
        )
