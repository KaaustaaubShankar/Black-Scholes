import scipy.stats as stats
import math
from yahooquery import Ticker
import pandas as pd


def black_scholes(S, K, T, r, sigma, q=0):
    # S: spot price, K: strike price, T: time to expiry (years), r: risk-free rate, sigma: volatility, q: dividend yield
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call = S * math.exp(-q * T) * stats.norm.cdf(d1) - K * math.exp(-r * T) * stats.norm.cdf(d2)
    put = K * math.exp(-r * T) * stats.norm.cdf(-d2) - S * math.exp(-q * T) * stats.norm.cdf(-d1)
    return call, put


def main(stock):
    # Initialize ticker, default to AAPL if error
    try:
        stk = Ticker(stock)
    except Exception as e:
        stock = 'AAPL'
        stk = Ticker(stock)
    
    # Get option chain and filter for calls only
    option_chain = stk.option_chain
    options_df = option_chain.reset_index()
    calls_df = options_df[options_df['optionType'] == 'calls']
    
    # Calculate mid price and filter out low value options
    calls_df['mid_price'] = (calls_df['ask'] + calls_df['bid']) / 2
    calls_df = calls_df[calls_df['mid_price'] > 1]
    
    # Get current stock price and calculate time to expiry
    current_price = stk.price[stock]['regularMarketPrice']
    calls_df['days_to_expiry'] = pd.to_datetime(calls_df['expiration']) - pd.Timestamp.now()
    calls_df['T'] = calls_df['days_to_expiry'].dt.days / 365
    
    # Set constants for Black-Scholes calculation
    r = 0.045  # Risk-free rate
    dividend_yield = stk.summary_detail[stock].get('dividendYield', 0)
    
    # Calculate theoretical price using Black-Scholes
    calls_df['bs_price'] = calls_df.apply(
        lambda row: black_scholes(
            S=current_price,
            K=row['strike'], 
            T=row['T'],
            r=r,
            sigma=row['impliedVolatility'],
            q=dividend_yield
        )[0],
        axis=1
    )
    
    # Calculate price difference and export results
    calls_df['price_diff'] = calls_df['mid_price'] - calls_df['bs_price']
    output_df = calls_df[['symbol', 'contractSymbol', 'expiration', 'days_to_expiry', 'strike', 
               'impliedVolatility', 'bid', 'ask', 'mid_price', 'bs_price', 'price_diff']]
    output_df.to_csv('output.csv', index=False)


if __name__ == '__main__':
    main('AAPL')
