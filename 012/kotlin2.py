from decimal import Decimal

# Example accounting-period amounts, not per-trip fares.
platform_revenue = Decimal("50000.00")
operating_costs = Decimal("20000.00")
taxes = Decimal("5000.00")
approved_reserves = Decimal("5000.00")
owner_share_rate = Decimal("0.20")

profit_after_costs_and_taxes = platform_revenue - operating_costs - taxes
distributable_profit = max(
    Decimal("0.00"),
    profit_after_costs_and_taxes - approved_reserves,
)
owner_distribution = distributable_profit * owner_share_rate

print("Distributable profit (EGP):", distributable_profit)
print("Owner distribution (EGP):", owner_distribution)