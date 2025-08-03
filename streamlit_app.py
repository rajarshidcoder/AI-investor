import streamlit as st
from time import sleep
import yfinance as yf
import google.generativeai as genai
import json




def initialize_gemini(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")

tickers_to_fetch = ['^CNXAUTO', '^NSEBANK', '^CNXFMCG', '^CNXIT', '^CNXMEDIA', '^CNXMETAL', '^CNXPHARMA', '^CNXPSUBANK', '^CNXREALTY', '^CNXENERGY', '^CNXINFRA', '^CNXCONSUM', '^CNXSERVICE']
text = '**Suggestion:** FMCG\n**Ticker name:** ^CNXFMCG\n**Reason:** FMCG shows relatively high and stable performance compared to other sectors during the given period, indicating consistent demand and lower volatility.\n'

def genAI(prompt: str) -> str:
    resonse = model.generate_content(prompt)
    return resonse.text

def gather_stock_data(result):
    for word in result.split():
        if word.startswith("^"):
            ticker = word
            break
    with open('list_stock.json', 'r') as f:
        json_data = json.load(f)
    tickers_stock = [data[1] for data in json_data[ticker]['List of stocks']]
    stock_data = yf.download(tickers_stock, period='10d',rounding=True,progress=False)
    stock_data.dropna()
    return stock_data['Close'].to_csv()



st.set_page_config(layout="wide",initial_sidebar_state='expanded')

st.title("AI Investor")
st.write("An AI agent which will extract the data from the open web to gather strong moving stocks and recomend them to the user for optimal profit wrt historical data and analysis")
st.divider()

with st.sidebar:
    api_key = st.text_input(
            "Google API key",
            type="password",
            help="Enter your google API key to access Gemini models"
            )
    
    st.divider()
    url = "https://github.com/rajarshidcoder/AI-investor"
    st.subheader(f"Github [link]({url}) for this project")


col1, col2, col3 = st.columns(3)

with col1:
    money = st.number_input('Capital investing',step=100,min_value=10000,help="Enter the amount you want to invest")
with col2:
    term = st.selectbox('Term of investing',['Short Term','Long Term'],index=None,help="Which mode of investing you want to do?")
with col3:
    if term == 'Short Term':
        options = [f"{i} Months" for i in range(3,12)]
    elif term == 'Long Term':
        options = [f"{i} Years" for i in range(1,11)]
    else:
        options = []
    
    time = st.selectbox('Time of investing',options,index=None,help="For how long you wish to invest your money?")

if money and term and time and api_key:
    clicked = st.button("Submit", use_container_width=True)
    model = initialize_gemini(api_key)
else:
    clicked = st.button("Submit", use_container_width=True, disabled=True)

generation1 = "'Suggestion: ^CNXFMCG\nTicker name: ^CNXFMCG\nReason:  ^CNXFMCG shows the highest closing value (56541.8) among all the indices listed in the provided data.\n'"
if clicked:
    #downloading index data from yfin
    with st.spinner("Downloading files form the web",show_time=True):
        data = yf.download(tickers_to_fetch, period='10d',rounding=True,progress=False)
        csv_data = data.to_csv(index=False)
        prompt = f'''
                {csv_data}

                which index is wise to invest according to this and current market data, just use statistics and basic common sence.
                Answer in exact format below
                Suggestion: <human understaning index name>
                Ticker name: <Exact ticker name as given above>
                Reason: <One sentence result>
                '''
    #generating data using Index data
    with st.spinner("Gathering data from Gemini",show_time=True):
        index_responce = genAI(prompt)
    #printing Index data
    st.subheader("Index Suggestion from past data")
    for lines in index_responce.split("\n"):
        st.markdown(lines)



    #downloading stock data from yfin
    with st.spinner("Downloading Stock Data for selected Index",show_time=True):
        sleep(2)
        csv_data = gather_stock_data(index_responce)
        prompt2 = f'''

                {csv_data}

                give your opinion on where to invest in according to this data and if user have {time} to invest with {money}, how much the user should expect?

                give the result ONLY 

                Suggestion: <Real human understanding stock Name, not the ticker>
                Reason: <Give good insights of the selected stock in one sentence>
                Expected return: <Give exact value in %>
                Final return: <give an estimated numerical value with ₹ (in indian comma schema) calculated if {money} amount of money is invested for {time}, use compounding>
                Disclamer: <short disclamer as you are an AI>
            '''

    #generating data using Stock data
    with st.spinner("Gathering data from Gemini",show_time=True):
        stock_responce = genAI(prompt2)



    st.subheader("Stock Suggestion from best performing Index")
    # stock_text = 'Suggestion: Varun Beverages\nReason: Varun Beverages shows a consistent upward trend, suggesting growth potential over the observed period.\nExpected return: 1.89%\nFinal return: ₹ 1,01,890\nDisclaimer: I am an AI and this is not financial advice. Consult a financial expert before making investment decisions.\n'
    for lines in stock_responce.split("\n"):
        st.markdown(lines)









