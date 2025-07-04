"""
Selenium test configuration and fixtures for frontend testing.
"""
import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from werkzeug.serving import make_server
import threading
import time


class FlaskServerThread(threading.Thread):
    """Thread for running a Flask server during tests."""
    
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()
        self.daemon = True
    
    def run(self):
        """Start the Flask server."""
        self.srv.serve_forever()
    
    def shutdown(self):
        """Stop the Flask server."""
        self.srv.shutdown()


@pytest.fixture(scope='session')
def app_server(app):
    """Start a Flask server in a separate thread for UI testing."""
    server = FlaskServerThread(app)
    server.start()
    time.sleep(1)  # Give the server time to start
    yield server
    server.shutdown()


@pytest.fixture(scope='function')
def selenium(request, app_server):
    """Create a Selenium WebDriver instance based on the browser specified."""
    browser_name = request.config.getoption('--browser') or 'chrome'
    headless = request.config.getoption('--headless', False)
    
    if browser_name == 'chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
    elif browser_name == 'firefox':
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
    elif browser_name == 'edge':
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Edge(options=options)
    elif browser_name == 'safari':
        options = SafariOptions()
        driver = webdriver.Safari(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    
    # Set window size for consistent testing
    driver.set_window_size(1366, 768)
    
    # Return the driver instance
    yield driver
    
    # Quit the driver after the test is complete
    driver.quit()


@pytest.fixture(scope='session')
def screen_sizes():
    """Return a list of screen sizes to test for responsiveness."""
    return [
        {'width': 375, 'height': 667, 'name': 'mobile'},  # iPhone 8
        {'width': 768, 'height': 1024, 'name': 'tablet'},  # iPad
        {'width': 1366, 'height': 768, 'name': 'laptop'},  # Laptop
        {'width': 1920, 'height': 1080, 'name': 'desktop'}  # Desktop
    ]


def pytest_addoption(parser):
    """Add browser selection options to pytest."""
    parser.addoption('--browser', action='store', default='chrome',
                     help='Browser to use for testing: chrome, firefox, edge, safari')
    parser.addoption('--headless', action='store_true',
                     help='Run browser in headless mode') 