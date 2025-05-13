import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

st.set_page_config(page_title="M-Pesa Finance App", page_icon="💰", layout="wide")

category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": [],
    }
    
if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)
        
def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df["Category"] = "Uncategorized"
    
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        
        for idx, row in df.iterrows():
            details = str(row["Details"]).lower().strip()
            if any(keyword in details for keyword in lowered_keywords):
                df.at[idx, "Category"] = category
                
    return df  

def process_mpesa_data(df):
    """Process M-Pesa statement data"""
    # Clean column names
    df.columns = [col.strip() for col in df.columns]
    
    # Determine amount and transaction type
    df['Amount'] = df.apply(
        lambda row: float(row['Paid In']) if pd.notna(row['Paid In']) 
        else -float(row['Withdrawn']) if pd.notna(row['Withdrawn']) 
        else 0,
        axis=1
    )
    
    # Create Debit/Credit column
    df['Debit/Credit'] = df['Amount'].apply(lambda x: 'Credit' if x > 0 else 'Debit')
    df['Amount'] = df['Amount'].abs()
    
    # Convert date
    df['Date'] = pd.to_datetime(df['Completion Time'], format='%Y-%m-%d %H:%M:%S')
    
    # Clean Details by removing phone numbers
    df['Details'] = df['Details'].str.replace(r'-\s*\d{3,}\*+\d+', '', regex=True)
    
    # Select relevant columns
    df = df[['Date', 'Details', 'Amount', 'Debit/Credit', 'Balance']]
    
    return df

def load_transactions(file):
    try:
        # Try reading with different encodings if needed
        try:
            df = pd.read_csv(file)
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding='latin1')
            
        # Check if this is an M-Pesa file
        if 'Completion Time' in df.columns and 'Paid In' in df.columns:
            df = process_mpesa_data(df)
        else:
            st.error("Unsupported file format. Please upload an M-Pesa statement CSV.")
            return None
            
        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False

def display_expense_tab(debits_df):
    """Display the expenses tab with categorization and visualization"""
    col1, col2 = st.columns(2)
    
    with col1:
        new_category = st.text_input("New Category Name")
        add_button = st.button("Add Category")
        
        if add_button and new_category:
            if new_category not in st.session_state.categories:
                st.session_state.categories[new_category] = []
                save_categories()
                st.rerun()
    
    with col2:
        selected_category = st.selectbox("Add keyword to category", options=list(st.session_state.categories.keys()))
        new_keyword = st.text_input("New keyword for category")
        add_keyword_button = st.button("Add Keyword")
        
        if add_keyword_button and new_keyword:
            if add_keyword_to_category(selected_category, new_keyword):
                st.success(f"Keyword '{new_keyword}' added to {selected_category}")
            else:
                st.warning("Keyword already exists or is empty")
    
    st.subheader("Your Expenses")
    edited_df = st.data_editor(
        debits_df[['Date', 'Details', 'Amount', 'Category']],
        column_config={
            'Date': st.column_config.DateColumn('Date', format='DD/MM/YYYY'),
            'Amount': st.column_config.NumberColumn('Amount', format='%.2f'),
            'Category': st.column_config.SelectboxColumn(
                'Category',
                options=list(st.session_state.categories.keys())
            )
        },
        hide_index=True,
        use_container_width=True,
        key='category_editor'
    )
    
    save_button = st.button('Apply Changes', type='primary')
    if save_button:
        for idx, row in edited_df.iterrows():
            new_category = row['Category']
            if new_category == debits_df.at[idx, 'Category']:
                continue
            
            details = row['Details']
            debits_df.at[idx, 'Category'] = new_category
            add_keyword_to_category(new_category, details)
            
    st.subheader('Expense Summary')
    category_totals = debits_df.groupby('Category')['Amount'].sum().reset_index()
    category_totals = category_totals.sort_values('Amount', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(
            category_totals, 
            column_config={
             'Amount': st.column_config.NumberColumn('Amount', format='%.2f')   
            },
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        fig = px.pie(
            category_totals,
            values='Amount',
            names='Category',
            title='Expenses by Category'
        )
        st.plotly_chart(fig, use_container_width=True)

def display_payments_tab(credits_df):
    """Display the payments/credits tab"""
    st.subheader('Payments Summary')
    total_payments = credits_df['Amount'].sum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric('Total Payments', f'{total_payments:,.2f}')
    
    with col2:
        st.metric('Number of Payments', len(credits_df))
    
    # Show top payment recipients
    st.subheader('Top Payment Recipients')
    credits_df['Recipient'] = credits_df['Details'].str.extract(r'to (.*)')
    top_recipients = credits_df.groupby('Recipient')['Amount'].sum().nlargest(5).reset_index()
    
    fig = px.bar(
        top_recipients,
        x='Recipient',
        y='Amount',
        title='Top 5 Payment Recipients'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(credits_df, use_container_width=True)

def main():
    st.title('M-Pesa Finance Dashboard')
    
    uploaded_file = st.file_uploader('Upload your M-Pesa statement CSV', type=['csv'])
    
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            debits_df = df[df['Debit/Credit'] == 'Debit'].copy()
            credits_df = df[df['Debit/Credit'] == 'Credit'].copy()
            
            st.session_state.debits_df = debits_df.copy()
            
            tab1, tab2 = st.tabs(['Expenses (Debits)', 'Payments (Credits)'])
            with tab1:
                display_expense_tab(debits_df)
            
            with tab2:
                display_payments_tab(credits_df)

if __name__ == '__main__':
    main()