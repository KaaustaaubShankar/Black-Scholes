import scipy.stats as stats
import math
from yahooquery import Ticker
import pandas as pd


def black_scholes(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call = S * stats.norm.cdf(d1) - K * math.exp(-r * T) * stats.norm.cdf(d2)
    put = K * math.exp(-r * T) * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)
    return call, put


def main(stock):

    try:
        stk = Ticker(stock)
    except Exception as e:
        print(f"Error fetching data for {stock}: {e}")
        print("Doing Apple")
        stock = 'AAPL'
        stk = Ticker(stock)
    
    option_chain = stk.option_chain
    options_df = option_chain.reset_index()
    calls_df = options_df[options_df['optionType'] == 'calls']
    calls_df['mid_price'] = (calls_df['ask'] + calls_df['bid']) / 2
    calls_df = calls_df[calls_df['mid_price'] > 1]
    
    # Get current stock price
    current_price = stk.price[stock]['regularMarketPrice']

    # Calculate days to expiration and convert to years
    calls_df['days_to_expiry'] = pd.to_datetime(calls_df['expiration']) - pd.Timestamp.now()
    calls_df['T'] = calls_df['days_to_expiry'].dt.days / 365

    # Use 10-year Treasury rate as risk-free rate (approximate)
    r = 0.045

    # Calculate theoretical prices using Black-Scholes
    calls_df['bs_price'] = calls_df.apply(
        lambda row: black_scholes(
            S=current_price,
            K=row['strike'], 
            T=row['T'],
            r=r,
            sigma=row['impliedVolatility']
        )[0],  # Index 0 gets call price
        axis=1
    )

    # Compare market vs model prices
    calls_df['price_diff'] = calls_df['mid_price'] - calls_df['bs_price']

    output_df = calls_df[['symbol', 'contractSymbol', 'expiration', 'days_to_expiry', 'strike', 
               'impliedVolatility', 'bid', 'ask', 'mid_price', 'bs_price', 'price_diff']]

    output_df.to_csv('output.csv', index=False)




if __name__ == '__main__':
    main('AAPL')