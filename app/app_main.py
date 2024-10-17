import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from itertools import islice
from plotly.subplots import make_subplots

data = pd.read_csv("candle_data.csv")
tickers = pd.read_csv("tickers_list.csv")
financial = pd.read_csv("financial_data.csv")
valuations = pd.read_csv("valuations_data.csv")

# Getting the symbols
symbols = data['Symbol'].unique()
symbols = symbols.tolist()

st.set_page_config(page_title="Stocks Dashboard", page_icon="💹", layout = "wide")
# st.html("styles.html")
pio.templates.default = "plotly_white"

mapping_period = {"1D": 1, "1M": 21, "3M": 64, "6M": 128, "1Y": 260, "2Y": 518, "5Y": 1296}

def header(valuations, selected_data):
    selected_valuation = valuations[valuations['Symbol'] == selected_data['Symbol'].iloc[0]]
    st.title(f"{selected_valuation['longName'].iloc[0]}")

def filter_symbol_widget():
    with st.sidebar:
        st.title ("📈 Stock Dashboard App")
        selected_symbol = st.selectbox("📰 Select a symbol:", symbols)
        selected_period = st.selectbox("📅 Select a period:", ["1D", "1M", "3M", "6M", "1Y", "2Y", "5Y"])
    
    return selected_symbol, selected_period

def custom_metric(label, value):
    st.markdown(
        f"""
        <div style="font-size: 20px; margin-bottom: 8px; padding-bottom: 10px;">
            <strong>{label}</strong><br>
            {value}
        </div>
        """,
        unsafe_allow_html=True
    )

def display_metrics(selected_data, financial, valuations):
    with st.sidebar:
        # Create a single column for metrics
        col = st
        selected_valuation = valuations[valuations['Symbol'] == selected_data['Symbol'].iloc[0]]
        selected_financial = financial[financial['Symbol'] == selected_data['Symbol'].iloc[0]]
    
        # Display statistics in the sidebar
        st.title("❓Company Info")
        custom_metric("Country", selected_valuation['country'].iloc[0])
        custom_metric("Sector", selected_valuation['sector'].iloc[0])
        custom_metric("Industry", selected_valuation['industryDisp'].iloc[0])
        
        st.title("💲Company Financials")
        custom_metric("Market Cap", f"${selected_valuation['marketCap'].iloc[0]:,.0f}")
        custom_metric("Enterprise Value", f"${selected_valuation['enterpriseValue'].iloc[0]:,.0f}")
        custom_metric("Total Cash", f"${selected_valuation['totalCash'].iloc[0]:,.0f}")
        custom_metric("Total Debt", f"${selected_valuation['totalDebt'].iloc[0]:,.0f}")
        custom_metric("Total Revenue", f"${selected_valuation['totalRevenue'].iloc[0]:,.0f}")
        custom_metric("Shares Outstanding", f"{selected_valuation['sharesOutstanding'].iloc[0]:,.0f}")
        custom_metric("Net Income", f"${selected_financial['Net Income'].iloc[0]:,.0f}")
        custom_metric("Operating Income", f"${selected_financial['Operating Income'].iloc[0]:,.0f}")
        custom_metric("Gross Profit", f"${selected_financial['Gross Profit'].iloc[0]:,.0f}")
        

def display_df(selected_data, selected_period, selected_symbol):
    st.subheader(f"**🕓 {selected_symbol} Price Data**")
    with st.container():
        selected_data = selected_data.iloc[-mapping_period[selected_period]:]
        selected_data = selected_data.reset_index()  # Reset index to access 'Date' as a column
        selected_data = selected_data.drop(columns=['index'])
        selected_data = selected_data.sort_values(by='Date', ascending=False)
        
        
        st.dataframe(selected_data, use_container_width=True)
        
