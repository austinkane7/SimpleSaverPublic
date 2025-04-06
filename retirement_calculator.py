def calculate_retirement(initial_investment, annual_rate, years, yearly_contribution):
    """
    Calculate retirement portfolio balances and safe withdrawal amounts.

    Parameters:
        initial_investment (float): The starting amount.
        annual_rate (float): The annual growth rate in percent.
        years (int): Number of years for growth.
        yearly_contribution (float): The annual contribution amount.

    Returns:
        dict: A dictionary containing:
            - 'balance_with_contrib': Final balance with yearly contributions.
            - 'balance_no_contrib': Final balance without any further contributions.
            - 'annual_withdraw_with_contrib': 4% annual withdrawal of the contributed balance.
            - 'annual_withdraw_no_contrib': 4% annual withdrawal of the non-contributed balance.
            - 'monthly_withdraw_with_contrib': Monthly equivalent of the above annual amount.
            - 'monthly_withdraw_no_contrib': Monthly equivalent of the above annual amount.
    """
    # Scenario 1: With continued contributions
    balance_with_contrib = initial_investment
    for _ in range(years):
        balance_with_contrib = (balance_with_contrib + yearly_contribution) * (1 + annual_rate / 100)

    # Scenario 2: Without further contributions (only compound the initial investment)
    balance_no_contrib = initial_investment * ((1 + annual_rate / 100) ** years)

    # Calculate 4% rule withdrawals
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

    print("\n=== With Continued Contributions ===")
    print(f"Total investment after {years} years: ${results['balance_with_contrib']}")
    print(f"Annual withdrawal (4% rule): ${results['annual_withdraw_with_contrib']}")
    print(f"Monthly withdrawal: ${results['monthly_withdraw_with_contrib']}")

    print("\n=== Without Further Contributions ===")
    print(f"Total investment after {years} years: ${results['balance_no_contrib']}")
    print(f"Annual withdrawal (4% rule): ${results['annual_withdraw_no_contrib']}")
    print(f"Monthly withdrawal: ${results['monthly_withdraw_no_contrib']}")
