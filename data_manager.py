import sqlite3
import json
import datetime

class DataManager:
    def __init__(self, db_name="app_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        # In each table, the "name" field will hold the save timestamp.
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS retirement_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                starting_amount REAL,
                annual_rate REAL,
                years INTEGER,
                yearly_contribution REAL,
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
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
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

    def upsert_retirement_result(self, user_id, starting_amount, annual_rate, years, yearly_contribution, result):
        save_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.datetime.now().isoformat()
        query = "SELECT id FROM retirement_results WHERE user_id = ?"
        cursor = self.conn.execute(query, (user_id,))
        existing = cursor.fetchone()
        if existing:
            update_query = '''
                UPDATE retirement_results 
                SET name = ?, starting_amount = ?, annual_rate = ?, years = ?,
                    yearly_contribution = ?, balance_with_contrib = ?,
                    balance_no_contrib = ?, annual_withdraw_with_contrib = ?,
                    annual_withdraw_no_contrib = ?, monthly_withdraw_with_contrib = ?,
                    monthly_withdraw_no_contrib = ?, created_at = ?
                WHERE user_id = ?
            '''
            self.conn.execute(update_query, (
                save_timestamp,
                starting_amount,
                annual_rate,
                years,
                yearly_contribution,
                result.get("balance_with_contrib"),
                result.get("balance_no_contrib"),
                result.get("annual_withdraw_with_contrib"),
                result.get("annual_withdraw_no_contrib"),
                result.get("monthly_withdraw_with_contrib"),
                result.get("monthly_withdraw_no_contrib"),
                created_at,
                user_id
            ))
        else:
            insert_query = '''
                INSERT INTO retirement_results (
                    user_id, name, starting_amount, annual_rate, years, yearly_contribution,
                    balance_with_contrib, balance_no_contrib,
                    annual_withdraw_with_contrib, annual_withdraw_no_contrib,
                    monthly_withdraw_with_contrib, monthly_withdraw_no_contrib, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.conn.execute(insert_query, (
                user_id,
                save_timestamp,
                starting_amount,
                annual_rate,
                years,
                yearly_contribution,
                result.get("balance_with_contrib"),
                result.get("balance_no_contrib"),
                result.get("annual_withdraw_with_contrib"),
                result.get("annual_withdraw_no_contrib"),
                result.get("monthly_withdraw_with_contrib"),
                result.get("monthly_withdraw_no_contrib"),
                created_at
            ))
        self.conn.commit()

    def get_retirement_result(self, user_id):
        query = "SELECT * FROM retirement_results WHERE user_id = ?"
        cursor = self.conn.execute(query, (user_id,))
        return cursor.fetchone()

    def upsert_budget_summary(self, user_id, incomes, expenses, totals):
        save_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.datetime.now().isoformat()
        incomes_json = json.dumps(incomes)
        expenses_json = json.dumps(expenses)
        query = "SELECT id FROM budget_summary WHERE user_id = ?"
        cursor = self.conn.execute(query, (user_id,))
        existing = cursor.fetchone()
        if existing:
            update_query = '''
                UPDATE budget_summary 
                SET name = ?, incomes = ?, expenses = ?, total_income = ?,
                    total_expenses = ?, remaining_balance = ?, created_at = ?
                WHERE user_id = ?
            '''
            self.conn.execute(update_query, (
                save_timestamp,
                incomes_json,
                expenses_json,
                totals.get("total_income"),
                totals.get("total_expenses"),
                totals.get("remaining_balance"),
                created_at,
                user_id
            ))
        else:
            insert_query = '''
                INSERT INTO budget_summary (
                    user_id, name, incomes, expenses, total_income, total_expenses, remaining_balance, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.conn.execute(insert_query, (
                user_id,
                save_timestamp,
                incomes_json,
                expenses_json,
                totals.get("total_income"),
                totals.get("total_expenses"),
                totals.get("remaining_balance"),
                created_at
            ))
        self.conn.commit()

    def get_budget_summary(self, user_id):
        query = "SELECT * FROM budget_summary WHERE user_id = ?"
        cursor = self.conn.execute(query, (user_id,))
        return cursor.fetchone()

if __name__ == "__main__":
    dm = DataManager()


