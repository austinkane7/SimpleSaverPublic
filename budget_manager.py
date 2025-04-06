class BudgetManager:
    def __init__(self):
        # Store incomes in a simple dictionary
        self.incomes = {}  # e.g., {"Salary": 5000.00, "Freelance": 800.00}
        # Store expenses as a dictionary of categories, each with its own dictionary of items.
        self.expenses = {
            "Needs": {},
            "Wants": {},
            "Savings": {}
        }

    def add_income(self, name, amount):
        """Adds or updates an income entry."""
        self.incomes[name] = amount

    def delete_income(self, name):
        """Removes an income entry if it exists."""
        if name in self.incomes:
            del self.incomes[name]
        else:
            print(f"Income '{name}' not found.")

    def add_expense(self, category, name, amount):
        """
        Adds or updates an expense entry under a given category.
        Valid categories are "Needs", "Wants", and "Savings".
        """
        category = category.capitalize()
        if category not in self.expenses:
            print(f"Invalid category. Please choose from {list(self.expenses.keys())}.")
            return
        self.expenses[category][name] = amount

    def delete_expense(self, category, name):
        """
        Removes an expense entry from the specified category if it exists.
        """
        category = category.capitalize()
        if category not in self.expenses:
            print(f"Invalid category. Please choose from {list(self.expenses.keys())}.")
            return
        if name in self.expenses[category]:
            del self.expenses[category][name]
        else:
            print(f"Expense '{name}' not found in category '{category}'.")

    def calculate_totals(self):
        """
        Calculates total incomes, expenses per category, overall expenses, and remaining balance.
        """
        total_income = sum(self.incomes.values())
        category_totals = {cat: sum(items.values()) for cat, items in self.expenses.items()}
        total_expenses = sum(category_totals.values())
        remaining_balance = total_income - total_expenses
        return total_income, category_totals, total_expenses, remaining_balance

    def show_summary(self):
        """Displays a detailed summary with incomes, categorized expenses, and totals."""
        total_income, category_totals, total_expenses, remaining_balance = self.calculate_totals()
        print("\n=== Monthly Budget Summary ===")

        # Display incomes
        print("\n-- Incomes --")
        if not self.incomes:
            print("No incomes added.")
        else:
            for name, amount in self.incomes.items():
                print(f"  {name}: ${amount:.2f}")

        # Display expenses by category
        for category in self.expenses:
            print(f"\n-- {category} Expenses --")
            if not self.expenses[category]:
                print(f"No {category.lower()} expenses added.")
            else:
                for name, amount in self.expenses[category].items():
                    print(f"  {name}: ${amount:.2f}")
            cat_total = category_totals.get(category, 0)
            percentage = (cat_total / total_income * 100) if total_income else 0
            print(f"  Total {category}: ${cat_total:.2f} ({percentage:.2f}% of total income)")

        # Display overall totals
        print("\n-- Totals --")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Total Expenses: ${total_expenses:.2f}")
        print(f"Remaining Balance: ${remaining_balance:.2f}")


def main():
    budget_manager = BudgetManager()
    while True:
        print("\nSelect an option:")
        print("1. Add Income")
        print("2. Delete Income")
        print("3. Add Expense")
        print("4. Delete Expense")
        print("5. Show Budget Summary")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            name = input("Enter income name: ")
            try:
                amount = float(input("Enter monthly amount for this income: "))
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
                continue
            budget_manager.add_income(name, amount)
            print(f"Income '{name}' added.")

        elif choice == '2':
            name = input("Enter the name of the income to delete: ")
            budget_manager.delete_income(name)

        elif choice == '3':
            category = input("Enter expense category (Needs, Wants, Savings): ")
            name = input("Enter expense name: ")
            try:
                amount = float(input("Enter monthly amount for this expense: "))
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
                continue
            budget_manager.add_expense(category, name, amount)
            print(f"Expense '{name}' added under category '{category.capitalize()}'.")

        elif choice == '4':
            category = input("Enter expense category (Needs, Wants, Savings): ")
            name = input("Enter the name of the expense to delete: ")
            budget_manager.delete_expense(category, name)

        elif choice == '5':
            budget_manager.show_summary()

        elif choice == '6':
            print("Exiting the budget manager.")
            break
        else:
            print("Invalid choice. Please select an option from 1 to 6.")


if __name__ == '__main__':
    main()