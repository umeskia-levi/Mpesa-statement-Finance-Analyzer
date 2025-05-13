 # M-Pesa Finance Dashboard

## 📊 Overview

The M-Pesa Finance Dashboard is a Streamlit application that helps you analyze and categorize your M-Pesa transaction history. It provides visualizations of your spending patterns, payment trends, and helps you manage your finances more effectively.

## ✨ Features

- **Transaction Categorization**: Automatically categorize transactions based on keywords
- **Expense Analysis**: Visualize spending by category with interactive charts
- **Payment Tracking**: Monitor incoming payments and identify top recipients
- **Custom Categories**: Create and manage your own transaction categories
- **Keyword Management**: Add specific keywords to improve auto-categorization
- **CSV Import**: Easily import your M-Pesa statement CSV files

## 📥 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/umeskia-levi/mpesa-finance-dashboard.git
   cd mpesa-finance-dashboard
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. Export your M-Pesa statement as a CSV file from:
   - The M-Pesa app (Statement section)
   - Safaricom's M-Pesa portal

2. Run the application:
   ```bash
   streamlit run app.py
   ```

3. In your browser:
   - Upload your M-Pesa CSV file
   - Review and adjust transaction categories
   - Explore your financial insights

## 📂 File Structure

```
mpesa-finance-dashboard/
├── app.py                # Main application code
├── categories.json       # Default transaction categories
├── README.md             # This documentation
└── requirements.txt      # Python dependencies
```

## ⚙️ Configuration

The application automatically creates and manages:
- `categories.json` - Stores your custom categories and keywords
- You can edit this file directly or through the app interface

## 📊 Sample M-Pesa CSV Format

The app expects CSV files in the standard M-Pesa export format:
```
Receipt No.,Completion Time,Details,Transaction Status,Paid In,Withdrawn,Balance
SGL1E8EQGD,2024-07-21 16:51:08,Payment to John Doe,Completed,,100.00,500.00
SGL2DVLDKE,2024-07-21 15:09:15,Received from Jane Smith,Completed,200.00,,600.00
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## 📜 License

This project is licensed under the MIT License.
