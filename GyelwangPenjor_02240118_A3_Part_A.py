import random  # for generating account ID and passcode

# GUI
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog

'''Exception classes for specific banking errors'''

class BankError(Exception):
    '''Base exception for all bank-related issues'''
    pass

class InvalidAmountError(BankError):
    pass

class InsufficientFundsError(BankError):
    pass

class InvalidAccountError(BankError):
    pass

class Bank_Account:
    """Base class for a bank account, allows deposits, transfers, and withdrawals."""
    def __init__(self, id, passcode, account_category, funds=0):
        self.id = id
        self.passcode = passcode
        self.account_category = account_category
        self.funds = funds

    def deposit(self, amount):
        """Add funds to the account."""
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero")
        self.funds += amount
        return f"Deposited Nu: {amount}. New balance: Nu: {self.funds}"

    def withdraw(self, amount):
        """Withdraw money from the account."""
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero")
        if amount > self.funds:
            raise InsufficientFundsError("Not enough balance")
        self.funds -= amount
        return f"Withdrew Nu: {amount}. New balance: Nu: {self.funds}"

    def transfer(self, amount, recipient_account):
        """Transfer money to another user."""
        if recipient_account is None:
            raise BankError("Invalid recipient account")
        try:
            self.withdraw(amount)
            recipient_account.deposit(amount)
            return f"Successfully transferred Nu: {amount} to account {recipient_account.id}"
        except BankError as e:
            raise BankError(f"Transfer failed: {str(e)}")

class Personal_account(Bank_Account):
    """Subclass for personal accounts"""
    def __init__(self, id, passcode, account_category="Personal", funds=0):
        super().__init__(id, passcode, account_category, funds)

class Business_account(Bank_Account):
    """Subclass for business accounts"""
    def __init__(self, id, passcode, account_category="Business", funds=0):
        super().__init__(id, passcode, account_category, funds)

class Banking_system:
    """System to handle account data and file I/O"""
    def __init__(self, filename="accounts.txt"):
        self.filename = filename
        self.accounts = self.load_accounts()

    def load_accounts(self):
        accounts = {}
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    try:
                        id, passcode, account_category, funds = line.strip().split(",")
                        funds = float(funds)
                        account = Personal_account(id, passcode, account_category, funds) if account_category == "Personal" else Business_account(id, passcode, account_category, funds)
                        accounts[id] = account
                    except ValueError:
                        continue
        except FileNotFoundError:
            pass
        return accounts

    def save_accounts(self):
        with open(self.filename, "w") as file:
            for account in self.accounts.values():
                file.write(f"{account.id},{account.passcode},{account.account_category},{account.funds}\n")

    def create_account(self, account_type):
        id = str(random.randint(10000, 99999))
        passcode = str(random.randint(1000, 9999))
        account = Personal_account(id, passcode) if account_type == "Personal" else Business_account(id, passcode)
        self.accounts[id] = account
        self.save_accounts()
        return account

    def login(self, id, passcode):
        account = self.accounts.get(id)
        if not account or account.passcode != passcode:
            raise InvalidAccountError("Invalid ID or passcode")
        return account

    def delete_account(self, id):
        if id not in self.accounts:
            raise InvalidAccountError("Account not found")
        del self.accounts[id]
        self.save_accounts()

    def top_up_mobile(self, account, phone_number, amount):
        try:
            account.withdraw(amount)
            return f"Successfully topped up Nu: {amount} to phone {phone_number}"
        except BankError as e:
            raise BankError(f"Top-up failed: {str(e)}")

class BankingController:
    """Handles input decisions for user interactions"""
    def __init__(self, banking_system):
        self.bank = banking_system
        self.current_account = None

    def processUserInput(self, choice, is_main_menu=True):
        return self._process_main_menu(choice) if is_main_menu else self._process_account_menu(choice)

    def _process_main_menu(self, choice):
        if choice == "1": return self._create_account()
        if choice == "2": return self._login_account()
        if choice == "3": return "exit"
        raise ValueError("Unknown menu choice")

    def _process_account_menu(self, choice):
        if not self.current_account:
            raise BankError("No account logged in")
        if choice == "1": return f"Current balance: Nu: {self.current_account.funds}"
        if choice == "2": amount = float(simpledialog.askstring("Deposit", "Enter amount:")); return self.current_account.deposit(amount)
        if choice == "3": amount = float(simpledialog.askstring("Withdraw", "Enter amount:")); return self.current_account.withdraw(amount)
        if choice == "4":
            recipient_id = simpledialog.askstring("Transfer", "Recipient account ID:")
            amount = float(simpledialog.askstring("Transfer", "Enter amount:"))
            recipient = self.bank.accounts.get(recipient_id)
            if not recipient: raise BankError("Recipient not found")
            return self.current_account.transfer(amount, recipient)
        if choice == "5": phone = simpledialog.askstring("Top-up", "Phone number:"); amount = float(simpledialog.askstring("Top-up", "Amount:")); return self.bank.top_up_mobile(self.current_account, phone, amount)
        if choice == "6":
            confirm = messagebox.askyesno("Confirm", "Permanently delete this account?")
            if confirm:
                self.bank.delete_account(self.current_account.id)
                self.current_account = None
                return "Account deleted successfully"
            return "Deletion cancelled"
        if choice == "7": self.current_account = None; return "logout"
        raise ValueError("Invalid option")

    def _create_account(self):
        acc_type = simpledialog.askstring("Account Type", "1 for Personal, 2 for Business:")
        if acc_type not in ("1", "2"):
            raise ValueError("Invalid type")
        account = self.bank.create_account("Personal" if acc_type == "1" else "Business")
        return f"Account created!\nID: {account.id}\nPasscode: {account.passcode}"

    def _login_account(self):
        account_id = simpledialog.askstring("Login", "Enter account ID:")
        passcode = simpledialog.askstring("Login", "Enter passcode:", show="*")
        self.current_account = self.bank.login(account_id, passcode)
        return f"Welcome, {account_id}"

