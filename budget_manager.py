class BudgetManager:
    def __init__(self):
        self.incomes = {}
        self.expenses = {"Needs": {}, "Wants": {}, "Savings": {}}

    def add_income(self, name, amount):
        self.incomes[name] = amount

    def delete_income(self, name):
        if name in self.incomes:
            del self.incomes[name]
        else:
            print(f"Income '{name}' not found.")

    def add_expense(self, category, name, amount):
        category = category.capitalize()
        if category not in self.expenses:
            print(f"Invalid category. Choose from {list(self.expenses.keys())}.")
            return
        self.expenses[category][name] = amount

    def delete_expense(self, category, name):
        category = category.capitalize()
        if category not in self.expenses:
            print(f"Invalid category. Choose from {list(self.expenses.keys())}.")
            return
        if name in self.expenses[category]:
            del self.expenses[category][name]
        else:
            print(f"Expense '{name}' not found in category '{category}'.")

    def calculate_totals(self):
        total_income = sum(self.incomes.values())
        category_totals = {cat: sum(items.values()) for cat, items in self.expenses.items()}
        total_expenses = sum(category_totals.values())
        remaining_balance = total_income - total_expenses
        return total_income, category_totals, total_expenses, remaining_balance

    def show_summary(self):
        total_income, category_totals, total_expenses, remaining_balance = self.calculate_totals()
        print("\n=== Monthly Budget Summary ===")
        print("\n-- Incomes --")
        if not self.incomes:
            print("No incomes added.")
        else:
            for name, amount in self.incomes.items():
                print(f"  {name}: ${amount:.2f}")
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
        print("\n-- Totals --")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Total Expenses: ${total_expenses:.2f}")
        print(f"Remaining Balance: ${remaining_balance:.2f}")

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    bm = BudgetManager()
    bm.show_summary()
