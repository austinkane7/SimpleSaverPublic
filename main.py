import sys
import json
import datetime
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QTabWidget,
    QLineEdit, QPushButton, QLabel, QFormLayout, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from user_manager import UserManager
from data_manager import DataManager
from retirement_calculator import calculate_retirement, calculate_retirement_yearly
from budget_manager import BudgetManager
from profile_widget import ProfileWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# --- Bar Chart Widget for Retirement Calculation ---
class BarChartWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(5, 3))
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)

    def update_chart(self, yearly_with, yearly_without):
        self.axes.clear()
        n = len(yearly_with)
        x = np.arange(n)
        width = 0.35
        # Convert values to millions:
        yearly_with_m = [val / 1e6 for val in yearly_with]
        yearly_without_m = [val / 1e6 for val in yearly_without]
        self.axes.bar(x - width / 2, yearly_with_m, width, label="With Contribution", color='blue')
        self.axes.bar(x + width / 2, yearly_without_m, width, label="Without Contribution", color='orange')
        self.axes.set_xlabel("Year")
        self.axes.set_ylabel("Balance (in millions of $)")
        self.axes.set_title("Yearly Balance")
        self.axes.legend()
        self.draw()


# --- Pie Chart Widget for Budget Summary ---
class PieChartWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(3, 3))
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)

    def update_chart(self, expenses, incomes):
        self.axes.clear()
        labels = []
        sizes = []
        for category, items in expenses.items():
            total = sum(items.values())
            labels.append(category)
            sizes.append(total)
        if sum(sizes) == 0:
            self.axes.text(0.5, 0.5, "No Expenses", horizontalalignment='center', verticalalignment='center')
        else:
            self.axes.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        self.draw()


