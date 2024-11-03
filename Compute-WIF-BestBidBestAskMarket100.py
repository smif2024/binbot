from binance.client import Client
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import csv
from datetime import datetime

# Binance API credentials (Replace with your own API keys)
api_key = 'mykey'
api_secret = 'mysecret'

# Initialize the Binance Client
client = Client(api_key, api_secret)

# Set up the logger configuration
def setup_logger(log_file_name):
    """Set up a logger to log messages to both file and console."""
    logger = logging.getLogger(log_file_name)
    logger.setLevel(logging.INFO)

    # Create a TimedRotatingFileHandler to rotate logs every 1 hour
    handler = TimedRotatingFileHandler(
        filename=log_file_name,
        when='H',  # Rotate every hour
        interval=1,
        backupCount=240  # Keep the last 240 log files
    )
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    # Set up console handler to display logs on the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Remove any existing handlers before adding new ones
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add handlers for both file and console output
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

# Define a function to compute and log arbitrage details
def compute_arbitrage(logger):
    """Compute profit or loss for Quadrangular Arbitrage every 15 seconds."""
    # Fetch best prices for each trading pair
    eth_usdt_bid, eth_usdt_ask = get_best_prices('ETHUSDT', logger)  # BUY ETH with USDT
    eth_brl_bid, eth_brl_ask = get_best_prices('ETHBRL', logger)     # SELL ETH for BRL
    wif_brl_bid, wif_brl_ask = get_best_prices('WIFBRL', logger)     # BUY WIF with BRL
    wif_usdt_bid, wif_usdt_ask = get_best_prices('WIFUSDT', logger)  # SELL WIF for USDT

    # Display fetched prices for verification
    logger.info("")
    logger.info(f"=== Fetched Prices for Trading Pairs ===")
    logger.info(f"ETHUSDT: Best Bid = {eth_usdt_bid}, Best Ask = {eth_usdt_ask}")
    logger.info(f"ETHBRL: Best Bid = {eth_brl_bid}, Best Ask = {eth_brl_ask}")
    logger.info(f"WIFBRL: Best Bid = {wif_brl_bid}, Best Ask = {wif_brl_ask}")
    logger.info(f"WIFUSDT: Best Bid = {wif_usdt_bid}, Best Ask = {wif_usdt_ask}\n")

    # Define a starting capital in USDT
    starting_capital = 100  # Assuming 100 USDT to begin the arbitrage cycle

    # Step 1: Calculate the amount of ETH we can buy with USDT at the best ask price
    eth_bought = starting_capital / eth_usdt_ask

    # Step 2: Calculate the amount of BRL obtained by selling ETH at the best bid price
    brl_received = eth_bought * eth_brl_bid

    # Step 3: Calculate the amount of WIF we can buy with BRL at the best ask price
    wif_bought = brl_received / wif_brl_ask

    # Step 4: Calculate the amount of USDT obtained by selling WIF at the best bid price
    usdt_received = wif_bought * wif_usdt_bid

    # Assume a trading fee of 0.07% per transaction (4 trades) + initial capital
    trading_fee = (0.07 * 4) + 0.6
    # Calculate profit or loss
    profit_or_loss = (usdt_received - starting_capital) - trading_fee

    # Log the results
    logger.info(f"Starting Capital (USDT): {starting_capital:.2f}")
    logger.info(f"ETH bought at best ask price: {eth_bought:.6f} ETH")
    logger.info(f"BRL received after selling ETH at best bid price: {brl_received:.2f} BRL")
    logger.info(f"WIF bought with BRL at best ask price: {wif_bought:.6f} WIF")
    logger.info(f"USDT received after selling WIF at best bid price: {usdt_received:.2f} USDT")
    logger.info(f"Trading Fee: {trading_fee:.2f}")
    logger.info(f"Profit/Loss: {profit_or_loss:.2f} USDT")

    # Check for profit and log to a separate CSV file if there is profit
    if profit_or_loss > 0:
        logger.info(f"Arbitrage compute result = PROFIT: {profit_or_loss:.2f} USDT")
        profit_filename = f"logs/compute/profit-WIF-100-{datetime.now().strftime('%d%m%Y%H')}.csv"  # Update filename pattern to hourly
        with open(profit_filename, mode='a', newline='', encoding='utf-8') as profit_file:
            writer = csv.writer(profit_file)
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), eth_bought, brl_received, wif_bought, usdt_received, profit_or_loss])
            logger.info(f"Profit logged to file {profit_filename}")
    else:
        logger.info(f"Arbitrage compute result = LOSS: {profit_or_loss:.2f} USDT")

    logger.info("=============== END ===============")
    logger.info("")

def get_best_prices(symbol, logger):
    """Fetch the best bid and ask prices for a given symbol using get_orderbook_ticker."""
    ticker = client.get_orderbook_ticker(symbol=symbol)
    best_bid = float(ticker['bidPrice'])
    best_ask = float(ticker['askPrice'])
    logger.info(f"Fetched best prices for {symbol}: Best Bid = {best_bid}, Best Ask = {best_ask}")
    return best_bid, best_ask

# Set up the logger with an hourly log file name pattern
log_filename = f"logs/compute/compute-WIF-100-{datetime.now().strftime('%d%m%Y%H')}.log"
logger = setup_logger(log_filename)

# Main loop to run the arbitrage computation every 15 seconds and rotate log file every hour
while True:
    # Update the log file name every hour based on hour-level filename
    new_log_filename = f"logs/compute/compute-WIF-100-{datetime.now().strftime('%d%m%Y%H')}.log"
    if new_log_filename != logger.handlers[0].baseFilename:
        logger = setup_logger(new_log_filename)

    # Run the arbitrage analysis
    compute_arbitrage(logger)

    # Sleep for 15 seconds before running the next analysis
    time.sleep(15)