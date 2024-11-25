import streamlit as st
import scipy.stats as stats
import math
import matplotlib.pyplot as plt
from yahooquery import Ticker
import pandas as pd


def black_scholes(S, K, T, r, sigma, q=0):
    # S: spot price, K: strike price, T: time to expiry (years), r: risk-free rate, sigma: volatility, q: dividend yield
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call = S * math.exp(-q * T) * stats.norm.cdf(d1) - K * math.exp(-r * T) * stats.norm.cdf(d2)
    put = K * math.exp(-r * T) * stats.norm.cdf(-d2) - S * math.exp(-q * T) * stats.norm.cdf(-d1)
    return call, put


def fetch_option_data(stock):
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
    return output_df


def plot_graphs(data):
    # Create columns for side-by-side layout
    col1, col2 = st.columns(2)

    # Price Distribution of Options
    with col1:
        st.subheader("Price Distribution")
        fig1, ax1 = plt.subplots()
        ax1.hist(data['mid_price'], bins=20, alpha=0.7, edgecolor="black")
        ax1.set_title("Mid Price Distribution")
        ax1.set_xlabel("Mid Price")
        ax1.set_ylabel("Frequency")
        st.pyplot(fig1)

    # Black-Scholes Value vs. Mid Price
    with col2:
        st.subheader("Black-Scholes vs. Mid Price")
        fig2, ax2 = plt.subplots()
        ax2.scatter(data['mid_price'], data['bs_price'], alpha=0.6)
        ax2.set_title("Black-Scholes vs. Mid Price")
        ax2.set_xlabel("Mid Price")
        ax2.set_ylabel("Black-Scholes Price")
        st.pyplot(fig2)




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

                # Display graphs
                plot_graphs(results)
            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