# --- Retirement Calculator Tab Widget ---
class RetirementTabWidget(QWidget):
    def __init__(self, dm, user_id, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.user_id = user_id
        self.initUI()
        self.loadData()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.lastSavedLabel = QLabel("Last Saved: N/A")
        formLayout = QFormLayout()
        self.initialEdit = QLineEdit()
        self.rateEdit = QLineEdit()
        self.yearsEdit = QLineEdit()
        self.contributionEdit = QLineEdit()
        self.calculateButton = QPushButton("Calculate & Save")
        self.resultLabel = QLabel("")
        formLayout.addRow("Starting Amount:", self.initialEdit)
        formLayout.addRow("Annual Rate (%):", self.rateEdit)
        formLayout.addRow("Years:", self.yearsEdit)
        formLayout.addRow("Yearly Contribution:", self.contributionEdit)
        formLayout.addRow(self.calculateButton)
        formLayout.addRow("Result:", self.resultLabel)
        self.barChart = BarChartWidget()
        self.layout.addWidget(self.lastSavedLabel)
        self.layout.addLayout(formLayout)
        self.layout.addWidget(self.barChart)
        self.setLayout(self.layout)
        self.calculateButton.clicked.connect(self.calculateAndSave)

    def loadData(self):
        data = self.dm.get_retirement_result(self.user_id)
        if data:
            # data: (id, user_id, name, starting_amount, annual_rate, years, yearly_contribution,
            #        balance_with_contrib, balance_no_contrib, annual_withdraw_with_contrib,
            #        annual_withdraw_no_contrib, monthly_withdraw_with_contrib, monthly_withdraw_no_contrib, created_at)
            self.lastSavedLabel.setText(f"Retirement Calculation Saved: {data[2]}")
            self.initialEdit.setText(str(data[3]))
            self.rateEdit.setText(str(data[4]))
            self.yearsEdit.setText(str(data[5]))
            self.contributionEdit.setText(str(data[6]))
            result_text = (
                f"With Contribution: ${data[7]}\n"
                f"Without Contribution: ${data[8]}\n"
                f"Annual Withdrawal (With): ${data[9]}\n"
                f"Annual Withdrawal (Without): ${data[10]}\n"
                f"Monthly Withdrawal (With): ${data[11]}\n"
                f"Monthly Withdrawal (Without): ${data[12]}"
            )
            self.resultLabel.setText(result_text)
            try:
                years = int(data[5])
                initial = float(data[3])
                rate = float(data[4])
                contribution = float(data[6])
                yearly_with, yearly_without = calculate_retirement_yearly(initial, rate, years, contribution)
                self.barChart.update_chart(yearly_with, yearly_without)
            except Exception:
                pass

    def calculateAndSave(self):
        try:
            initial = float(self.initialEdit.text())
            rate = float(self.rateEdit.text())
            years = int(self.yearsEdit.text())
            contribution = float(self.contributionEdit.text())
        except ValueError:
            self.resultLabel.setText("Invalid input.")
            return
        result = calculate_retirement(initial, rate, years, contribution)
        # Use current timestamp as save name
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.dm.upsert_retirement_result(self.user_id, initial, rate, years, contribution, result)
        result_text = (
            f"Retirement Results:\n"
            f"Saved on: {current_time}\n"
            f"With Contribution: ${result['balance_with_contrib']}\n"
            f"Without Contribution: ${result['balance_no_contrib']}\n"
            f"Annual Withdrawal (With): ${result['annual_withdraw_with_contrib']}\n"
            f"Annual Withdrawal (Without): ${result['annual_withdraw_no_contrib']}\n"
            f"Monthly Withdrawal (With): ${result['monthly_withdraw_with_contrib']}\n"
            f"Monthly Withdrawal (Without): ${result['monthly_withdraw_no_contrib']}"
        )
        self.resultLabel.setText(result_text)
        self.lastSavedLabel.setText(f"Retirement Calculation Saved: {current_time}")
        yearly_with, yearly_without = calculate_retirement_yearly(initial, rate, years, contribution)
        self.barChart.update_chart(yearly_with, yearly_without)


# --- Budget Summary Tab Widget ---
class BudgetTabWidget(QWidget):
    def __init__(self, dm, user_id, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.user_id = user_id
        self.incomes = {}
        self.expenses = {"Needs": {}, "Wants": {}, "Savings": {}}
        self.initUI()
        self.loadData()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.lastSavedLabel = QLabel("Budget Saved: N/A")
        self.incomeLabel = QLabel("Incomes:")
        self.incomeList = QLabel("")
        self.addIncomeButton = QPushButton("Add Income")
        self.removeIncomeButton = QPushButton("Remove Income")
        self.expenseLabel = QLabel("Expenses:")
        self.expenseList = QLabel("")
        self.addExpenseButton = QPushButton("Add Expense")
        self.removeExpenseButton = QPushButton("Remove Expense")
        self.saveBudgetButton = QPushButton("Save Budget Summary")
        self.messageLabel = QLabel("")
        self.savingsLabel = QLabel("")
        self.pieChart = PieChartWidget()
        self.layout.addWidget(self.lastSavedLabel)
        self.layout.addWidget(self.incomeLabel)
        self.layout.addWidget(self.incomeList)
        self.layout.addWidget(self.addIncomeButton)
        self.layout.addWidget(self.removeIncomeButton)
        self.layout.addWidget(self.expenseLabel)
        self.layout.addWidget(self.expenseList)
        self.layout.addWidget(self.addExpenseButton)
        self.layout.addWidget(self.removeExpenseButton)
        self.layout.addWidget(self.saveBudgetButton)
        self.layout.addWidget(self.messageLabel)
        self.layout.addWidget(self.savingsLabel)
        self.layout.addWidget(self.pieChart)
        self.setLayout(self.layout)
        self.addIncomeButton.clicked.connect(self.addIncome)
        self.removeIncomeButton.clicked.connect(self.removeIncome)
        self.addExpenseButton.clicked.connect(self.addExpense)
        self.removeExpenseButton.clicked.connect(self.removeExpense)
        self.saveBudgetButton.clicked.connect(self.saveBudget)

    def loadData(self):
        data = self.dm.get_budget_summary(self.user_id)
        if data:
            self.lastSavedLabel.setText(f"Budget Saved: {data[2]}")
            try:
                self.incomes = json.loads(data[3])
            except Exception:
                self.incomes = {}
            try:
                self.expenses = json.loads(data[4])
            except Exception:
                self.expenses = {"Needs": {}, "Wants": {}, "Savings": {}}
            self.updateIncomeList()
            self.updateExpenseList()

    def addIncome(self):
        iname, ok = QInputDialog.getText(self, "Add Income", "Enter income name:")
        if not ok or not iname:
            return
        iamount, ok = QInputDialog.getDouble(self, "Add Income", "Enter income amount:")
        if not ok:
            return
        self.incomes[iname] = iamount
        self.updateIncomeList()

    def removeIncome(self):
        if not self.incomes:
            QMessageBox.information(self, "Remove Income", "No incomes to remove.")
            return
        income_names = list(self.incomes.keys())
        item, ok = QInputDialog.getItem(self, "Remove Income", "Select income to remove:", income_names, 0, False)
        if ok and item:
            del self.incomes[item]
            self.updateIncomeList()

    def updateIncomeList(self):
        text = ""
        for key, value in self.incomes.items():
            text += f"{key}: ${value:.2f}\n"
        self.incomeList.setText(text)
        self.updateSavingsLabel()
        self.updatePieChart()

    def addExpense(self):
        categories = ["Needs", "Wants", "Savings"]
        cat, ok = QInputDialog.getItem(self, "Add Expense", "Select category:", categories, 0, False)
        if not ok:
            return
        ename, ok = QInputDialog.getText(self, "Add Expense", f"Enter {cat} expense name:")
        if not ok or not ename:
            return
        eamount, ok = QInputDialog.getDouble(self, "Add Expense", "Enter expense amount:")
        if not ok:
            return
        self.expenses[cat][ename] = eamount
        self.updateExpenseList()

    def removeExpense(self):
        available_categories = [cat for cat, items in self.expenses.items() if items]
        if not available_categories:
            QMessageBox.information(self, "Remove Expense", "No expenses to remove.")
            return
        cat, ok = QInputDialog.getItem(self, "Remove Expense", "Select expense category:", available_categories, 0,
                                       False)
        if not ok or not cat:
            return
        expense_names = list(self.expenses[cat].keys())
        item, ok = QInputDialog.getItem(self, "Remove Expense", f"Select {cat} expense to remove:", expense_names, 0,
                                        False)
        if ok and item:
            del self.expenses[cat][item]
            self.updateExpenseList()

    def updateExpenseList(self):
        text = ""
        for cat, items in self.expenses.items():
            text += f"{cat}:\n"
            for key, value in items.items():
                text += f"  {key}: ${value:.2f}\n"
            total = sum(items.values())
            percentage = (total / sum(self.incomes.values()) * 100) if self.incomes else 0
            text += f"  Total {cat}: ${total:.2f} ({percentage:.2f}% of total income)\n"
        self.expenseList.setText(text)
        self.updateSavingsLabel()
        self.updatePieChart()

    def updateSavingsLabel(self):
        total_income = sum(self.incomes.values())
        total_expenses = sum(sum(items.values()) for items in self.expenses.values())
        remaining = total_income - total_expenses
        if total_income == 0:
            self.savingsLabel.setText("")
        else:
            if remaining >= 0:
                self.savingsLabel.setText(f"Money left for savings: ${remaining:.2f}")
            else:
                self.savingsLabel.setText(f"Overspending by: ${abs(remaining):.2f} per month")

    def updatePieChart(self):
        self.pieChart.update_chart(self.expenses, self.incomes)

    def saveBudget(self):
        total_income = sum(self.incomes.values())
        total_expenses = sum(sum(items.values()) for items in self.expenses.values())
        totals = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "remaining_balance": total_income - total_expenses
        }
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.dm.upsert_budget_summary(self.user_id, self.incomes, self.expenses, totals)
        self.messageLabel.setText("Budget summary saved.")
        self.lastSavedLabel.setText(f"Budget Saved: {current_time}")
        self.updateSavingsLabel()
        self.updatePieChart()


# --- Dashboard Widget (contains tabs for Retirement, Budget, and Profile) ---
class DashboardWidget(QWidget):
    def __init__(self, email, user_id, parent=None):
        super().__init__(parent)
        self.email = email
        self.user_id = user_id
        self.dm = DataManager()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.retirementTab = RetirementTabWidget(self.dm, self.user_id)
        self.budgetTab = BudgetTabWidget(self.dm, self.user_id)
        self.profileTab = ProfileWidget(self.email, self.user_id)
        self.tabs.addTab(self.retirementTab, "Retirement Calculator")
        self.tabs.addTab(self.budgetTab, "Budget Summary")
        self.tabs.addTab(self.profileTab, "Profile")
        layout.addWidget(self.tabs)
        self.setLayout(layout)


# --- Login Widget ---
class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.um = UserManager()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.emailEdit = QLineEdit()
        self.emailEdit.setPlaceholderText("Email")
        self.passwordEdit = QLineEdit()
        self.passwordEdit.setPlaceholderText("Password")
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.loginButton = QPushButton("Login")
        self.registerButton = QPushButton("Register")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.emailEdit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.passwordEdit)
        layout.addWidget(self.loginButton)
        layout.addWidget(self.registerButton)
        self.setLayout(layout)
        self.loginButton.clicked.connect(self.handleLogin)
        self.registerButton.clicked.connect(self.handleRegister)

    def handleLogin(self):
        email = self.emailEdit.text()
        password = self.passwordEdit.text()
        user = self.um.validate_login(email, password)
        if user:
            self.window().switchToDashboard(email, user[0])
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect email or password.")

    def handleRegister(self):
        email = self.emailEdit.text()
        password = self.passwordEdit.text()
        first_name, ok1 = QInputDialog.getText(self, "Register", "Enter First Name:")
        if not ok1:
            return
        last_name, ok2 = QInputDialog.getText(self, "Register", "Enter Last Name:")
        if not ok2:
            return
        if self.um.register_user(email, first_name, last_name, password):
            QMessageBox.information(self, "Registration Successful", "You are now registered. Please log in.")
        else:
            QMessageBox.warning(self, "Registration Failed", "Registration failed. Email may be in use.")


# --- Main Window with QStackedWidget to switch between Login and Dashboard ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Saver")
        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)
        self.loginWidget = LoginWidget(self)
        self.stack.addWidget(self.loginWidget)

    def switchToDashboard(self, email, user_id):
        self.dashboardWidget = DashboardWidget(email, user_id, self)
        self.stack.addWidget(self.dashboardWidget)
        self.stack.setCurrentWidget(self.dashboardWidget)

    def switchToLogin(self):
        self.stack.setCurrentWidget(self.loginWidget)


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    from data_manager import DataManager  # Ensure this import works here

    main()








