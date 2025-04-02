@ -0,0 +1,534 @@
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import time
import os
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
# DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/DexScreener/services/swaps/token/{token_address}" # Older endpoint
DEXSCREENER_PAIRS_URL = "https://api.dexscreener.com/latest/DexScreener/services/pairs/solana/{pair_address}"
DEXSCREENER_TOKEN_SEARCH_URL = "https://api.dexscreener.com/latest/DexScreener/services/tokens/search?q={query}" # Search endpoint
DEXSCREENER_TOKEN_PAIRS_URL = "https://api.dexscreener.com/latest/DexScreener/services/tokens/{token_address}" # Get pairs for a token
SOLSCAN_API_URL = "https://public-api.solscan.io/" # Base URL, specific endpoints needed
SOLSCAN_PRO_API_BASE = "https://pro-api.solscan.io/v2.0"

# Helius RPC URL - MUST BE SET AS ENVIRONMENT VARIABLE
HELIUS_RPC_URL = os.getenv('HELIUS_RPC_URL')

# Helius V0 Transaction Fetching
HELIUS_V0_TXN_URL = "https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={api_key}"

# Fallback launch timestamp if DexScreener fails (from mint transaction)
FALLBACK_LAUNCH_TIMESTAMP_S = 1739559482 # Approx Feb 14, 2025 21:38:02 UTC
TRANSACTION_CACHE_DIR = "simulation" # Directory to save JSON cache
MANUAL_TARGET_COUNT = 171628 # Manual target based on Solscan observations

# --- REMOVED Hardcoded API Key --- 
# HELIUS_API_KEY = "beb88a7d-d8d6-4cb5-b587-bb550a186ab9"