class BankingGUI:
    """Main Graphical Interface for the bank"""
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("LIGHT BANK")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f8ff")

        self.header_font = ("Helvetica", 18, "bold")
        self.button_font = ("Helvetica", 11)
        self.label_font = ("Helvetica", 12)

        self.bg_color = "#5f6464"
        self.button_bg = "#6e7172"
        self.button_active_bg = "#7ceb14"
        self.text_color = "black"
        self.header_color = "#14e722"

        self.display_main_menu()

    def display_main_menu(self):
        self.clear_window()
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(pady=20)

        tk.Label(header_frame, text="LIGHT BANK", font=self.header_font, fg=self.header_color, bg=self.bg_color).pack()
        tk.Label(header_frame, text=" FASTER THAN THE SPEED OF LIGHT  ", font=self.label_font, bg=self.bg_color).pack(pady=10)

        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(expand=True, fill=tk.BOTH, padx=30)

        buttons = [
            (" 1. Create Account", self.create_new_account),
            (" 2. Login", self.login_user),
            (" 3. Exit", self.root.quit)
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, font=self.button_font, bg=self.button_bg,
                            fg=self.text_color, activebackground=self.button_active_bg, activeforeground="white",
                            relief=tk.RAISED, borderwidth=2, command=command)
            btn.pack(fill=tk.X, pady=5, ipady=8)

        tk.Label(self.root, text="BHUTAN BANK", font=("Helvetica", 9), bg=self.bg_color).pack(side=tk.BOTTOM, pady=20)

    def show_account_menu(self):
        self.clear_window()
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(pady=20)

        tk.Label(header_frame, text=f"Account: {self.controller.current_account.id}", font=self.header_font,
                 fg=self.header_color, bg=self.bg_color).pack()

        tk.Label(header_frame, text=f"Balance: Nu: {self.controller.current_account.funds:.2f}",
                 font=("Helvetica", 14, "bold"), bg=self.bg_color).pack(pady=10)

        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(expand=True, fill=tk.BOTH, padx=30)

        operations = [
            (" 1. Check Balance", self.show_balance),
            (" 2. Deposit", self.deposit_funds),
            (" 3. Withdraw", self.withdraw_funds),
            (" 4. Transfer", self.transfer_money),
            (" 5. Mobile Top-up", self.mobile_top_up),
            (" 6. Delete Account", self.remove_account),
            ("  7. Logout", self.logout_account)
        ]

        for text, command in operations:
            btn = tk.Button(button_frame, text=text, font=self.button_font, bg=self.button_bg,
                            fg=self.text_color, activebackground=self.button_active_bg, activeforeground="white",
                            relief=tk.RAISED, borderwidth=2, command=command)
            btn.pack(fill=tk.X, pady=5, ipady=6)

    def create_new_account(self): self._handle_main("1")
    def login_user(self): self._handle_main("2")
    def show_balance(self): self._handle_account("1")
    def deposit_funds(self): self._handle_account("2")
    def withdraw_funds(self): self._handle_account("3")
    def transfer_money(self): self._handle_account("4")
    def mobile_top_up(self): self._handle_account("5")
    def remove_account(self): self._handle_account("6")
    def logout_account(self): self._handle_account("7")

    def _handle_main(self, choice):
        try:
            result = self.controller.processUserInput(choice, True)
            if result == "exit":
                self.root.quit()
            else:
                messagebox.showinfo("Success", result)
                if choice == "2": self.show_account_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _handle_account(self, choice):
        try:
            result = self.controller.processUserInput(choice, False)
            if result == "logout":
                self.display_main_menu()
            else:
                messagebox.showinfo("Success", result)
                self.controller.bank.save_accounts()
                if choice == "6": self.display_main_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()

if __name__ == "__main__":
    bank_system = Banking_system()
    controller = BankingController(bank_system)
    app = BankingGUI(controller)
    app.run()