def info_cards(selected_data, selected_period, financial, selected_symbol):
    # selected_valuation = valuations[valuations['Symbol'] == selected_data['Symbol'].iloc[0]]
    # st.title(f"{selected_valuation['longName'].iloc[0]}")
    with st.container():
        left_column, right_column = st.columns([1, 1])
        
        selected_data = selected_data.iloc[-mapping_period[selected_period]:]
        
        financial = financial[financial['Symbol'] == selected_data['Symbol'].iloc[0]]
        
        current_price = selected_data['Close'].iloc[-1]
        initial_price = selected_data['Close'].iloc[0]
        price_difference = current_price - initial_price
        price_diff_percentage = (price_difference / initial_price) * 100
        
        if price_difference > 0:
            color = "green"
            arrow = "▲"
            background_color = "#d4edda"  # light green
        else:
            color = "red"
            arrow = "▼"
            background_color = "#f8d7da"  # light red
        
        left_column.markdown(
            f"""
            <div style="text-align: left; margin: 0;">
                <p style="margin: 0; font-size: 20px; line-height: 1.0; margin-bottom: 8px; margin-top: 20px;">Current Price</p>
                <p style="font-size: 45px; margin: 0; line-height: 1.0; margin-bottom: 10px;">${current_price:.2f}</p>
                <p style="font-size: 16px; color: {color}; background-color: {background_color}; border-radius: 5px; padding: 2px 5px; display: inline-block; width: auto; margin: 0; margin-bottom: 15px;">
                    {arrow} ${price_difference:.2f} ({price_diff_percentage:.2f}%)
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_chart(selected_data, selected_period, financial):
    with st.container():
        selected_data = selected_data.iloc[-mapping_period[selected_period]:]
        selected_data = selected_data.reset_index()  # Reset index to access 'Date' as a column
        financial = financial[financial['Symbol'] == selected_data['Symbol'].iloc[0]]
    
        # Calculate moving averages
        selected_data['MA20'] = selected_data['Close'].rolling(window=20).mean()
        selected_data['MA50'] = selected_data['Close'].rolling(window=50).mean()
    
        # Create subplots with shared x-axis
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            row_heights=[0.8, 0.2], vertical_spacing=0.2,
                            subplot_titles=('Price Chart', 'Volume Chart'))
    
        # Add candlestick chart to the first row
        fig.add_trace(go.Candlestick(
            x=selected_data['Date'],
            open=selected_data['Open'],
            high=selected_data['High'],
            low=selected_data['Low'],
            close=selected_data['Close'],
            name='Candlestick'
        ), row=1, col=1)
    
        # Add moving averages to the first row
        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['MA20'], mode='lines', name='MA20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['MA50'], mode='lines', name='MA50'), row=1, col=1)
    
        # Add volume bar chart to the second row
        fig.add_trace(go.Bar(x=selected_data['Date'], y=selected_data['Volume'], name='Volume'), row=2, col=1)
    
        # Set the layout properties for width and height
        fig.update_layout(
            xaxis_title='',  
            yaxis_title='Price',
            height=800,
            margin=dict(t=50, b=50),  
            updatemenus=[{
                'buttons': [
                    {
                        'label': 'Show MA20',
                        'method': 'update',
                        'args': [{'visible': [True, True, False, True]}]
                    },
                    {
                        'label': 'Show MA50',
                        'method': 'update',
                        'args': [{'visible': [True, False, True, True]}]
                    },
                    {
                        'label': 'Show Both',
                        'method': 'update',
                        'args': [{'visible': [True, True, True, True]}]
                    },
                    {
                        'label': 'Hide All',
                        'method': 'update',
                        'args': [{'visible': [True, False, False, True]}]
                    }
                ],
                'direction': 'down',
                'showactive': True
            }]
        )
    
        st.plotly_chart(fig)
    
def display_financials(selected_data, valuations):
    with st.container():
        selected_valuation = valuations[valuations['Symbol'] == selected_data['Symbol'].iloc[0]]
        st.subheader(f"📊 {selected_data['Symbol'].iloc[0]} Metrics")
        metrics = [
            ("💲Price-to-Book Ratio", f"{selected_valuation['priceToBook'].iloc[0]:.2f}"),
            ("💲Debt-to-Equity Ratio", f"{selected_valuation['debtToEquity'].iloc[0]:.2f}"),
            ("💲PEG Ratio", f"{selected_valuation['pegRatio'].iloc[0]:.2f}"),
            ("💲Quick Ratio", f"{selected_valuation['quickRatio'].iloc[0]:.2f}"),
            ("💲Current Ratio", f"{selected_valuation['currentRatio'].iloc[0]:.2f}"),
            ("🔎Trailing PE", f"{selected_valuation['trailingPE'].iloc[0]:.2f}"),
            ("🔎Forward PE", f"{selected_valuation['forwardPE'].iloc[0]:.2f}"),
            ("🔎Revenue Per Share", f"${selected_valuation['revenuePerShare'].iloc[0]:.2f}"),
            ("🔎Return On Equity", f"{selected_valuation['returnOnEquity'].iloc[0]:.2f}"),
            ("🔎Enterprise value to EBIT", f"{selected_valuation['enterpriseToEbitda'].iloc[0]:.2f}"),
            
        ]
        
        cols = st.columns(5)
        for i, (label, value) in enumerate(metrics):
            col = cols[i % 5]
            col.metric(label, value)


def main():
    # putting selected symbol and period into variables
    selected_symbol, selected_period = filter_symbol_widget()
    selected_data = data[data['Symbol'] == selected_symbol]
    # display_metrics(selected_data, financial, valuations)
    header(valuations, selected_data)
    display_metrics(selected_data, financial, valuations)
    info_cards(selected_data, selected_period, financial, selected_symbol)
    # Filtering the dataframe
    display_chart(selected_data, selected_period, financial)
    display_financials(selected_data, valuations)
    display_df(selected_data, selected_period, selected_symbol)
    
    
   

if __name__ == "__main__":
    main()