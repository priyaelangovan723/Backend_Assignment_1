from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import mstarpy
import secrets

secret_key = secrets.token_hex(16)  
print(secret_key)


app = Flask(__name__)
app.secret_key = '5553c57fb7484cb90428566a5971bd34' 

CACHE_DIR = "nav_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Function to fetch NAV (with error handling)
def get_current_nav(isin):
    cache_file = os.path.join(CACHE_DIR, f"{isin}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return json.load(file)['nav']
    
    try:
        
        fund = mstarpy.Funds(term=isin, country="in")
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=1)
        history = fund.nav(start_date=start_date, end_date=end_date, frequency="daily")
        
        if not history:
            raise ValueError(f"No NAV data found for ISIN: {isin}")
        
        if isinstance(history, list) and len(history) > 0 and 'nav' in history[-1]:
            return history[-1]['nav']
        
        raise ValueError(f"'nav' key not found in NAV history for ISIN: {isin}")
    
    except ValueError as ve:
        flash(f"Error fetching NAV for ISIN {isin}: {ve}", 'error')
        return 0.0
    except Exception as e:
        flash(f"Unexpected error fetching NAV for ISIN {isin}: {e}", 'error')
        return 0.0


def fetch_navs_in_parallel(isins):
    """Fetch NAVs for all ISINs in parallel."""
    nav_cache = {}
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_isin = {executor.submit(get_current_nav, isin): isin for isin in isins}
        for future in as_completed(future_to_isin):
            isin = future_to_isin[future]
            nav_cache[isin] = future.result()

    return nav_cache

def calculate_portfolio(transactions):
    portfolio = {}
    
    # Collect unique ISINs
    isins = {tr['isin'] for tr in transactions}
    nav_cache = fetch_navs_in_parallel(isins)

    total_portfolio_value = 0.0
    total_portfolio_gain = 0.0

    for tr in sorted(transactions, key=lambda x: (x['folio'], datetime.datetime.strptime(x['trxnDate'], '%d-%b-%Y'))):
        folio = tr['folio']
        scheme_name = tr['schemeName']
        units = float(tr['trxnUnits'])
        trxn_amount = float(tr['trxnAmount'])
        current_nav = nav_cache.get(tr['isin'], 0.0)

        if folio not in portfolio:
            portfolio[folio] = {
                'units': 0.0, 
                'total_invested': 0.0, 
                'total_redeemed': 0.0, 
                'schemeName': scheme_name,  
                'gain_loss': 0.0
            }

        portfolio[folio]['units'] += units
        if units > 0:
            portfolio[folio]['total_invested'] += trxn_amount
        else:
            portfolio[folio]['total_redeemed'] += abs(trxn_amount)

        current_value = portfolio[folio]['units'] * current_nav
        gain_loss = current_value + portfolio[folio]['total_redeemed'] - portfolio[folio]['total_invested']
        portfolio[folio]['gain_loss'] = gain_loss
        total_portfolio_value += current_value
        total_portfolio_gain += gain_loss
    
    portfolio_results = []
    for folio, data in portfolio.items():
        portfolio_results.append({
            'folio': folio,
            'schemeName': data['schemeName'],
            'Net units': data['units'],
            'Total invested': data['total_invested'],
            'Total redeemed': data['total_redeemed'],
            'Net Value as of today': data['units'] * nav_cache.get(folio, 0.0),
            'Gain/Loss': data['gain_loss']
        })
    
    portfolio_summary = {
        'Total Portfolio Value': total_portfolio_value,
        'Total Portfolio Gain': total_portfolio_gain,
    }

    return portfolio_results, portfolio_summary

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    transactions = load_transactions(file)
    if transactions:
        portfolio_results, portfolio_summary = calculate_portfolio(transactions)
        return render_template('results.html', results=portfolio_results, summary=portfolio_summary)

    flash('Error loading transactions', 'error')
    return redirect(url_for('index'))

def load_transactions(file):
    """Load transactions from a JSON file."""
    try:
        data = json.load(file)
        if 'data' in data and isinstance(data['data'], list) and 'dtTransaction' in data['data'][0]:
            return data['data'][0]['dtTransaction']
        else:
            return None
    except Exception as e:
        flash(f"Error loading file: {e}", 'error')
        return None

if __name__ == "__main__":
    app.run(debug=True)
