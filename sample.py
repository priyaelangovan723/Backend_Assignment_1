from collections import defaultdict
import datetime


def get_current_nav(isin):
    # For testing purposes, let's use a fixed NAV value
    return 76.4465



def calculate_portfolio(transactions):
    # Initialize portfolio data
    portfolio = defaultdict(lambda: {
        'units': 0.0, 
        'total_invested': 0.0, 
        'total_redeemed': 0.0, 
        'total_portfolio_value': 0.0, 
        'cashflows': [], 
        'dates': [], 
        'isin': None,
        'gain_loss': 0.0
    })
    
    total_portfolio_value = 0.0
    total_portfolio_gain = 0.0
    
    # Loop through transactions sorted by folio and date (FIFO)
    for tr in sorted(transactions, key=lambda x: (x['folio'], datetime.datetime.strptime(x['trxnDate'], '%d-%b-%Y'))):
        folio = tr['folio']
        scheme_name = tr['schemeName']
        units = float(tr['trxnUnits'])
        trxn_amount = float(tr['trxnAmount'])
        trxn_date = datetime.datetime.strptime(tr['trxnDate'], '%d-%b-%Y')
        current_nav = get_current_nav(tr['isin'])  # Fetch NAV as of today
        
        
        
        # Buy transaction
        if units > 0:
            portfolio[folio]['units'] += units
            portfolio[folio]['total_invested'] += trxn_amount
        
        # Sell transaction (negative units)
        elif units < 0:
            portfolio[folio]['units'] += units  # Deduct sold units
            portfolio[folio]['total_redeemed'] += abs(trxn_amount)  # Record redeemed amount as positive
        
        # Calculate the gain/loss at the folio level
        current_value = portfolio[folio]['units'] * current_nav
        gain_loss = current_value + portfolio[folio]['total_redeemed'] - portfolio[folio]['total_invested']
        portfolio[folio]['gain_loss'] = gain_loss
        
        # Update total portfolio value and gain/loss
    total_portfolio_value += current_value
    total_portfolio_gain += gain_loss
    
    # Final calculation for XIRR and portfolio results
    portfolio_results = []
    for folio, data in portfolio.items():
       
        

       

        portfolio_results.append({
            'folio': folio,
            'schemeName': scheme_name,
            'Net units': data['units'],
            'Total invested': data['total_invested'],
            'Total redeemed': data['total_redeemed'],
            'Net Value as of today': data['units'] * current_nav,
            'Gain/Loss': data['gain_loss']
            
        })
    
    # Append overall portfolio summary
    portfolio_summary = {
        'Total Portfolio Value': total_portfolio_value,
        'Total Portfolio Gain': total_portfolio_gain,
    }

    return portfolio_results, portfolio_summary

# Sample data to test the function
transactions = [
    {
        "trxnDate": "14-FEB-2020",
        "schemeName": "Franklin India Feeder - Franklin U S Opportunities Fund - Direct Plan - Growth",
        "folio": "22399192",
        "trxnUnits": "121.978",
        "purchasePrice": "40.9910",
        "trxnAmount": "5000.00",
        "isin": "INF090I01JR0"
    },
    {
        "trxnDate": "02-MAR-2020",
        "schemeName": "Franklin India Feeder - Franklin U S Opportunities Fund - Direct Plan - Growth",
        "folio": "22399192",
        "trxnUnits": "26.073",
        "purchasePrice": "38.3535",
        "trxnAmount": "1000.00",
        "isin": "INF090I01JR0"
    },
    {
        "trxnDate": "27-APR-2020",
        "schemeName": "Franklin India Feeder - Franklin U S Opportunities Fund - Direct Plan - Growth",
        "folio": "22399192",
        "trxnUnits": "-148.051",
        "purchasePrice": "39.0157",
        "trxnAmount": "-5776.31",
        "isin": "INF090I01JR0"
    }
]

# Call the function to calculate portfolio details
portfolio_results, portfolio_summary = calculate_portfolio(transactions)

# Output the results
print("\n----- Portfolio Details for Each Fund -----\n")
for result in portfolio_results:
    print(f"Scheme Name       : {result['schemeName']}")
    print(f"Folio             : {result['folio']}")
    print(f"Net Units         : {result['Net units']:.3f}")
    print(f"Total Invested    : ₹{result['Total invested']:.2f}")
    print(f"Total Redeemed    : ₹{result['Total redeemed']:.2f}")
    print(f"Net Value Today   : ₹{result['Net Value as of today']:.2f}")
    print(f"Gain/Loss         : ₹{result['Gain/Loss']:.2f}")
    #print(f"XIRR              : {result['XIRR']*100:.2f}%")
    print("-" * 40)

# Display portfolio summary
print("\n----- Portfolio Summary -----\n")
print(f"Total Portfolio Value : ₹{portfolio_summary['Total Portfolio Value']:.2f}")
print(f"Total Portfolio Gain  : ₹{portfolio_summary['Total Portfolio Gain']:.2f}")
print("-" * 40)
