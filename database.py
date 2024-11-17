import yfinance as yf
import matplotlib.pyplot as plt
import sqlite3

def init_db():
    conn = sqlite3.connect('stocks_portfolio.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticker TEXT,
            shares INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# Add a new user
def create_user(username):
    conn = sqlite3.connect('stocks_portfolio.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        print(f"User '{username}' created successfully!")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists!")
    conn.close()

# Buy stocks
def buy_stock(username, ticker, shares):
    conn = sqlite3.connect('stocks_portfolio.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        print(f"User '{username}' not found!")
        return
    user_id = user[0]

    c.execute('SELECT id, shares FROM stocks WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    stock = c.fetchone()
    if stock:
        c.execute('UPDATE stocks SET shares = shares + ? WHERE id = ?', (shares, stock[0]))
    else:
        c.execute('INSERT INTO stocks (user_id, ticker, shares) VALUES (?, ?, ?)', (user_id, ticker, shares))
    conn.commit()
    print(f"Bought {shares} shares of {ticker} for {username}.")
    conn.close()

# Sell stocks
def sell_stock(username, ticker, shares):
    conn = sqlite3.connect('stocks_portfolio.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        print(f"User '{username}' not found!")
        return
    user_id = user[0]

    c.execute('SELECT id, shares FROM stocks WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    stock = c.fetchone()
    if not stock:
        print(f"No shares of {ticker} found for user {username}.")
        return
    if stock[1] < shares:
        print(f"Not enough shares to sell! Available: {stock[1]}.")
        return
    elif stock[1] == shares:
        c.execute('DELETE FROM stocks WHERE id = ?', (stock[0],))
    else:
        c.execute('UPDATE stocks SET shares = shares - ? WHERE id = ?', (shares, stock[0]))
    conn.commit()
    print(f"Sold {shares} shares of {ticker} for {username}.")
    conn.close()

# View portfolio
def view_portfolio(username):
    conn = sqlite3.connect('stocks_portfolio.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        print(f"User '{username}' not found!")
        return
    user_id = user[0]

    c.execute('SELECT ticker, shares FROM stocks WHERE user_id = ?', (user_id,))
    stocks = c.fetchall()
    if not stocks:
        print(f"No stocks found for user {username}.")
        return

    total_value = 0  # Variable to hold the total portfolio value

    # Print Portfolio Header
    print(f"\nYour Portfolio for {username}:")
    print(f"{'Ticker':<10} {'Shares':<10} {'Current Price':<15} {'Total Value':<15}")
    print("-" * 50)

    # Print each stock's data
    for ticker, shares in stocks:
        stock = yf.Ticker(ticker)
        current_price = None
        try:
            # Get the most recent closing price
            current_price = stock.history(period="1d")['Close'].iloc[-1]
        except (IndexError, KeyError):
            current_price = 'N/A'

        # Calculate the total value for this stock
        if current_price != 'N/A':
            total_stock_value = current_price * shares
            total_value += total_stock_value
            # Format current price and total stock value to 2 decimal places
            current_price = round(current_price, 2)
            total_stock_value = round(total_stock_value, 2)
        else:
            total_stock_value = 'N/A'

        # Print stock row with formatted values
        print(f"{ticker:<10} {shares:<10} {current_price:<15} {total_stock_value:<15}")

    print("-" * 50)
    print(f"Total Portfolio Value: ${round(total_value, 2):.2f}")
    conn.close()


# Function to retrieve historical data and plot a graph
def plot_portfolio_graph(username, period):
    conn = sqlite3.connect('stocks_portfolio.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        print(f"User '{username}' not found!")
        return
    user_id = user[0]

    c.execute('SELECT ticker, shares FROM stocks WHERE user_id = ?', (user_id,))
    stocks = c.fetchall()
    if not stocks:
        print(f"No stocks found for user {username}.")
        return

    # Initialize the plot
    plt.figure(figsize=(10, 6))

    for ticker, shares in stocks:
        stock = yf.Ticker(ticker)

        try:
            # Get historical data for the last 3 months
            hist_data = stock.history(period=period)
            plt.plot(hist_data.index, hist_data['Close'], label=f"{ticker} ({shares} shares)", linewidth=2)
        except (IndexError, KeyError) as e:
            print(f"Error retrieving data for {ticker}: {e}")

    plt.title(f"Stock Portfolio Performance for {username}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    conn.close()