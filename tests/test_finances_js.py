"""
Unit tests for finances.js JavaScript functions using pytest-selenium.
"""
import pytest
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.frontend
class TestFinancesJavaScript:
    """Test class for finances.js JavaScript functions."""

    @pytest.fixture(scope="function")
    def finances_page(self, app_client_with_user, selenium):
        """Setup fixture to load the finances page in Selenium."""
        # First, authenticate the user
        response = app_client_with_user.get('/finances')
        cookies = app_client_with_user.cookie_jar._cookies['localhost.local']['/']
        
        # Load the page in Selenium
        selenium.get(f"{app_client_with_user.application_root}/finances")
        
        # Add the session cookie to maintain authentication
        for cookie_name, cookie_obj in cookies.items():
            selenium.add_cookie({
                'name': cookie_name,
                'value': cookie_obj.value,
                'path': '/'
            })
            
        # Reload the page with cookies
        selenium.get(f"{app_client_with_user.application_root}/finances")
        
        # Wait for page to load
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, "financial-summary"))
        )
        
        return selenium

    def test_filter_transactions_by_date(self, finances_page):
        """Test filtering transactions by date."""
        # Set date range filters
        finances_page.find_element(By.ID, "filter-date-from").send_keys("2025-01-01")
        finances_page.find_element(By.ID, "filter-date-to").send_keys("2025-01-31")
        finances_page.find_element(By.ID, "apply-filters").click()
        
        # Wait for AJAX request to complete
        time.sleep(0.5)
        
        # Check that transactions are filtered
        transaction_dates = finances_page.find_elements(By.CSS_SELECTOR, ".transaction-date")
        for date_elem in transaction_dates:
            date_text = date_elem.text
            # Check that dates are within range (format: MM/DD/YYYY)
            month, day, year = map(int, date_text.split('/'))
            assert year == 2025
            assert month == 1
            assert 1 <= day <= 31

    def test_filter_transactions_by_account(self, finances_page):
        """Test filtering transactions by account."""
        # Get first account option
        account_select = finances_page.find_element(By.ID, "filter-account")
        first_account_option = account_select.find_elements(By.TAG_NAME, "option")[1]
        account_id = first_account_option.get_attribute("value")
        account_name = first_account_option.text
        
        # Select the account
        first_account_option.click()
        finances_page.find_element(By.ID, "apply-filters").click()
        
        # Wait for AJAX request to complete
        time.sleep(0.5)
        
        # Check that only transactions from the selected account are shown
        account_cells = finances_page.find_elements(By.CSS_SELECTOR, ".transaction-account")
        for cell in account_cells:
            assert cell.text == account_name

    def test_filter_transactions_by_category(self, finances_page):
        """Test filtering transactions by category."""
        # Get first category option
        category_select = finances_page.find_element(By.ID, "filter-category")
        first_category_option = category_select.find_elements(By.TAG_NAME, "option")[1]
        category_id = first_category_option.get_attribute("value")
        category_name = first_category_option.text
        
        # Select the category
        first_category_option.click()
        finances_page.find_element(By.ID, "apply-filters").click()
        
        # Wait for AJAX request to complete
        time.sleep(0.5)
        
        # Check that only transactions from the selected category are shown
        category_cells = finances_page.find_elements(By.CSS_SELECTOR, ".transaction-category")
        for cell in category_cells:
            assert cell.text == category_name

    def test_expand_collapse_account_section(self, finances_page):
        """Test expanding and collapsing account sections."""
        # Find first account section
        account_header = finances_page.find_element(By.CSS_SELECTOR, ".account-header")
        account_body = finances_page.find_element(By.CSS_SELECTOR, ".account-transactions")
        
        # Check initial state (should be collapsed)
        assert "show" not in account_body.get_attribute("class")
        
        # Expand section
        account_header.click()
        time.sleep(0.3)  # Wait for animation
        assert "show" in account_body.get_attribute("class")
        
        # Collapse section
        account_header.click()
        time.sleep(0.3)  # Wait for animation
        assert "show" not in account_body.get_attribute("class")

    def test_bulk_select_transactions(self, finances_page):
        """Test bulk selection of transactions."""
        # Expand first account
        finances_page.find_element(By.CSS_SELECTOR, ".account-header").click()
        time.sleep(0.3)
        
        # Click "Select All" checkbox
        select_all = finances_page.find_element(By.ID, "select-all")
        select_all.click()
        
        # Check that all checkboxes are selected
        checkboxes = finances_page.find_elements(By.CSS_SELECTOR, ".transaction-checkbox")
        for checkbox in checkboxes:
            assert checkbox.is_selected()
        
        # Verify selected count
        selected_count = finances_page.find_element(By.ID, "selected-count")
        assert f"{len(checkboxes)} selected" in selected_count.text

    def test_inline_categorization(self, finances_page):
        """Test inline categorization of a transaction."""
        # Expand first account
        finances_page.find_element(By.CSS_SELECTOR, ".account-header").click()
        time.sleep(0.3)
        
        # Find first transaction's category dropdown
        category_select = finances_page.find_element(By.CSS_SELECTOR, ".category-select")
        category_options = category_select.find_elements(By.TAG_NAME, "option")
        
        if len(category_options) > 1:
            # Select a different category
            current_value = category_select.get_attribute("value")
            new_option = category_options[1] if category_options[0].get_attribute("value") == current_value else category_options[0]
            new_option.click()
            
            # Click save button
            save_btn = finances_page.find_element(By.CSS_SELECTOR, ".save-category")
            save_btn.click()
            
            # Wait for AJAX request to complete
            time.sleep(0.5)
            
            # Verify category was updated
            updated_select = finances_page.find_element(By.CSS_SELECTOR, ".category-select")
            assert updated_select.get_attribute("value") == new_option.get_attribute("value")

    def test_quick_filter_buttons(self, finances_page):
        """Test quick filter buttons."""
        # Click "Uncategorized" quick filter
        uncategorized_btn = finances_page.find_element(By.ID, "quick-filter-uncategorized")
        uncategorized_btn.click()
        
        # Wait for AJAX request to complete
        time.sleep(0.5)
        
        # Check that only uncategorized transactions are shown
        category_cells = finances_page.find_elements(By.CSS_SELECTOR, ".transaction-category")
        for cell in category_cells:
            assert cell.text == "Uncategorized" or not cell.text.strip()

    def test_search_functionality(self, finances_page):
        """Test transaction search functionality."""
        # Enter search term
        search_input = finances_page.find_element(By.ID, "search-transactions")
        search_term = "grocery"
        search_input.send_keys(search_term)
        
        # Submit search
        finances_page.find_element(By.ID, "apply-filters").click()
        
        # Wait for AJAX request to complete
        time.sleep(0.5)
        
        # Check that results contain search term
        transaction_descriptions = finances_page.find_elements(By.CSS_SELECTOR, ".transaction-description")
        if transaction_descriptions:
            at_least_one_match = False
            for desc in transaction_descriptions:
                if search_term.lower() in desc.text.lower():
                    at_least_one_match = True
                    break
            assert at_least_one_match

    def test_add_transaction_modal(self, finances_page):
        """Test opening the add transaction modal."""
        # Click add transaction button
        finances_page.find_element(By.CSS_SELECTOR, ".add-transaction-btn").click()
        
        # Verify modal is displayed
        modal = finances_page.find_element(By.ID, "addTransactionModal")
        assert modal.is_displayed()
        
        # Verify form fields exist
        assert finances_page.find_element(By.ID, "transaction-date").is_displayed()
        assert finances_page.find_element(By.ID, "transaction-description").is_displayed()
        assert finances_page.find_element(By.ID, "transaction-amount").is_displayed()
        assert finances_page.find_element(By.ID, "transaction-category").is_displayed() 