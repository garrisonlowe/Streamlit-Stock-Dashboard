import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from itertools import islice
from plotly.subplots import make_subplots

# Setting the page configuration
st.set_page_config(page_title="Stocks Dashboard", page_icon="💹", layout = "wide")

# Loading the data
data = pd.read_csv("data/candle_data.csv")
tickers = pd.read_csv("data/tickers_list.csv")
financial = pd.read_csv("data/financial_data.csv")
valuations = pd.read_csv("data/valuations_data.csv")

# Getting the symbols
symbols = data['Symbol'].unique()
symbols = symbols.tolist()

# Mapping period to number of days
mapping_period = {"1D": 1, "1M": 21, "3M": 64, "6M": 128, "1Y": 260, "2Y": 518, "5Y": 1296}

# Function to display the header
def header(valuations, selected_data):
    selected_valuation = valuations[valuations['Symbol'] == selected_data['Symbol'].iloc[0]]
    st.title(f"{selected_valuation['longName'].iloc[0]}")

# Function to filter the symbol and period
def filter_symbol_widget():
    with st.sidebar:
        st.title ("📈 Stock Dashboard App")
        selected_symbol = st.selectbox("📰 Select a symbol:", symbols)
        selected_period = st.selectbox("📅 Select a period:", ["1D", "1M", "3M", "6M", "1Y", "2Y", "5Y"])
    
    return selected_symbol, selected_period

# Function to define the style of the metrics
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
    
def custom_metric_two(label, value):
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
            <div style="font-size: 20px; margin-bottom: 8px; padding-top: 35px;">
                <strong>{label}</strong><br>
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Function to display the metrics
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
        
# Function to display the dataframe
def display_df(selected_data, selected_period, selected_symbol):
    st.subheader(f"**🕓 {selected_symbol} Price Data**")
    with st.container():
        selected_data = selected_data.iloc[-mapping_period[selected_period]:]
        selected_data = selected_data.reset_index(drop=True)  
        selected_data = selected_data.sort_values(by='Date', ascending=False)
        selected_data = selected_data.set_index('Date')  
        
        st.dataframe(selected_data, use_container_width=True)

# Function to display the info cards        
def info_cards(selected_data, selected_period, financial):

    with st.container():
        left_column,  col1, col2, col3, col4, col5 = st.columns([1,3,1,1,1,1])
        
        selected_data = selected_data.iloc[-mapping_period[selected_period]:]
        
        financial = financial[financial['Symbol'] == selected_data['Symbol'].iloc[0]]
        
        # Calculate the price difference and percentage
        current_price = selected_data['Close'].iloc[-1]
        initial_price = selected_data['Close'].iloc[0]
        price_difference = current_price - initial_price
        price_diff_percentage = (price_difference / initial_price) * 100
        highest_price = selected_data['High'].max()
        lowest_price = selected_data['Low'].min()
        highest_volume = selected_data['Volume'].max()
        lowest_volume = selected_data['Volume'].min()
        
        if price_difference > 0:
            color = "green"
            arrow = "▲"
            background_color = "#d4edda"  # light green
        else:
            color = "red"
            arrow = "▼"
            background_color = "#f8d7da"  # light red
            
     
        # Display the metrics
        left_column.markdown(
            f"""
            <div style="text-align: left; margin: 0;">
                <p style="margin: 0; font-size: 20px; line-height: 1.0; margin-bottom: 8px; margin-top: 15px;"> <strong>Current Price</p>
                <p style="font-size: 40px; margin: 0; line-height: 1.0; margin-bottom: 10px;">${current_price:.2f}</p>
                <p style="font-size: 16px; color: {color}; background-color: {background_color}; border-radius: 5px; padding: 2px 5px; display: inline-block; width: auto; margin: 0; margin-bottom: 20px;">
                    {arrow} ${price_difference:.2f} ({price_diff_percentage:.2f}%)
                </p>
            </div>  
            """,
            unsafe_allow_html=True
            )
        with col2:
            custom_metric_two("Highest Price", f"${highest_price:,.2f}")
        
        with col3:
            custom_metric_two("Lowest Price", f"${lowest_price:,.2f}")
            
        with col4:
            custom_metric_two("Highest Volume", f"${highest_volume:,.0f}")
            
        with col5:
            custom_metric_two("Lowest Volume", f"${lowest_volume:,.0f}")
                
# Function to display the chart
def display_chart(selected_data, selected_period, financial):

    with st.container():
        # Calculate moving averages on the entire dataset
        selected_data['MA20'] = selected_data['Close'].rolling(window=20).mean()
        selected_data['MA50'] = selected_data['Close'].rolling(window=50).mean()

        # Slice the dataset based on the selected period
        selected_data = selected_data.iloc[-mapping_period[selected_period]:]
        selected_data = selected_data.reset_index()  
        financial = financial[financial['Symbol'] == selected_data['Symbol'].iloc[0]]

        # Create subplots with shared x-axis
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            row_heights=[0.8, 0.2], vertical_spacing=0.2,
                            subplot_titles=('', 'Volume Chart'))

        # Add candlestick chart to the first row
        fig.add_trace(go.Candlestick(
            x=selected_data['Date'],
            open=selected_data['Open'],
            high=selected_data['High'],
            low=selected_data['Low'],
            close=selected_data['Close'],
            name='Candlestick',
            increasing_line_color='green',  
            decreasing_line_color='red'    
        ), row=1, col=1)

        # Add moving averages to the first row
        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['MA20'], mode='lines', name='MA20', line_shape='spline', line=dict(color='light blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=selected_data['Date'], y=selected_data['MA50'], mode='lines', name='MA50', line_shape='spline', line=dict(color='orange')), row=1, col=1)

        # Add volume bar chart to the second row
        fig.add_trace(go.Bar(x=selected_data['Date'], y=selected_data['Volume'], name='Volume', marker_color='violet'), row=2, col=1)

        # Set the layout properties
        fig.update_layout(
            xaxis_title='',  
            yaxis_title='Price',
            height=800,
            margin=dict(t=50, b=50),  
            updatemenus=[{
                'type': 'buttons',
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
                'direction': 'left',
                'pad': {'r': 10, 't': 10},
                'showactive': True,
                'x': -0.036,
                'xanchor': 'left',
                'y': 1.1,
                'yanchor': 'top'
            }]
        )

        st.plotly_chart(fig)

    

# Function to display the financials
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

# Main function
def main():
    # Putting selected symbol and period into variables
    selected_symbol, selected_period = filter_symbol_widget()
    selected_data = data[data['Symbol'] == selected_symbol]
    
    header(valuations, selected_data)
    display_metrics(selected_data, financial, valuations)
    info_cards(selected_data, selected_period, financial)
    # Filtering the dataframe
    display_chart(selected_data, selected_period, financial)
    display_financials(selected_data, valuations)
    display_df(selected_data, selected_period, selected_symbol)
    
# Running the main function
if __name__ == "__main__":
    main()