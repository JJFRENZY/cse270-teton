import os, pathlib
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Let port/origin be overridden without editing code
BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost:5500")

ARTIFACTS = pathlib.Path("tests/_artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)

def save_artifacts(driver, name):
    (ARTIFACTS / f"{name}.png").write_bytes(driver.get_screenshot_as_png())
    (ARTIFACTS / f"{name}.html").write_text(driver.page_source, encoding="utf-8")

class TestSmokeAdmin:
    def setup_method(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 12)

    def teardown_method(self):
        self.driver.quit()

    def _open_admin(self):
        # Try /admin.html then /admin/ (folder with index.html)
        for suffix in ("/admin.html", "/admin/"):
            url = f"{BASE_URL}{suffix}"
            self.driver.get(url)
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))
                return url
            except TimeoutException:
                continue
        save_artifacts(self.driver, "admin_not_found")
        pytest.fail("Admin page not reachable at /admin.html or /admin/.")

    def test_admin_login_error(self):
        self._open_admin()

        # username
        user = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[name='username'], #username")
        ))
        user.clear(); user.send_keys("wronguser")

        # password
        pw = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[name='password'], #password, input[type='password']")
        ))
        pw.clear(); pw.send_keys("wrongpass")

        # submit (button or input)
        submit = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
        ))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'})", submit)
        submit.click()

        # error text anywhere (your app shows: "Invalid username and password.")
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[contains(normalize-space(.), 'Invalid username and password')] | "
                           "//*[contains(translate(., 'INVALID', 'invalid'), 'invalid')]")
            ))
        except TimeoutException:
            save_artifacts(self.driver, "admin_after_submit")
            raise
