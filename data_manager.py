import sqlite3
import json
import datetime

class DataManager:
    def __init__(self, db_name="app_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS retirement_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                balance_with_contrib REAL,
                balance_no_contrib REAL,
                annual_withdraw_with_contrib REAL,
                annual_withdraw_no_contrib REAL,
                monthly_withdraw_with_contrib REAL,
                monthly_withdraw_no_contrib REAL,
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS budget_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                incomes TEXT,
                expenses TEXT,
                total_income REAL,
                total_expenses REAL,
                remaining_balance REAL,
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def save_retirement_result(self, user_id, result):
        created_at = datetime.datetime.now().isoformat()
        query = '''
            INSERT INTO retirement_results (
                user_id, balance_with_contrib, balance_no_contrib,
                annual_withdraw_with_contrib, annual_withdraw_no_contrib,
                monthly_withdraw_with_contrib, monthly_withdraw_no_contrib, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (
            user_id,
            result.get("balance_with_contrib"),
            result.get("balance_no_contrib"),
            result.get("annual_withdraw_with_contrib"),
            result.get("annual_withdraw_no_contrib"),
            result.get("monthly_withdraw_with_contrib"),
            result.get("monthly_withdraw_no_contrib"),
            created_at
        ))
        self.conn.commit()

    def list_retirement_results(self, user_id):
        query = "SELECT id, balance_with_contrib, balance_no_contrib, created_at FROM retirement_results WHERE user_id = ?"
        cursor = self.conn.execute(query, (user_id,))
        results = cursor.fetchall()
        return results

    def delete_retirement_result(self, user_id, result_id):
        query = "DELETE FROM retirement_results WHERE id = ? AND user_id = ?"
        self.conn.execute(query, (result_id, user_id))
        self.conn.commit()

    def save_budget_summary(self, user_id, incomes, expenses, totals):
        created_at = datetime.datetime.now().isoformat()
        incomes_json = json.dumps(incomes)
        expenses_json = json.dumps(expenses)
        query = '''
            INSERT INTO budget_summary (
                user_id, incomes, expenses, total_income, total_expenses, remaining_balance, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.conn.execute(query, (
            user_id,
            incomes_json,
            expenses_json,
            totals.get("total_income"),
            totals.get("total_expenses"),
            totals.get("remaining_balance"),
            created_at
        ))
        self.conn.commit()

    def list_budget_summaries(self, user_id):
        query = "SELECT id, incomes, expenses, total_income, total_expenses, remaining_balance, created_at FROM budget_summary WHERE user_id = ?"
        cursor = self.conn.execute(query, (user_id,))
        results = cursor.fetchall()
        return results

    def delete_budget_summary(self, user_id, summary_id):
        query = "DELETE FROM budget_summary WHERE id = ? AND user_id = ?"
        self.conn.execute(query, (summary_id, user_id))
        self.conn.commit()