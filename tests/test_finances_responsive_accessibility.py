"""
Tests for responsive design and accessibility of the unified finances page.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from axe_selenium_python import Axe


@pytest.mark.responsive
class TestFinancesResponsive:
    """Test class for responsive design of the finances page."""

    @pytest.fixture(scope="function")
    def logged_in_finances_page(self, app_server, selenium):
        """Setup fixture for a logged-in user on the finances page."""
        # Navigate to login page
        selenium.get("http://127.0.0.1:5000/login")
        
        # Fill in login form (assumes test user exists)
        selenium.find_element(By.ID, "username").send_keys("testuser")
        selenium.find_element(By.ID, "password").send_keys("TestPassword123!")
        selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect to dashboard
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard-container"))
        )
        
        # Navigate to finances page
        selenium.get("http://127.0.0.1:5000/finances")
        
        # Wait for finances page to load
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, "financial-summary"))
        )
        
        return selenium

    @pytest.mark.parametrize('size', [
        {'width': 375, 'height': 667, 'name': 'mobile'},  # iPhone 8
        {'width': 768, 'height': 1024, 'name': 'tablet'},  # iPad
        {'width': 1366, 'height': 768, 'name': 'laptop'},  # Laptop
        {'width': 1920, 'height': 1080, 'name': 'desktop'}  # Desktop
    ])
    def test_responsive_layout(self, logged_in_finances_page, size):
        """Test responsive layout at different screen sizes."""
        driver = logged_in_finances_page
        
        # Resize window to test size
        driver.set_window_size(size['width'], size['height'])
        time.sleep(0.5)  # Allow time for responsive layout to adjust
        
        # Check that financial summary cards are displayed properly
        financial_summary = driver.find_element(By.ID, "financial-summary")
        assert financial_summary.is_displayed()
        
        # On mobile, cards should stack
        if size['name'] == 'mobile':
            cards = financial_summary.find_elements(By.CSS_SELECTOR, ".summary-card")
            for i in range(1, len(cards)):
                # Check vertical stacking: y of current card should be greater than y of previous card
                assert cards[i].location['y'] > cards[i-1].location['y']
        
        # On tablet+, check filter form layout
        filter_form = driver.find_element(By.ID, "filter-form")
        
        if size['name'] in ['mobile', 'tablet']:
            # In smaller screens, form elements should stack more
            date_from = driver.find_element(By.ID, "filter-date-from")
            date_to = driver.find_element(By.ID, "filter-date-to")
            assert date_from.location['y'] < date_to.location['y']
        else:
            # On larger screens, date fields should be side by side
            date_from = driver.find_element(By.ID, "filter-date-from")
            date_to = driver.find_element(By.ID, "filter-date-to")
            assert date_from.location['y'] == date_to.location['y']
        
        # Check quick filter buttons visibility
        quick_filters = driver.find_elements(By.CSS_SELECTOR, ".quick-filter-btn")
        for button in quick_filters:
            assert button.is_displayed()
        
        # Expand an account section
        account_headers = driver.find_elements(By.CSS_SELECTOR, ".account-header")
        if account_headers:
            account_headers[0].click()
            time.sleep(0.5)  # Wait for animation
            
            # Check transaction table is visible and fits in viewport
            transactions_table = driver.find_element(By.CSS_SELECTOR, ".account-transactions.show .table")
            assert transactions_table.is_displayed()
            
            # On mobile, check that table has horizontal scroll
            if size['name'] == 'mobile':
                # Table should have a parent with overflow-x: auto
                table_container = transactions_table.find_element(By.XPATH, "./..")
                assert "table-responsive" in table_container.get_attribute("class")

    def test_filter_panel_collapse(self, logged_in_finances_page):
        """Test filter panel collapses on small screens."""
        driver = logged_in_finances_page
        
        # Set mobile size
        driver.set_window_size(375, 667)
        time.sleep(0.5)  # Allow time for responsive layout to adjust
        
        # Find filter toggle button (should only be visible on small screens)
        filter_toggle = driver.find_element(By.ID, "filter-toggle")
        assert filter_toggle.is_displayed()
        
        # Filter panel should be collapsed initially
        filter_panel = driver.find_element(By.ID, "filter-panel")
        assert not filter_panel.is_displayed()
        
        # Click toggle button
        filter_toggle.click()
        time.sleep(0.5)  # Wait for animation
        
        # Filter panel should now be visible
        assert filter_panel.is_displayed()
        
        # Click toggle button again to collapse
        filter_toggle.click()
        time.sleep(0.5)  # Wait for animation
        
        # Filter panel should be collapsed again
        assert not filter_panel.is_displayed()

    def test_quick_actions_menu(self, logged_in_finances_page):
        """Test quick actions menu on mobile screens."""
        driver = logged_in_finances_page
        
        # Set mobile size
        driver.set_window_size(375, 667)
        time.sleep(0.5)  # Allow time for responsive layout to adjust
        
        # Find quick actions menu (should only be visible on mobile)
        quick_actions_button = driver.find_element(By.ID, "quick-actions-button")
        assert quick_actions_button.is_displayed()
        
        # Menu should be collapsed initially
        quick_actions_menu = driver.find_element(By.ID, "quick-actions-menu")
        assert not quick_actions_menu.is_displayed()
        
        # Click button to show menu
        quick_actions_button.click()
        time.sleep(0.5)  # Wait for animation
        
        # Menu should now be visible
        assert quick_actions_menu.is_displayed()
        
        # Menu should contain key action buttons
        assert driver.find_element(By.CSS_SELECTOR, "#quick-actions-menu .add-transaction-btn").is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, "#quick-actions-menu .ai-suggest-btn").is_displayed()


@pytest.mark.accessibility
class TestFinancesAccessibility:
    """Test class for accessibility of the finances page."""

    @pytest.fixture(scope="function")
    def logged_in_finances_page(self, app_server, selenium):
        """Setup fixture for a logged-in user on the finances page."""
        # Navigate to login page
        selenium.get("http://127.0.0.1:5000/login")
        
        # Fill in login form (assumes test user exists)
        selenium.find_element(By.ID, "username").send_keys("testuser")
        selenium.find_element(By.ID, "password").send_keys("TestPassword123!")
        selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect to dashboard
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard-container"))
        )
        
        # Navigate to finances page
        selenium.get("http://127.0.0.1:5000/finances")
        
        # Wait for finances page to load
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, "financial-summary"))
        )
        
        return selenium

    def test_axe_accessibility(self, logged_in_finances_page):
        """Test page accessibility using aXe."""
        driver = logged_in_finances_page
        
        # Initialize axe
        axe = Axe(driver)
        axe.inject()
        
        # Run accessibility analysis
        results = axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Write violations to a file for review
        if violations:
            with open("accessibility_violations.json", "w") as f:
                import json
                json.dump(violations, f, indent=4)
        
        # Assert no critical violations
        critical_violations = [v for v in violations if v["impact"] == "critical"]
        assert len(critical_violations) == 0, f"Critical accessibility violations found: {len(critical_violations)}"

    def test_keyboard_navigation(self, logged_in_finances_page):
        """Test keyboard navigation for accessibility."""
        driver = logged_in_finances_page
        
        # Focus on first interactive element
        active_element = driver.switch_to.active_element
        active_element.send_keys("\t")  # First tab
        
        # Elements to check for keyboard focus
        focus_elements = [
            {"id": "search-transactions", "name": "Search box"},
            {"id": "filter-date-from", "name": "From date"},
            {"id": "filter-date-to", "name": "To date"},
            {"id": "filter-account", "name": "Account filter"},
            {"id": "filter-category", "name": "Category filter"},
            {"id": "filter-type", "name": "Transaction type filter"},
            {"id": "apply-filters", "name": "Apply filters button"},
            {"id": "quick-filter-all", "name": "All transactions button"}
        ]
        
        # Check that we can tab through all elements
        for element in focus_elements:
            active_element = driver.switch_to.active_element
            assert active_element.get_attribute("id") == element["id"], f"Failed to focus on {element['name']}"
            active_element.send_keys("\t")  # Next tab

    def test_screen_reader_accessibility(self, logged_in_finances_page):
        """Test screen reader accessibility attributes."""
        driver = logged_in_finances_page
        
        # Check for aria-labels on buttons without text
        icon_buttons = driver.find_elements(By.CSS_SELECTOR, "button:not(:has(span:not(.icon)))")
        for button in icon_buttons:
            assert button.get_attribute("aria-label") is not None, "Button missing aria-label"
        
        # Check for form field labels
        form_fields = driver.find_elements(By.CSS_SELECTOR, "input, select")
        for field in form_fields:
            field_id = field.get_attribute("id")
            if field_id:
                # Either has a <label> tag or aria-label
                label_exists = len(driver.find_elements(By.CSS_SELECTOR, f"label[for='{field_id}']")) > 0
                has_aria_label = field.get_attribute("aria-label") is not None
                assert label_exists or has_aria_label, f"Field {field_id} missing label or aria-label"
        
        # Check for alt text on images
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            assert img.get_attribute("alt") is not None, "Image missing alt text"
        
        # Check for proper heading structure
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
        heading_levels = [int(h.tag_name[1]) for h in headings]
        # Ensure no heading level is skipped (e.g., h1 to h3 without h2)
        for i in range(len(heading_levels) - 1):
            if heading_levels[i+1] > heading_levels[i]:
                assert heading_levels[i+1] <= heading_levels[i] + 1, "Heading level skipped"

    def test_color_contrast(self, logged_in_finances_page):
        """Test color contrast compliance."""
        driver = logged_in_finances_page
        
        # Initialize axe
        axe = Axe(driver)
        axe.inject()
        
        # Run accessibility analysis with specific rules for color contrast
        results = axe.run(rules=['color-contrast'])
        
        # Check for violations
        violations = results["violations"]
        
        # Assert no color contrast violations
        assert len(violations) == 0, f"Color contrast violations found: {len(violations)}"

    def test_table_accessibility(self, logged_in_finances_page):
        """Test transaction table accessibility."""
        driver = logged_in_finances_page
        
        # Expand an account section to see the table
        account_headers = driver.find_elements(By.CSS_SELECTOR, ".account-header")
        if account_headers:
            account_headers[0].click()
            time.sleep(0.5)  # Wait for animation
            
            # Check table has proper ARIA attributes
            table = driver.find_element(By.CSS_SELECTOR, ".account-transactions.show .table")
            
            # Check table headers have scope
            th_elements = table.find_elements(By.TAG_NAME, "th")
            for th in th_elements:
                assert th.get_attribute("scope") == "col", "Table header missing scope attribute"
            
            # Check table caption or aria-label for screen readers
            has_caption = len(table.find_elements(By.TAG_NAME, "caption")) > 0
            has_aria_label = table.get_attribute("aria-label") is not None
            assert has_caption or has_aria_label, "Table missing caption or aria-label" 