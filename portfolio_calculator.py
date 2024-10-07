import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import mstarpy
import threading

import time
import os
import mstarpy

# Cache directory
CACHE_DIR = "nav_cache"

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def get_current_nav(isin):
    cache_file = os.path.join(CACHE_DIR, f"{isin}.json")
    # Check if the NAV is already cached
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return json.load(file)['nav']
    
    # Fetch NAV from the API
    try:
        fund = mstarpy.Funds(term=isin, country="in")
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=1)
        history = fund.nav(start_date=start_date, end_date=end_date, frequency="daily")

        if not history or 'nav' not in history[-1]:
            raise ValueError(f"No valid NAV data found for ISIN: {isin}")

        # Cache the result
        with open(cache_file, 'w') as file:
            json.dump({'nav': history[-1]['nav']}, file)

        return history[-1]['nav']

    except Exception as e:
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

    # Process transactions
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

# GUI setup
def main_gui():
    root = tk.Tk()
    root.title("Portfolio Calculator")
    root.geometry("700x500")

    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            file_label.config(text=f"Uploaded File: {file_path.split('/')[-1]}")
            transactions = load_transactions(file_path)
            if transactions:
                result_text.delete(1.0, tk.END)  
                result_text.insert(tk.END, "Processing data...\n")  
               
                threading.Thread(target=process_data, args=(transactions,)).start()

    def process_data(transactions):
        start_time = time.time() 
        portfolio_results, portfolio_summary = calculate_portfolio(transactions)
        end_time = time.time()
        display_results(portfolio_results, portfolio_summary)
        print(f"Processing completed in {end_time - start_time:.2f} seconds")

    def display_results(results, summary):
        result_text.delete(1.0, tk.END)  
        result_text.insert(tk.END, "----- Portfolio Details for Each Fund -----\n\n")
        for result in results:
            result_text.insert(tk.END, f"Scheme Name       : {result['schemeName']}\n")
            result_text.insert(tk.END, f"Folio             : {result['folio']}\n")
            result_text.insert(tk.END, f"Net Units         : {result['Net units']:.3f}\n")
            result_text.insert(tk.END, f"Total Invested    : ₹{result['Total invested']:.2f}\n")
            result_text.insert(tk.END, f"Total Redeemed    : ₹{result['Total redeemed']:.2f}\n")
            result_text.insert(tk.END, f"Net Value Today   : ₹{result['Net Value as of today']:.2f}\n")
            result_text.insert(tk.END, f"Gain/Loss         : ₹{result['Gain/Loss']:.2f}\n")
            result_text.insert(tk.END, "-" * 40 + "\n")
        
        result_text.insert(tk.END, "\n----- Portfolio Summary -----\n\n")
        result_text.insert(tk.END, f"Total Portfolio Value : ₹{summary['Total Portfolio Value']:.2f}\n")
        result_text.insert(tk.END, f"Total Portfolio Gain  : ₹{summary['Total Portfolio Gain']:.2f}\n")
        result_text.insert(tk.END, "-" * 40 + "\n")

    # GUI Widgets
    load_button = tk.Button(root, text="Load Transaction File", command=load_file, width=25)
    load_button.pack(pady=10)

    file_label = tk.Label(root, text="No file uploaded", font=("Arial", 10))
    file_label.pack(pady=10)

    result_text = tk.Text(root, height=20, width=70)
    result_text.pack(pady=20)

    root.mainloop()

def load_transactions(file_path):
    """Load transactions from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if 'data' in data and isinstance(data['data'], list) and 'dtTransaction' in data['data'][0]:
                return data['data'][0]['dtTransaction']
            else:
                print("Error: 'data' or 'dtTransaction' keys not found in the JSON structure.")
                return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

if __name__ == "__main__":
    main_gui()
