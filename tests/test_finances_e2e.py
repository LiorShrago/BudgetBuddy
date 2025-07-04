"""
End-to-end tests for unified finances page workflows.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


@pytest.mark.e2e
class TestFinancesE2E:
    """End-to-end test class for finances page workflows."""

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

    def test_complete_account_viewing_workflow(self, logged_in_finances_page):
        """Test the complete workflow of viewing accounts and their transactions."""
        driver = logged_in_finances_page
        
        # 1. Verify financial summary cards are present
        assert driver.find_element(By.ID, "net-worth-card").is_displayed()
        assert driver.find_element(By.ID, "cash-accounts-card").is_displayed()
        assert driver.find_element(By.ID, "credit-card-accounts-card").is_displayed()
        
        # 2. Click on a financial summary card to expand details
        driver.find_element(By.ID, "cash-accounts-card").click()
        
        # Wait for dropdown to appear
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#cash-accounts-card .card-dropdown"))
        )
        
        # 3. Find and click on an account in the accounts list
        account_sections = driver.find_elements(By.CSS_SELECTOR, ".account-section")
        if account_sections:
            account_sections[0].find_element(By.CSS_SELECTOR, ".account-header").click()
            
            # Wait for transactions to appear
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".account-transactions.show"))
            )
            
            # 4. Verify transactions are visible
            transactions = driver.find_elements(By.CSS_SELECTOR, ".transaction-row")
            assert len(transactions) > 0
            
            # 5. Close the account section
            account_sections[0].find_element(By.CSS_SELECTOR, ".account-header").click()
            
            # Wait for transactions to be hidden
            time.sleep(0.5)  # Animation delay
            
            # 6. Verify transactions are hidden
            account_body = account_sections[0].find_element(By.CSS_SELECTOR, ".account-transactions")
            assert "show" not in account_body.get_attribute("class")

    def test_transaction_filtering_workflow(self, logged_in_finances_page):
        """Test the complete workflow of filtering transactions."""
        driver = logged_in_finances_page
        
        # 1. Set date range
        driver.find_element(By.ID, "filter-date-from").send_keys("2025-01-01")
        driver.find_element(By.ID, "filter-date-to").send_keys("2025-12-31")
        
        # 2. Select an account type
        account_select = Select(driver.find_element(By.ID, "filter-account"))
        # Choose the second option (first real account, not "All Accounts")
        if len(account_select.options) > 1:
            account_select.select_by_index(1)
        
        # 3. Select a transaction type
        type_select = Select(driver.find_element(By.ID, "filter-type"))
        type_select.select_by_value("expense")
        
        # 4. Apply filters
        driver.find_element(By.ID, "apply-filters").click()
        
        # Wait for AJAX request to complete
        time.sleep(1)
        
        # 5. Verify filter indicators appear
        filter_badges = driver.find_elements(By.CSS_SELECTOR, ".filter-badge")
        assert len(filter_badges) > 0
        
        # 6. Test a quick filter button
        driver.find_element(By.ID, "quick-filter-recent").click()
        
        # Wait for AJAX request to complete
        time.sleep(1)
        
        # 7. Verify the filters changed
        date_from = driver.find_element(By.ID, "filter-date-from").get_attribute("value")
        assert date_from != "2025-01-01"  # Should be updated to 30 days ago
        
        # 8. Clear all filters
        driver.find_element(By.ID, "clear-filters").click()
        
        # Wait for AJAX request to complete
        time.sleep(1)
        
        # 9. Verify filters are reset
        account_select = Select(driver.find_element(By.ID, "filter-account"))
        assert account_select.first_selected_option.get_attribute("value") == ""

    def test_inline_categorization_workflow(self, logged_in_finances_page):
        """Test the workflow of categorizing transactions inline."""
        driver = logged_in_finances_page
        
        # 1. Use quick filter to show uncategorized transactions
        driver.find_element(By.ID, "quick-filter-uncategorized").click()
        
        # Wait for AJAX request to complete
        time.sleep(1)
        
        # 2. Expand the first account with uncategorized transactions
        account_sections = driver.find_elements(By.CSS_SELECTOR, ".account-section")
        
        for account in account_sections:
            # Click to expand
            account.find_element(By.CSS_SELECTOR, ".account-header").click()
            time.sleep(0.5)  # Wait for animation
            
            # Check if there are transactions
            transactions = account.find_elements(By.CSS_SELECTOR, ".transaction-row")
            if transactions:
                # Find first transaction with empty category
                for transaction in transactions:
                    category_select = transaction.find_element(By.CSS_SELECTOR, ".category-select")
                    if not category_select.get_attribute("value"):
                        # 3. Select a category
                        select = Select(category_select)
                        if len(select.options) > 1:
                            select.select_by_index(1)
                            
                            # 4. Save the category
                            transaction.find_element(By.CSS_SELECTOR, ".save-category").click()
                            
                            # Wait for AJAX request to complete
                            time.sleep(1)
                            
                            # 5. Verify the category was saved
                            updated_select = Select(transaction.find_element(By.CSS_SELECTOR, ".category-select"))
                            assert updated_select.first_selected_option.get_attribute("value") != ""
                            
                            return  # Test successful
                
            # If no suitable transactions found, collapse and try next account
            account.find_element(By.CSS_SELECTOR, ".account-header").click()
            time.sleep(0.5)  # Wait for animation

    def test_bulk_categorization_workflow(self, logged_in_finances_page):
        """Test the workflow of bulk categorizing transactions."""
        driver = logged_in_finances_page
        
        # 1. Use quick filter to show uncategorized transactions
        driver.find_element(By.ID, "quick-filter-uncategorized").click()
        
        # Wait for AJAX request to complete
        time.sleep(1)
        
        # 2. Expand an account section
        account_sections = driver.find_elements(By.CSS_SELECTOR, ".account-section")
        if account_sections:
            account_sections[0].find_element(By.CSS_SELECTOR, ".account-header").click()
            time.sleep(0.5)  # Wait for animation
            
            # 3. Select multiple transactions
            checkboxes = driver.find_elements(By.CSS_SELECTOR, ".transaction-checkbox")
            if len(checkboxes) >= 2:
                checkboxes[0].click()
                checkboxes[1].click()
                
                # 4. Select category from bulk dropdown
                bulk_category_select = Select(driver.find_element(By.ID, "bulk-category"))
                if len(bulk_category_select.options) > 1:
                    bulk_category_select.select_by_index(1)
                    
                    # 5. Click categorize selected button
                    driver.find_element(By.ID, "categorize-selected").click()
                    
                    # Wait for AJAX request to complete
                    time.sleep(1)
                    
                    # 6. Verify success message appears
                    success_alert = driver.find_element(By.CSS_SELECTOR, ".alert-success")
                    assert success_alert.is_displayed()
                    assert "successfully categorized" in success_alert.text.lower()

    def test_add_transaction_workflow(self, logged_in_finances_page):
        """Test the workflow of adding a new transaction."""
        driver = logged_in_finances_page
        
        # 1. Click on an account to expand it
        account_sections = driver.find_elements(By.CSS_SELECTOR, ".account-section")
        if account_sections:
            account_sections[0].find_element(By.CSS_SELECTOR, ".account-header").click()
            time.sleep(0.5)  # Wait for animation
            
            # 2. Click add transaction button
            add_button = account_sections[0].find_element(By.CSS_SELECTOR, ".add-transaction-btn")
            add_button.click()
            
            # 3. Wait for modal to appear
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "addTransactionModal"))
            )
            
            # 4. Fill out transaction form
            driver.find_element(By.ID, "transaction-date").send_keys("2025-03-15")
            driver.find_element(By.ID, "transaction-description").send_keys("Test Transaction E2E")
            driver.find_element(By.ID, "transaction-amount").send_keys("42.99")
            
            # Select a category
            category_select = Select(driver.find_element(By.ID, "transaction-category"))
            if len(category_select.options) > 1:
                category_select.select_by_index(1)
            
            # 5. Submit form
            driver.find_element(By.ID, "save-transaction").click()
            
            # 6. Wait for modal to close and success message
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "addTransactionModal"))
            )
            
            # 7. Verify success message
            success_alert = driver.find_element(By.CSS_SELECTOR, ".alert-success")
            assert success_alert.is_displayed()
            assert "added successfully" in success_alert.text.lower()
            
            # 8. Verify new transaction appears in the list
            transaction_descriptions = driver.find_elements(By.CSS_SELECTOR, ".transaction-description")
            found = False
            for desc in transaction_descriptions:
                if "Test Transaction E2E" in desc.text:
                    found = True
                    break
            assert found

    def test_ai_suggestion_workflow(self, logged_in_finances_page):
        """Test the AI suggestion workflow for categorization."""
        driver = logged_in_finances_page
        
        # 1. Use quick filter to show uncategorized transactions
        driver.find_element(By.ID, "quick-filter-uncategorized").click()
        
        # Wait for AJAX request to complete
        time.sleep(1)
        
        # 2. Expand an account section
        account_sections = driver.find_elements(By.CSS_SELECTOR, ".account-section")
        if account_sections:
            account_sections[0].find_element(By.CSS_SELECTOR, ".account-header").click()
            time.sleep(0.5)  # Wait for animation
            
            # 3. Select a transaction
            checkboxes = driver.find_elements(By.CSS_SELECTOR, ".transaction-checkbox")
            if checkboxes:
                checkboxes[0].click()
                
                # 4. Click AI suggest button
                driver.find_element(By.ID, "ai-suggest-selected").click()
                
                # Wait for AJAX request to complete (AI suggestions may take longer)
                time.sleep(2)
                
                # 5. Verify the transaction row gets the "ai-suggestion" class
                transaction_row = checkboxes[0].find_element(By.XPATH, "./ancestor::tr")
                assert "ai-suggestion" in transaction_row.get_attribute("class")
                
                # 6. Verify suggestion is shown
                suggestion_badge = transaction_row.find_element(By.CSS_SELECTOR, ".suggestion-badge")
                assert suggestion_badge.is_displayed()

    def test_keyboard_navigation(self, logged_in_finances_page):
        """Test keyboard navigation of the interface."""
        driver = logged_in_finances_page
        
        # 1. Press 'n' to open new transaction modal
        ActionChains(driver).send_keys('n').perform()
        
        # Wait for modal to appear
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "addTransactionModal"))
        )
        
        # Close the modal
        driver.find_element(By.CSS_SELECTOR, ".btn-close").click()
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "addTransactionModal"))
        )
        
        # 2. Press 'f' to focus search box
        ActionChains(driver).send_keys('f').perform()
        
        # Verify search box is focused
        focused_element = driver.switch_to.active_element
        assert focused_element.get_attribute("id") == "search-transactions"
        
        # 3. Test tab navigation through filters
        focused_element.send_keys(Keys.TAB)
        focused_element = driver.switch_to.active_element
        assert focused_element.get_attribute("id") == "filter-date-from"
        
        focused_element.send_keys(Keys.TAB)
        focused_element = driver.switch_to.active_element
        assert focused_element.get_attribute("id") == "filter-date-to" 