# tests/test_smokeTest.py
import sys
import time
from urllib.parse import urljoin

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:5500/"
# If your site lives under a subfolder (e.g., teton/1.6/),
# you can hardcode that here instead:
# BASE_URL = "http://127.0.0.1:5500/teton/1.6/"


def wait_for(driver, cond, timeout=10):
    return WebDriverWait(driver, timeout).until(cond)


@pytest.fixture(scope="module")
def driver():
    opts = Options()
    # headless mode for CI and local runs
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,1000")
    # Selenium Manager (bundled with Selenium 4.6+) will fetch ChromeDriver automatically
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()


def open_page(driver, path=""):
    driver.get(urljoin(BASE_URL, path))


# --------------------------
# 1) Home page basics
# --------------------------
def test_homepage_loads_and_title(driver):
    open_page(driver, "")
    wait_for(driver, EC.presence_of_element_located((By.TAG_NAME, "body")))
    # Title should be exactly this per assignment
    assert driver.title.strip() == "Teton Idaho CoC"


def test_logo_is_displayed(driver):
    open_page(driver, "")
    # Be permissive: look for a typical logo image by src/alt
    logo = wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//img[contains(translate(@alt,'LOGO','logo'),'logo') or "
                "contains(translate(@src,'LOGO','logo'),'logo')]",
            )
        ),
    )
    assert logo.is_displayed()


def test_heading_text_present(driver):
    open_page(driver, "")
    heading = wait_for(
        driver,
        EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(., 'Teton Idaho Chamber of Commerce')]")
        ),
    )
    assert "Teton Idaho Chamber of Commerce" in heading.text


# --------------------------
# 2) Navigation / spotlights
# --------------------------
def test_full_nav_and_spotlights(driver):
    open_page(driver, "")
    driver.set_window_size(1400, 1000)

    # Make sure the full nav (several links) is visible
    nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a, header nav a")
    # be a bit flexible—expect at least 3 links visible
    visible_links = [a for a in nav_links if a.is_displayed()]
    assert len(visible_links) >= 3

    # Spotlights: expect at least 2 spotlight blocks
    # Try common class names that ship with this assignment
    spotlights = driver.find_elements(
        By.XPATH,
        "//section[contains(@class,'spotlight')]"
        " | //div[contains(@class,'spotlight')]"
        " | //section[contains(@id,'spotlight')]"
        " | //div[contains(@id,'spotlight')]",
    )
    assert len(spotlights) >= 2


def test_join_link_navigates(driver):
    open_page(driver, "")
    join_link = wait_for(
        driver,
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[contains(translate(.,'JOIN','join'),'join')]",
            )
        ),
    )
    join_link.click()
    # On join page now
    wait_for(driver, EC.presence_of_element_located((By.TAG_NAME, "body")))
    assert "join" in driver.current_url.lower()


# --------------------------
# 3) Directory page view toggles and content
# --------------------------
def test_directory_grid_then_list_shows_teton_turf(driver):
    # go directly to the directory page (common names below)
    # try a few likely paths
    tried = []
    for candidate in ("directory.html", "directory", "teton/1.6/directory.html"):
        try:
            open_page(driver, candidate)
            wait_for(driver, EC.presence_of_element_located((By.TAG_NAME, "body")))
            tried.append(candidate)
            # If body loaded, assume OK and proceed
            break
        except Exception:
            continue
    else:
        pytest.fail("Could not open a directory page. Tried: " + ", ".join(tried))

    # Click Grid
    try:
        grid_btn = wait_for(
            driver,
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(translate(.,'GRID','grid'),'grid')]"
                    " | //a[contains(translate(.,'GRID','grid'),'grid')]",
                )
            ),
        )
        grid_btn.click()
    except Exception:
        # tolerate if it's already in grid mode
        pass

    # Confirm “Teton Turf and Tree” appears somewhere in card/grid
    wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[contains(translate(.,'TETON TURF AND TREE','teton turf and tree'),"
                "'teton turf and tree')]",
            )
        ),
    )

    # Click List
    try:
        list_btn = wait_for(
            driver,
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(translate(.,'LIST','list'),'list')]"
                    " | //a[contains(translate(.,'LIST','list'),'list')]",
                )
            ),
        )
        list_btn.click()
    except Exception:
        # tolerate if there's no separate list button
        pass

    # Confirm still visible in list mode
    wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[contains(translate(.,'TETON TURF AND TREE','teton turf and tree'),"
                "'teton turf and tree')]",
            )
        ),
    )


# --------------------------
# 4) Join page basic form
# --------------------------
def test_join_page_has_first_name_then_email(driver):
    # open the join page
    for candidate in ("join.html", "join", "teton/1.6/join.html"):
        try:
            open_page(driver, candidate)
            wait_for(driver, EC.presence_of_element_located((By.TAG_NAME, "body")))
            break
        except Exception:
            continue
    else:
        pytest.fail("Could not open a join page.")

    # First Name input present
    first_name = wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[contains(translate(@name,'FIRST','first'),'first')"
                " or contains(translate(@id,'FIRST','first'),'first')"
                " or contains(translate(@placeholder,'FIRST','first'),'first')]",
            )
        ),
    )
    first_name.clear()
    first_name.send_keys("Alex")

    # Click "Next Step"
    next_btn = wait_for(
        driver,
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(translate(.,'NEXT','next'),'next')]"
                " | //a[contains(translate(.,'NEXT','next'),'next')]",
            )
        ),
    )
    next_btn.click()

    # Email input present on step 2
    wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[contains(translate(@type,'EMAIL','email'),'email')"
                " or contains(translate(@name,'EMAIL','email'),'email')"
                " or contains(translate(@id,'EMAIL','email'),'email')]",
            )
        ),
    )


# --------------------------
# 5) Admin login negative test
# --------------------------
def test_admin_login_shows_error_for_bad_credentials(driver):
    # open the admin page
    for candidate in ("admin.html", "admin", "teton/1.6/admin.html"):
        try:
            open_page(driver, candidate)
            wait_for(driver, EC.presence_of_element_located((By.TAG_NAME, "body")))
            break
        except Exception:
            continue
    else:
        pytest.skip("Admin page not found; skipping this check.")

    # Username + password inputs
    username = wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[contains(translate(@name,'USER','user'),'user')"
                " or contains(translate(@id,'USER','user'),'user')"
                " or contains(translate(@placeholder,'USER','user'),'user')]",
            )
        ),
    )
    password = wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[contains(translate(@type,'PASS','pass'),'pass')"
                " or contains(translate(@name,'PASS','pass'),'pass')"
                " or contains(translate(@id,'PASS','pass'),'pass')]",
            )
        ),
    )
    username.clear()
    password.clear()
    username.send_keys("wronguser")
    password.send_keys("wrongpass")

    # Click Login
    login_btn = wait_for(
        driver,
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(translate(.,'LOGIN','login'),'login')]"
                " | //input[@type='submit' or @type='button'][contains(translate(@value,'LOGIN','login'),'login')]"
                " | //a[contains(translate(.,'LOGIN','login'),'login')]",
            )
        ),
    )
    login_btn.click()

    # Look for an error message (very flexible)
    err = wait_for(
        driver,
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[contains(translate(@class,'ERROR','error'),'error')"
                " or contains(translate(.,'INVALID','invalid'),'invalid')"
                " or contains(translate(.,'ERROR','error'),'error')]",
            )
        ),
    )
    assert err.is_displayed()
