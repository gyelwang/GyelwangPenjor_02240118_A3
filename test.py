import unittest
import os
import random
from GyelwangPenjor_02240118_A3_Part_A import *

class TestBankingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a test file with some accounts before running tests"""
        cls.test_filename = "test_accounts.txt"
        with open(cls.test_filename, "w") as f:
            f.write("10001,1234,Personal,500.0\n")
            f.write("10002,5678,Business,1000.0\n")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test file after all tests"""
        try:
            os.remove(cls.test_filename)
        except:
            pass

    def setUp(self):
        """Create fresh banking system instance for each test"""
        self.bank = Banking_system(self.test_filename)
        self.controller = BankingController(self.bank)
    
    def test_load_accounts(self):
        """Test loading accounts from file"""
        self.assertEqual(len(self.bank.accounts), 2)
        self.assertIn("10001", self.bank.accounts)
        self.assertIn("10002", self.bank.accounts)
    
    def test_create_account(self):
        """Test account creation"""
        initial_count = len(self.bank.accounts)
        account = self.bank.create_account("Personal")
        
        self.assertEqual(len(self.bank.accounts), initial_count + 1)
        self.assertIn(account.id, self.bank.accounts)
        self.assertEqual(account.account_category, "Personal")
        self.assertEqual(account.funds, 0)
    
    def test_login_valid(self):
        """Test successful login"""
        account = self.bank.login("10001", "1234")
        self.assertEqual(account.id, "10001")
        self.assertEqual(account.passcode, "1234")
    
    def test_login_invalid(self):
        """Test failed login attempts"""
        with self.assertRaises(InvalidAccountError):
            self.bank.login("99999", "0000")  # Non-existent account
        
        with self.assertRaises(InvalidAccountError):
            self.bank.login("10001", "9999")  # Wrong passcode
    
    def test_deposit_valid(self):
        """Test valid deposits"""
        account = self.bank.accounts["10001"]
        initial_balance = account.funds
        result = account.deposit(100)
        
        self.assertEqual(account.funds, initial_balance + 100)
        self.assertIn("Deposited Nu: 100", result)
    
    def test_deposit_invalid(self):
        """Test invalid deposit amounts"""
        account = self.bank.accounts["10001"]
        
        with self.assertRaises(InvalidAmountError):
            account.deposit(0)  # Zero amount
        
        with self.assertRaises(InvalidAmountError):
            account.deposit(-100)  # Negative amount
    
    def test_withdraw_valid(self):
        """Test valid withdrawals"""
        account = self.bank.accounts["10001"]
        initial_balance = account.funds
        result = account.withdraw(100)
        
        self.assertEqual(account.funds, initial_balance - 100)
        self.assertIn("Withdrew Nu: 100", result)
    
    def test_withdraw_invalid(self):
        """Test invalid withdrawal attempts"""
        account = self.bank.accounts["10001"]
        
        with self.assertRaises(InvalidAmountError):
            account.withdraw(0)  # Zero amount
        
        with self.assertRaises(InvalidAmountError):
            account.withdraw(-100)  # Negative amount
        
        with self.assertRaises(InsufficientFundsError):
            account.withdraw(10000)  # More than balance
    
    def test_transfer_valid(self):
        """Test valid transfers between accounts"""
        sender = self.bank.accounts["10002"]
        recipient = self.bank.accounts["10001"]
        sender_initial = sender.funds
        recipient_initial = recipient.funds
        amount = 200
        
        result = sender.transfer(amount, recipient)
        
        self.assertEqual(sender.funds, sender_initial - amount)
        self.assertEqual(recipient.funds, recipient_initial + amount)
        self.assertIn(f"transferred Nu: {amount}", result)
    
    def test_transfer_invalid(self):
        """Test invalid transfer attempts"""
        sender = self.bank.accounts["10001"]
        recipient = self.bank.accounts["10002"]
        
        with self.assertRaises(InvalidAmountError):
            sender.transfer(0, recipient)  # Zero amount
        
        with self.assertRaises(InvalidAmountError):
            sender.transfer(-100, recipient)  # Negative amount
        
        with self.assertRaises(InsufficientFundsError):
            sender.transfer(10000, recipient)  # More than balance
        
        with self.assertRaises(BankError):
            sender.transfer(100, None)  # Invalid recipient
    
    def test_top_up_mobile_valid(self):
        """Test valid mobile top-ups"""
        account = self.bank.accounts["10001"]
        initial_balance = account.funds
        amount = 50
        phone = "17171717"
        
        result = self.bank.top_up_mobile(account, phone, amount)
        
        self.assertEqual(account.funds, initial_balance - amount)
        self.assertIn(f"topped up Nu: {amount} to phone {phone}", result)
    
    def test_top_up_mobile_invalid(self):
        """Test invalid mobile top-up attempts"""
        account = self.bank.accounts["10001"]
        
        with self.assertRaises(BankError):
            self.bank.top_up_mobile(account, "17171717", 0)  # Zero amount
        
        with self.assertRaises(BankError):
            self.bank.top_up_mobile(account, "17171717", -50)  # Negative amount
        
        with self.assertRaises(BankError):
            self.bank.top_up_mobile(account, "17171717", 10000)  # More than balance
    
    def test_delete_account(self):
        """Test account deletion"""
        initial_count = len(self.bank.accounts)
        self.bank.delete_account("10001")
        
        self.assertEqual(len(self.bank.accounts), initial_count - 1)
        self.assertNotIn("10001", self.bank.accounts)
        
        with self.assertRaises(InvalidAccountError):
            self.bank.delete_account("99999")  # Non-existent account
    
    def test_controller_input_processing(self):
        """Test controller's input processing"""
        # Test main menu options
        with self.assertRaises(ValueError):
            self.controller.processUserInput("0", True)  # Invalid option
        
        # Test account menu options without logged in account
        with self.assertRaises(BankError):
            self.controller.processUserInput("1", False)
        
        # Login first
        self.controller.current_account = self.bank.accounts["10001"]
        
        # Test account menu options
        with self.assertRaises(ValueError):
            self.controller.processUserInput("0", False)  # Invalid option
        
        # Test valid balance check
        result = self.controller.processUserInput("1", False)
        self.assertIn(f"Nu: {self.controller.current_account.funds}", result)
    
    def test_account_types(self):
        """Test different account types"""
        personal = Personal_account("20001", "1111")
        business = Business_account("20002", "2222")
        
        self.assertEqual(personal.account_category, "Personal")
        self.assertEqual(business.account_category, "Business")
        
        # Test inheritance
        self.assertIsInstance(personal, Bank_Account)
        self.assertIsInstance(business, Bank_Account)

if __name__ == "__main__":
    unittest.main()