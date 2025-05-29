from flask import Flask, render_template, request, jsonify
from io import StringIO
import sys
import yfinance as yf

from agent import analysis_agent_executor, advice_agent_executor
from langchain.agents import tool

app = Flask(__name__)

@tool 
def PythonREPL_run(command: str) -> str:
    """A Python shell. Use this to execute Python commands. If you expect output, it should be printed out."""
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        exec(command, globals())
        sys.stdout = old_stdout
        return mystdout.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return str(e)

@tool
def get_stock_price(ticker, period='1d'):
    """Retrieves the stock price for a given ticker and period."""
    stock = yf.Ticker(ticker)
    try:
        todays_data = stock.history(period=period)
        if not todays_data.empty:
            return todays_data['Close'].iloc[-1]
        else:
            return "No data available"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@tool
def calculate_rsi(ticker, period='6mo', interval='1d', rsi_period=14):
    """Calculates the Relative Strength Index (RSI) for a given stock ticker."""
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        return "No data available"

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.ewm(com=rsi_period-1, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com=rsi_period-1, min_periods=rsi_period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def process_input():
    query = request.json.get('message', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    response = analysis_agent_executor.invoke({"input": query})
    return jsonify({"response": response})

@app.route('/advice', methods=['POST'])
def get_advice():
    query = request.json.get('message', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    response = advice_agent_executor.invoke({"input": query})
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