# Helper Functions
def fetch_dexscreener_data(pair_address):
    """Fetches pair data from DexScreener API using the pair address."""
    url = DEXSCREENER_PAIRS_URL.format(pair_address=pair_address)
    print(f"Fetching DexScreener data for pair: {pair_address} from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise exception for bad status codes
        data = response.json()
        print("DexScreener data fetched successfully via pair address.")
        return data.get('pair')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching DexScreener data via pair address ({url}): {e}")
        return None
    except Exception as e:
        print(f"Error processing DexScreener pair data: {e}")
        return None

def fetch_dexscreener_data_by_token(token_address):
    """Fetches data, potentially finding the pair, using the token address."""
    url = DEXSCREENER_TOKEN_PAIRS_URL.format(token_address=token_address)
    print(f"Fetching DexScreener data for token: {token_address} from {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # The response might contain multiple pairs, we need to find the relevant one
        # Or it might return the most relevant pair directly? API structure varies.
        if data and 'pairs' in data and data['pairs']:
             # Heuristic: Assume the first pair listed is the most relevant or has most liquidity
            print(f"Found {len(data['pairs'])} pairs for token. Selecting first one.")
            return data['pairs'][0]
        elif data and 'pair' in data:
             # Sometimes the response structure has 'pair' directly
             print("Found pair data directly for token.")
             return data['pair']
        else:
            print("No pairs found for the token address.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching DexScreener data via token address ({url}): {e}")
        return None
    except Exception as e:
        print(f"Error processing DexScreener token data: {e}")
        return None

def fetch_dexscreener_historical(pair_address, resolution=5, lookback_hours=24):
    """Fetches historical OHLCV data using a different (unofficial?) endpoint approach."""
    # This endpoint seems to work for historical bars but might be unofficial
    # Reference: Often found via network inspection on DexScreener website
    url = f"https://api.dexscreener.com/latest/DexScreener/services/candles/solana/{pair_address}?res={resolution}&bars=1000"

    # Calculate time boundaries (less reliable without specific DexScreener API for this)
    # We might get more data than needed and filter later
    print(f"Attempting to fetch historical data ({resolution}min bars) for pair: {pair_address}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Historical data fetched successfully.")
        return data.get('candles')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical data: {e}")
        return None
    except Exception as e:
        print(f"Error processing historical data: {e}")
        return None

def process_candles(candles_data):
    """Processes candle data into a pandas DataFrame."""
    if not candles_data:
        return None
    try:
        df = pd.DataFrame(candles_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.rename(columns={'timestamp': 'time', 'open': 'o', 'high': 'h', 'low': 'l', 'close': 'c', 'volume': 'v'}, inplace=True)
        # Convert price columns to numeric, coercing errors
        price_cols = ['o', 'h', 'l', 'c']
        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Convert volume to numeric
        df['v'] = pd.to_numeric(df['v'], errors='coerce')
        df.set_index('time', inplace=True)
        df.sort_index(inplace=True)
        print(f"Processed {len(df)} candles into DataFrame.")
        return df
    except Exception as e:
        print(f"Error processing candle data: {e}")
        return None

def plot_launch_data(df, pair_info, launch_timestamp_s):
    """Plots the price and volume around the launch."""
    if df is None or df.empty:
        print("No data available for plotting.")
        return

    token_name = pair_info.get('baseToken', {}).get('symbol', 'Token')
    pair_address = pair_info.get('pairAddress', 'UnknownPair')
    launch_time = pd.to_datetime(launch_timestamp_s, unit='s', utc=True)

    print(f"Plotting data for {token_name} ({pair_address})")
    print(f"Using launch time: {launch_time} (UTC)")

    # Filter data around launch time (e.g., first few hours)
    plot_start_time = launch_time - timedelta(minutes=10) # Include a bit before
    plot_end_time = launch_time + timedelta(hours=3)
    plot_df = df[(df.index >= plot_start_time) & (df.index <= plot_end_time)]

    if plot_df.empty:
        print("No data found within the plotting window around launch time.")
        # Fallback: plot the first few hours of available data relative to its start
        plot_start_time = df.index.min()
        plot_end_time = plot_start_time + timedelta(hours=3)
        plot_df = df[(df.index >= plot_start_time) & (df.index <= plot_end_time)]
        if plot_df.empty:
            print("No data to plot.")
            return

    fig, ax1 = plt.subplots(figsize=(15, 7))

    # Plot Price
    color_price = 'tab:blue'
    ax1.set_xlabel('Time (UTC)')
    ax1.set_ylabel('Price (USD)', color=color_price)
    ax1.plot(plot_df.index, plot_df['c'], color=color_price, label='Close Price')
    ax1.tick_params(axis='y', labelcolor=color_price)
    ax1.grid(True)

    # Plot Volume
    ax2 = ax1.twinx()
    color_volume = 'tab:red'
    ax2.set_ylabel('Volume (Quote)', color=color_volume)
    ax2.bar(plot_df.index, plot_df['v'], color=color_volume, alpha=0.3, width=0.002, label='Volume')
    ax2.tick_params(axis='y', labelcolor=color_volume)

    # Formatting
    plt.title(f'{token_name} Launch Analysis ({pair_address[:6]}...) - DexScreener Data')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    ax1.axvline(launch_time, color='k', linestyle='--', linewidth=1, label=f'Est. Launch {launch_time.strftime("%H:%M")}')
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.tight_layout()
    filename = f"simulation/launch_analysis_{token_name}_{pair_address[:6]}.png"
    plt.savefig(filename)
    print(f"Plot saved to {filename}")
    # plt.show()

# --- Solscan Transfer Count ---
def fetch_solscan_transfer_count(address):
    """Attempts to fetch the total transfer count from Solscan Pro API using JWT Auth."""
    solscan_jwt = os.getenv('SOLSCAN_API_JWT') # Look for JWT in env var
    if not solscan_jwt:
        print("Warning: SOLSCAN_API_JWT environment variable not set. Cannot verify total transfer count.")
        return None

    # Using the account overview endpoint might be more likely to have a total count
    url = f"{SOLSCAN_PRO_API_BASE}/account/overview?address={address}"
    # Use Authorization: Bearer header for JWT
    headers = {"accept": "application/json", "Authorization": f"Bearer {solscan_jwt}"}
    print(f"\nAttempting to fetch Solscan account overview for count: {address} (using JWT Auth)")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Look for a field that represents total transfers
        transfer_count = data.get('total_transfers') # Placeholder
        if transfer_count is not None:
            print(f"Solscan reported total transfers (overview): {transfer_count}")
            return int(transfer_count)
        else:
            print("Could not find total transfer count field in Solscan overview response.")
            # Try getting count from the transfer endpoint itself
            url_transfer = f"{SOLSCAN_PRO_API_BASE}/account/transfer?address={address}&page_size=1"
            response = requests.get(url_transfer, headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'pagination' in data and 'total_items' in data['pagination']:
                 transfer_count = data['pagination']['total_items']
                 print(f"Solscan reported total transfers via pagination: {transfer_count}")
                 return int(transfer_count)
            else:
                print("Could not determine total transfer count from Solscan transfer endpoint either.")
                return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Solscan data: {e}")
        if hasattr(e, 'response') and e.response is not None:
            # Print response body if available, might contain specific error message
            try:
                print(f"Solscan Response Status: {e.response.status_code}")
                print(f"Solscan Response Body: {e.response.text}")
            except Exception:
                pass # Ignore errors printing response details
        return None
    except Exception as e:
        print(f"Error processing Solscan response: {e}")
        return None

# --- Helius Transaction Fetching with Caching ---
def get_cached_transactions_path(address):
    """Generates the path for the transaction cache file."""
    filename = f"helius_transactions_{address}.json"
    return os.path.join(TRANSACTION_CACHE_DIR, filename)

def load_transactions_from_cache(address):
    """Loads transactions from a JSON cache file if it exists and reverses it (earliest first)."""
    cache_path = get_cached_transactions_path(address)
    if os.path.exists(cache_path):
        print(f"Loading transactions from cache file: {cache_path}")
        try:
            with open(cache_path, 'r') as f:
                # Load the transactions as saved (most recent first)
                transactions_raw = json.load(f)
            print(f"Successfully loaded {len(transactions_raw)} transactions raw from cache.")
            # Return the reversed list so earliest is first, consistent with fresh fetch
            return transactions_raw[::-1]
        except Exception as e:
            print(f"Error loading cache file {cache_path}: {e}. Will fetch from API.")
            return None
    return None

def save_transactions_to_cache(address, transactions):
    """Saves fetched transactions (assumed MOST RECENT FIRST) to a JSON cache file."""
    cache_path = get_cached_transactions_path(address)
    print(f"Saving {len(transactions)} transactions to cache file: {cache_path}")
    try:
        os.makedirs(TRANSACTION_CACHE_DIR, exist_ok=True)
        with open(cache_path, 'w') as f:
            # Save in the order received (most recent first)
            json.dump(transactions, f, indent=2)
        print("Successfully saved transactions to cache.")
    except Exception as e:
        print(f"Error saving cache file {cache_path}: {e}")

def fetch_helius_transactions(address, existing_transactions_recent_first=None, target_limit=200000, force_refresh=False, save_interval=50):
    """Fetches transaction history, potentially resuming from existing data, saves cache, returns earliest first."""

    # Read API key from environment
    api_key = os.getenv('HELIUS_API_KEY')
    if not api_key:
        print("Error: HELIUS_API_KEY environment variable not set. Please set it in .env file or environment.")
        return None

    # Determine starting point for fetching
    all_transactions_recent_first = []
    last_signature = None
    if existing_transactions_recent_first and not force_refresh:
        print("Resuming fetch based on existing transactions.")
        all_transactions_recent_first = existing_transactions_recent_first
        if all_transactions_recent_first:
            # Find the signature of the *earliest* transaction in the existing list (which is the last one when sorted recent-first)
            last_signature = all_transactions_recent_first[-1].get("signature")
            print(f"Starting fetch before signature: {last_signature}")
        else:
            print("Existing transaction list is empty, starting fresh fetch.")
    else:
         print(f"\n--- Starting Fresh Fetch for Helius Transactions: {address} using V0 API --- ")

    print(f"Target total transactions: {target_limit}. NOTE: This may take a long time and consume API credits.")

    request_count = 0
    # Adjust max requests based on remaining needed
    needed_limit = target_limit - len(all_transactions_recent_first)
    max_requests = (needed_limit // 100) + 5
    print(f"Maximum additional requests set to: {max_requests}")
    start_time = time.time()
    last_save_count = 0
    newly_fetched_count = 0

    while len(all_transactions_recent_first) < target_limit and request_count < max_requests:
        request_count += 1
        current_limit = min(100, target_limit - len(all_transactions_recent_first))
        if current_limit <= 0: break

        url = HELIUS_V0_TXN_URL.format(address=address, api_key=api_key)
        params = {"limit": current_limit}
        if last_signature:
            params["before"] = last_signature

        if request_count % 10 == 0 or request_count == 1:
            elapsed_time = time.time() - start_time
            print(f"Request {request_count}/{max_requests}... Total fetched so far: {len(all_transactions_recent_first)}/{target_limit}. Elapsed: {elapsed_time:.1f}s")

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            transactions_batch = response.json()

            if isinstance(transactions_batch, dict) and "error" in transactions_batch:
                print(f"Helius API Error: {transactions_batch['error']}")
                break

            if transactions_batch and isinstance(transactions_batch, list):
                # Prepend older transactions to maintain recent-first order during fetch
                all_transactions_recent_first.extend(transactions_batch)
                newly_fetched_count += len(transactions_batch)
                if "signature" in transactions_batch[-1]:
                    last_signature = transactions_batch[-1]["signature"]
                    # Periodic save during long fetches
                    if request_count - last_save_count >= save_interval:
                        print(f"  Saving intermediate cache ({len(all_transactions_recent_first)} transactions)...")
                        save_transactions_to_cache(address, all_transactions_recent_first)
                        last_save_count = request_count
                    time.sleep(0.3)
                else:
                    print("Warning: Could not find 'signature' in last transaction for pagination.")
                    break
            else:
                print("No more transactions found or empty/invalid result from Helius.")
                break # Stop fetching if Helius returns empty
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status Code: {http_err.response.status_code}")
            try: print(f"Response Body: {http_err.response.text}")
            except: pass
            if http_err.response.status_code == 429:
                print("Rate limit likely hit. Sleeping for 10 seconds...")
                time.sleep(10)
                request_count -= 1
                continue
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Helius transactions: {e}")
            time.sleep(5)
            request_count -=1
        except Exception as e:
            print(f"Error processing Helius response: {e}")
            break

    end_time = time.time()
    total_time = end_time - start_time
    print(f"--- Finished Helius fetch attempt. Newly fetched: {newly_fetched_count}. Total in list: {len(all_transactions_recent_first)}. Time: {total_time:.2f}s ---")

    if all_transactions_recent_first:
        # Save the final potentially combined list
        save_transactions_to_cache(address, all_transactions_recent_first)
        # Return reversed list (earliest first)
        return all_transactions_recent_first[::-1]
    else:
        # If initial list was also empty
        return []

# --- Helius Transaction Analysis ---
def analyze_initial_trades(transactions, target_token_address, launch_timestamp_s):
    """Analyzes fetched transactions to identify potential insider activity."""
    if not transactions:
        print("No transaction data to analyze.")
        return

    if not launch_timestamp_s:
        print("Launch timestamp is required for analysis.")
        return

    print("\n--- Analyzing Initial Trades from Helius Data ---")
    print(f"Target Token Address: {target_token_address}")
    print(f"Using Launch Timestamp (s): {launch_timestamp_s}")

    launch_dt = datetime.fromtimestamp(launch_timestamp_s, tz=timezone.utc)
    delta_minutes = 10 # Analyze first 10 minutes (t0 + delta)
    end_time_delta = launch_dt + timedelta(minutes=delta_minutes)
    print(f"Analysis window: {launch_dt} to {end_time_delta} (UTC)")

    initial_buyers = {} # Store initial buyers: {buyer_address: total_buy_amount_token}
    earliest_timestamp_dt = None # Track the actual earliest time in data

    if transactions:
        try:
            earliest_timestamp_s = transactions[0].get('timestamp') # First item is earliest
            if earliest_timestamp_s:
                 earliest_timestamp_dt = datetime.fromtimestamp(earliest_timestamp_s, tz=timezone.utc)
                 print(f"Earliest transaction found in loaded data: {earliest_timestamp_dt}")
                 # Check if data covers the launch window
                 if earliest_timestamp_dt > launch_dt:
                     print("WARNING: Earliest transaction in loaded data is AFTER the estimated launch time.")
                     print("         Analysis of the exact launch moment might not be possible with this data.")
            else:
                print("Could not determine earliest timestamp from data.")
        except Exception as e:
            print(f"Error getting earliest timestamp: {e}")

    # Iterate through transactions (earliest first)
    for tx in transactions:
        try:
            tx_timestamp = tx.get('timestamp')
            if not tx_timestamp: continue
            tx_dt = datetime.fromtimestamp(tx_timestamp, tz=timezone.utc)
            # Only process transactions within our analysis window relative to launch
            if tx_dt < launch_dt: continue
            if tx_dt > end_time_delta: continue # Analyze only first delta_minutes

            token_transfers = tx.get('tokenTransfers', [])
            for transfer in token_transfers:
                if transfer.get('mint') == target_token_address:
                    buyer = transfer.get('toUserAccount')
                    amount_str = transfer.get('tokenAmount')
                    if buyer and amount_str:
                        try:
                            amount = float(amount_str)
                            if amount > 0:
                                initial_buyers[buyer] = initial_buyers.get(buyer, 0) + amount
                        except ValueError: continue
        except Exception as e:
            print(f"Error processing transaction {tx.get('signature')}: {e}")
            continue

    print(f"--- Analysis Results (First {delta_minutes} mins After Est. Launch) ---")
    if not initial_buyers:
        print("No potential buy transactions found for the target token within the analysis window.")
        return
    sorted_buyers = sorted(initial_buyers.items(), key=lambda item: item[1], reverse=True)
    print(f"Found {len(sorted_buyers)} unique potential buyers in the analysis window.")
    print("Top 10 Potential Buyers:")
    for i, (buyer, amount) in enumerate(sorted_buyers[:10]):
        print(f"  {i+1}. Address: {buyer}, Total Bought: {amount:,.2f} {target_token_address[:6]}...")

    # Further analysis ideas:
    # - Compare timestamps of top buyers (did they buy exactly at launch?)
    # - Check if top buyers funded their wallets just before launch
    # - Analyze the *source* of the tokens (e.g., from the LP pair directly?)

# --- Main Execution ---
if __name__ == "__main__":
    print("Loading environment variables...")
    if load_dotenv(): print(".env loaded.")
    else: print("Warn: .env not found.")
    if not os.getenv('HELIUS_API_KEY'): print("CRIT ERR: HELIUS_API_KEY missing."); exit()

    libra_pair_address = "BzzMNvfm7T6zSGFeLXzERmRxfKaNLdo4fSzvsisxcSzz"
    libra_token_address = "Bo9jh3wsmcC2AjakLWzNmKJ3SgtZmXEcSaW7L2FAvUsU"
    force_helius_refresh = True

    print(f"Analyzing Pair: {libra_pair_address}")
    print(f"Token: {libra_token_address}")

    # 1. Fetch DexScreener Info
    pair_info = fetch_dexscreener_data(libra_pair_address)
    if not pair_info: print("Dex fail 1... token"); pair_info = fetch_dexscreener_data_by_token(libra_token_address)
    # Determine launch timestamp
    launch_timestamp_s = None
    if pair_info and pair_info.get('pairCreatedAt'): launch_timestamp_s = pair_info['pairCreatedAt']/1000; print(f"Use Dex launch: {datetime.fromtimestamp(launch_timestamp_s, tz=timezone.utc)}")
    else: launch_timestamp_s = FALLBACK_LAUNCH_TIMESTAMP_S; print(f"Use fallback launch: {datetime.fromtimestamp(launch_timestamp_s, tz=timezone.utc)}")
    if not pair_info: pair_info = {'baseToken': {'address': libra_token_address}, 'pairAddress': libra_pair_address, 'pairCreatedAt': launch_timestamp_s * 1000}
    elif 'pairCreatedAt' not in pair_info or not pair_info['pairCreatedAt']: pair_info['pairCreatedAt'] = launch_timestamp_s * 1000
    libra_pair_address = pair_info.get('pairAddress', libra_pair_address); print(f"Use Pair Addr: {libra_pair_address}")
    # 2. Plot DexScreener Data
    candles_data = fetch_dexscreener_historical(libra_pair_address);
    if candles_data: df_candles = process_candles(candles_data)
    else: df_candles = None
    if df_candles is not None: plot_launch_data(df_candles, pair_info, launch_timestamp_s)
    else: print("Skip plot: no Dex candles.")
    # 3. Load Helius Cache (for potential resume signature if refresh didn't clear it conceptually)
    helius_transactions_cache_recent_first = None
    cache_path = get_cached_transactions_path(libra_pair_address)
    # We still load cache here to potentially get the 'before' signature, even if forcing refresh
    if os.path.exists(cache_path):
        print(f"Loading Helius cache (for signature): {cache_path}")
        try:
            with open(cache_path, 'r') as f: helius_transactions_cache_recent_first = json.load(f)
            print(f"Loaded {len(helius_transactions_cache_recent_first)} txns (recent first) for signature.")
        except Exception as e: print(f"Error load cache: {e}"); helius_transactions_cache_recent_first = None

    # 4. Determine if Helius Refetch is Needed (Forcing it here)
    helius_cache_count = len(helius_transactions_cache_recent_first) if helius_transactions_cache_recent_first else 0
    final_helius_transactions_earliest_first = None
    should_refetch = False

    if force_helius_refresh:
        print("Forcing refresh of Helius data...")
        should_refetch = True
        # Don't clear cache content here, fetch function needs it for 'before' signature
        # helius_transactions_cache_recent_first = None
    elif helius_cache_count < MANUAL_TARGET_COUNT:
        # This block won't be hit when force_helius_refresh is True
        print(f"Helius cache ({helius_cache_count}) < Manual Target ({MANUAL_TARGET_COUNT}). Attempting refetch...")
        should_refetch = True
    elif helius_transactions_cache_recent_first is None:
        # This block won't be hit when force_helius_refresh is True unless cache failed load
        print("No Helius cache found. Attempting fresh fetch...")
        should_refetch = True

    if should_refetch:
        final_helius_transactions_earliest_first = fetch_helius_transactions(
            libra_pair_address,
            existing_transactions_recent_first=helius_transactions_cache_recent_first, # Pass cache for signature
            target_limit=MANUAL_TARGET_COUNT, # Aim for the manual target
            force_refresh=True # Pass the flag down
        )
    elif helius_transactions_cache_recent_first is not None:
        print("Using existing Helius cache data (refresh not forced). Reversing...")
        final_helius_transactions_earliest_first = helius_transactions_cache_recent_first[::-1]
    else:
        print("No Helius data available.")
        final_helius_transactions_earliest_first = []

    # 5. Analyze Final Helius Transactions
    analyze_initial_trades(final_helius_transactions_earliest_first, libra_token_address, launch_timestamp_s)

    print("\nAnalysis complete.") 