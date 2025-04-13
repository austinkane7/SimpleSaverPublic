def calculate_retirement(initial_investment, annual_rate, years, yearly_contribution):
    """
    Calculate final retirement balances and safe withdrawal amounts.
    Returns a dictionary with final balances and withdrawal amounts.
    """
    balance_with_contrib = initial_investment
    for _ in range(years):
        balance_with_contrib = (balance_with_contrib + yearly_contribution) * (1 + annual_rate / 100)
    balance_no_contrib = initial_investment * ((1 + annual_rate / 100) ** years)
    annual_withdraw_with_contrib = balance_with_contrib * 0.04
    annual_withdraw_no_contrib = balance_no_contrib * 0.04
    monthly_withdraw_with_contrib = annual_withdraw_with_contrib / 12
    monthly_withdraw_no_contrib = annual_withdraw_no_contrib / 12
    return {
        "balance_with_contrib": round(balance_with_contrib, 2),
        "balance_no_contrib": round(balance_no_contrib, 2),
        "annual_withdraw_with_contrib": round(annual_withdraw_with_contrib, 2),
        "annual_withdraw_no_contrib": round(annual_withdraw_no_contrib, 2),
        "monthly_withdraw_with_contrib": round(monthly_withdraw_with_contrib, 2),
        "monthly_withdraw_no_contrib": round(monthly_withdraw_no_contrib, 2)
    }

def calculate_retirement_yearly(initial_investment, annual_rate, years, yearly_contribution):
    """
    Calculate the balance at the end of each year (with contributions) and without contributions.
    Returns two lists: (balances_with_contrib, balances_without_contrib)
    """
    balances_with = []
    balances_without = []
    current_with = initial_investment
    current_without = initial_investment
    for _ in range(1, years+1):
        current_with = (current_with + yearly_contribution) * (1 + annual_rate / 100)
        balances_with.append(round(current_with,2))
        current_without = current_without * (1+annual_rate/100)
        balances_without.append(round(current_without,2))
    return balances_with, balances_without

if __name__ == "__main__":
    try:
        initial_investment = float(input("Enter starting amount: "))
        annual_rate = float(input("Enter annual rate (in %): "))
        years = int(input("Enter number of years for growth: "))
        yearly_contribution = float(input("Enter yearly contribution: "))
    except ValueError:
        print("Please enter valid numerical values.")
        exit(1)
    results = calculate_retirement(initial_investment, annual_rate, years, yearly_contribution)
    yearly_with, _ = calculate_retirement_yearly(initial_investment, annual_rate, years, yearly_contribution)
    print("\nFinal Results:")
    for key, val in results.items():
        print(f"{key}: {val}")
    print("\nYearly Balances (With Contributions):")
    print(yearly_with)


