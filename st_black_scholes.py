import streamlit as st
import math
import pandas as pd
from scipy.stats import norm
from yahooquery import Ticker


def black_scholes(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    put = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return call, put


def fetch_option_data(stock):
    try:
        stk = Ticker(stock)
        option_chain = stk.option_chain
    except Exception as e:
        st.error(f"Error fetching data for {stock}: {e}")
        st.info("Falling back to Apple (AAPL)")
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
    
    return output_df


def main():
    st.title("Black-Scholes Option Pricing")
    st.write("Calculate theoretical option prices using the Black-Scholes model and compare them with market prices.")

    # Input for stock ticker
    stock = st.text_input("Enter Stock Ticker", "AAPL")

    if st.button("Fetch and Calculate"):
        with st.spinner("Fetching data and calculating..."):
            try:
                results = fetch_option_data(stock)
                st.success("Calculation complete!")
                st.write("Below are the option data with theoretical Black-Scholes prices:")
                
                # Display data
                st.dataframe(results)

                # Allow user to download the results as a CSV file
                csv = results.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name=f"{stock}_options.csv", mime="text/csv")
            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
