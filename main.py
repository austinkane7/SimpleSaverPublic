import json
from user_manager import UserManager
from data_manager import DataManager
from retirement_calculator import calculate_retirement
from budget_manager import BudgetManager

def login_or_register():
    um = UserManager()
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    user = um.validate_login(email, password)
    if user:
        print("Login successful!")
    else:
        print("User not found or incorrect password. Registering new account.")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        if um.register_user(email, first_name, last_name, password):
            print("Registration successful!")
        else:
            print("Registration failed. Email might already be in use.")
        user = um.validate_login(email, password)
    user_id = user[0]
    return email, user_id

def main():
    email, user_id = login_or_register()
    dm = DataManager()
    bm = BudgetManager()

    while True:
        print("\nSelect an option:")
        print("1. Create new retirement result")
        print("2. View retirement results")
        print("3. Delete a retirement result")
        print("4. Create new budget summary")
        print("5. View budget summaries")
        print("6. Delete a budget summary")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            try:
                initial_investment = float(input("Enter starting amount: "))
                annual_rate = float(input("Enter annual rate (in %): "))
                years = int(input("Enter number of years: "))
                yearly_contribution = float(input("Enter yearly contribution: "))
            except ValueError:
                print("Invalid input, please try again.")
                continue
            result = calculate_retirement(initial_investment, annual_rate, years, yearly_contribution)
            dm.save_retirement_result(user_id, result)
            print("Retirement result saved.")
        elif choice == '2':
            results = dm.list_retirement_results(user_id)
            if results:
                for row in results:
                    rid, balance_with, balance_no, created_at = row
                    print(f"ID: {rid} | With Contrib: ${balance_with:.2f} | No Contrib: ${balance_no:.2f} | Date: {created_at}")
            else:
                print("No retirement results found.")
        elif choice == '3':
            rid = input("Enter the ID of the retirement result to delete: ")
            dm.delete_retirement_result(user_id, rid)
            print("Retirement result deleted.")
        elif choice == '4':
            # Interactive input for incomes
            incomes = {}
            while True:
                add_income = input("Would you like to add an income entry? (y/n): ")
                if add_income.lower() != 'y':
                    break
                iname = input("Enter income name: ")
                try:
                    iamount = float(input("Enter amount for this income: "))
                except ValueError:
                    print("Invalid amount.")
                    continue
                incomes[iname] = iamount

            # Interactive input for expenses per category
            expenses = {"Needs": {}, "Wants": {}, "Savings": {}}
            for category in expenses.keys():
                while True:
                    add_expense = input(f"Would you like to add a {category} expense entry? (y/n): ")
                    if add_expense.lower() != 'y':
                        break
                    ename = input(f"Enter {category} expense name: ")
                    try:
                        eamount = float(input("Enter amount for this expense: "))
                    except ValueError:
                        print("Invalid amount.")
                        continue
                    expenses[category][ename] = eamount

            total_income = sum(incomes.values())
            total_expenses = sum(sum(cat.values()) for cat in expenses.values())
            totals = {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "remaining_balance": total_income - total_expenses
            }
            dm.save_budget_summary(user_id, incomes, expenses, totals)
            print("Budget summary saved.")
        elif choice == '5':
            summaries = dm.list_budget_summaries(user_id)
            if summaries:
                print("Budget Summaries:")
                for row in summaries:
                    bid, incomes_json, expenses_json, total_income, total_expenses, remaining_balance, created_at = row
                    print(f"ID: {bid} | Date: {created_at} | Total Income: ${total_income:.2f} | Total Expenses: ${total_expenses:.2f} | Remaining: ${remaining_balance:.2f}")
                view_detail = input("Would you like to view a detailed summary? (y/n): ")
                if view_detail.lower() == 'y':
                    summary_id = input("Enter the ID of the budget summary to view in detail: ")
                    found = False
                    for row in summaries:
                        if str(row[0]) == summary_id:
                            found = True
                            bid, incomes_json, expenses_json, total_income, total_expenses, remaining_balance, created_at = row
                            incomes = json.loads(incomes_json)
                            expenses = json.loads(expenses_json)
                            print(f"\nDetailed Budget Summary (ID: {bid}, Date: {created_at}):")
                            print("\nIncomes:")
                            for key, val in incomes.items():
                                print(f"  {key}: ${val:.2f}")
                            print("\nExpenses:")
                            for cat, items in expenses.items():
                                cat_total = sum(items.values())
                                percentage = (cat_total / total_income * 100) if total_income else 0
                                print(f"  {cat}:")
                                for name, amount in items.items():
                                    print(f"    {name}: ${amount:.2f}")
                                print(f"    Total {cat}: ${cat_total:.2f} ({percentage:.2f}% of total income)")
                            print(f"\nOverall Totals:")
                            print(f"  Total Income: ${total_income:.2f}")
                            print(f"  Total Expenses: ${total_expenses:.2f}")
                            print(f"  Remaining Balance: ${remaining_balance:.2f}")
                            break
                    if not found:
                        print("Budget summary not found.")
            else:
                print("No budget summaries found.")
        elif choice == '6':
            bid = input("Enter the ID of the budget summary to delete: ")
            dm.delete_budget_summary(user_id, bid)
            print("Budget summary deleted.")
        elif choice == '7':
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()