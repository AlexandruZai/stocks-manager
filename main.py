from database import init_db, create_user, buy_stock, sell_stock, view_portfolio, plot_portfolio_graph
# Main menu

def main():
    init_db()
    while True:
        print("\nStock Portfolio Manager")
        print("1. Create User")
        print("2. Buy Stock")
        print("3. Sell Stock")
        print("4. View Portfolio")
        print("5. View Stocks Graph")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter username: ")
            create_user(username)
        elif choice == "2":
            username = input("Enter username: ")
            ticker = input("Enter stock ticker: ").upper()
            shares = int(input("Enter number of shares: "))
            buy_stock(username, ticker, shares)
        elif choice == "3":
            username = input("Enter username: ")
            ticker = input("Enter stock ticker: ").upper()
            shares = int(input("Enter number of shares: "))
            sell_stock(username, ticker, shares)
        elif choice == "4":
            username = input("Enter username: ")
            view_portfolio(username)
        elif choice == "5":
            username = input("Enter username: ")
            period = input("Enter the time period, e.g., '1h', '1d', '5d', '1wk', '1mo', '3mo', '6mo', 1y' ")
            plot_portfolio_graph(username, period)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
