# Black-Scholes Option Pricing Tool

This tool fetches real-time options data for a given stock and calculates the fair value of call options using the Black-Scholes model. The data is retrieved via Yahooquery and exported as a `.csv` file for analysis.

---

## Features
- **Real-time Data**: Fetches stock prices, dividend yield, and options chain.
- **Black-Scholes Model**: Computes theoretical call option prices.
- **Filtering**: Excludes options with a mid-price below 1.
- **Price Comparison**: Calculates the difference between the Black-Scholes price and market mid-price.
- **Output**: Generates a CSV file (`output.csv`) with detailed option data.

---

## Installation

### Prerequisites
Ensure Python is installed along with the following libraries:
```bash
pip install requirements.txt
```

---

## Usage

1. **Set Parameters**:
   - `stock`: Ticker symbol (default: `AAPL`).
   - `risk_free_rate`: Risk-free interest rate as a decimal (default: `0.045`).

2. **Run as Script**:
   ```bash
   python black_scholes.py
   ```

3. **Run as Streamlit App**:
   For an interactive interface:
   ```bash
   streamlit run st_black_scholes.py
   ```

4. **Output**:
   - View data in the Streamlit app or in the generated `output.csv`.

---
