import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost:5500")

class TestSmokeAdmin:
    def setup_method(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1280,900")
        self.driver = webdriver.Chrome(options=opts)
        self.wait = WebDriverWait(self.driver, 12)

    def teardown_method(self):
        self.driver.quit()

    def test_admin_login_error(self):
        self.driver.get(f"{BASE_URL}/admin.html")
        user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))
        user.clear(); user.send_keys("wronguser")
        pw = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
        pw.clear(); pw.send_keys("wrongpass")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(translate(., 'INVALID', 'invalid'), 'invalid')]")
        ))
