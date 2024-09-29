import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import binascii

class WalletApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CrystalisBaseWallet")
        
        # Load or initialize wallet data
        self.data_file = "wallet_data.json"
        self.load_data()

        # Set a new font
        self.font = ("Helvetica", 12)

        # Create widgets
        self.balance_label = tk.Label(root, text=f"Balance: ${self.balance:.2f}", font=("Helvetica", 16, "bold"))
        self.balance_label.pack(pady=20)

        self.load_coins_button = tk.Button(root, text="Deposit Cheque", command=self.load_coins, font=self.font)
        self.load_coins_button.pack(pady=10)

        self.create_coins_button = tk.Button(root, text="Create New Cheque", command=self.create_coins, font=self.font)
        self.create_coins_button.pack(pady=10)

        self.coin_count_label = tk.Label(root, text="Cheque Balance:", font=self.font)
        self.coin_count_label.pack(pady=5)

        self.coin_count_entry = tk.Entry(root, font=self.font, width=20)
        self.coin_count_entry.pack(pady=5)

        self.transaction_history_label = tk.Label(root, text="Transaction History:", font=self.font)
        self.transaction_history_label.pack(pady=10)

        self.transaction_history = tk.Text(root, height=10, width=50, font=self.font)
        self.transaction_history.pack(pady=10)

        # Load transaction history
        self.load_transaction_history()

        # Set minimum window size
        self.root.minsize(400, 400)

    def load_data(self):
        """Load wallet data from JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                self.balance = data.get("balance", 0.0)
                self.coins = data.get("coins", [])
        else:
            self.balance = 0.0
            self.coins = []
            self.save_data()

    def save_data(self):
        """Save wallet data to JSON file."""
        with open(self.data_file, "w") as file:
            json.dump({"balance": self.balance, "coins": self.coins}, file)

    def load_transaction_history(self):
        """Load transaction history from JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                history = data.get("history", [])
                for entry in history:
                    self.transaction_history.insert(tk.END, entry + "\n")

    def load_coins(self):
        """Load coins from a JSON file and update the master coin list."""
        file_path = filedialog.askopenfilename(title="Select Coin JSON File", filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    imported_coins = json.load(file)
                    total_deposit = len(imported_coins)
                    
                    for coin in imported_coins:
                        if "unminted" in coin:
                            self.coins.append(coin)

                    self.balance += total_deposit
                    self.update_balance()
                    self.add_transaction(f"Deposited {total_deposit} coins.")
            except Exception as e:
                messagebox.showerror("File Error", str(e))

    def create_coins(self):
        """Create a new JSON file for coins."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                count = int(self.coin_count_entry.get())
                if count <= 0:
                    raise ValueError("Number of coins must be positive.")
                if count > len(self.coins):
                    raise ValueError("Not enough coins available to create the new cheque.")

                new_coins = []
                for _ in range(count):
                    coin = self.coins.pop(0)  # Take the first coin from the master list
                    new_coins.append(coin)

                with open(file_path, "w") as file:
                    json.dump(new_coins, file)
                    self.add_transaction(f"Created cheque with {count} coins.")
                    messagebox.showinfo("Success", f"Cheque created successfully with {count} coins.")
                
            except ValueError as ve:
                messagebox.showerror("Input Error", str(ve))
            except Exception as e:
                messagebox.showerror("File Error", str(e))

    def add_transaction(self, entry):
        """Add a transaction to the history and save it."""
        self.transaction_history.insert(tk.END, entry + "\n")
        # Load existing history, add new entry, and save it back
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                history = data.get("history", [])
            history.append(entry)
            data["history"] = history
            with open(self.data_file, "w") as file:
                json.dump(data, file)

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
        self.save_data()

# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    app = WalletApp(root)
    root.mainloop()
