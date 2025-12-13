import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import pickle
from statsmodels.tsa.arima.model import ARIMA
import joblib

# Load CSV
df = pd.read_csv("../data/DSNY_Monthly_Tonnage_Data.csv")
df['MONTH'] = pd.to_datetime(df['MONTH'])
df = df[df['MONTH'] >= '2022-01-01']
df['id'] = (df['BOROUGH'] + df['COMMUNITYDISTRICT'].astype(str)).str.lower().str.replace(' ','', regex=True)
df['proportionrefuse'] = (df['PAPERTONSCOLLECTED'] + df['MGPTONSCOLLECTED']) / (
    df['PAPERTONSCOLLECTED'] + df['MGPTONSCOLLECTED'] + df['REFUSETONSCOLLECTED']
)

# User input
col1, col2, col3 = st.columns([2,3,1])
with col2: #center column
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/59/New_York_City_Department_of_Sanitation_logo.svg/2560px-New_York_City_Department_of_Sanitation_logo.svg.png",width=200)

st.title(body="Recycle Percentage Estimation Tool",width='stretch')

st.markdown(body="### Our tool is used internally by the Department of Sanitation,\n" \
"##### We've summed all recyclables (plastic, paper, glass, metal) and divided by all waste (including recyclables) to find percentage.\n" \
"##### The goal of our tool is to provide the best predictive model by district and borough between SARIMA, ARIMA, and baseline (decided by RMSE).\n")

col1, col2 = st.columns(2)

with col2: # Place the text input in the middle column
    user_input = st.text_input("Enter a borough and district (FORMAT: bronx1):")


if user_input:

    filtered = df[df['id'] == user_input]
    filtered = filtered[(filtered['MONTH'] >= '2023') & (filtered['MONTH'] < '2025')]
    s = filtered.set_index('MONTH')['proportionrefuse'].asfreq('D').dropna()

    # Train/test split
    split_idx = int(len(s) * 0.70)
    train = s.iloc[:split_idx]
    test  = s.iloc[split_idx:]

    # Baseline
    with open("../models/baseline.pkl", "rb") as f:
        baseline_model = joblib.load(f)
    baseline_pred = baseline_model[user_input]
    rmse_baseline = np.sqrt(mean_squared_error(test, baseline_pred))
    st.write(f"Baseline RMSE: {rmse_baseline:,.3f}")

    # Load ARIMA pickle
    with open("../models/modeling_simple.pkl", "rb") as f:
        arima_models = pickle.load(f)
    arima_model = arima_models[user_input]

    # Forecast exactly test length
    arima_forecast = arima_model.forecast(steps=len(test))
    arima_forecast.index = test.index
    rmse_arima = np.sqrt(mean_squared_error(test, arima_forecast))
    st.write(f"ARIMA RMSE: {rmse_arima:,.3f}")

    # Repeat for SARIMA
    with open("../models/modeling_tuned.pkl", "rb") as f:
        sarima_models = joblib.load(f)
    sarima_model = sarima_models[user_input]
    sarima_forecast = sarima_model.forecast(steps=len(test))
    sarima_forecast.index = test.index
    rmse_sarima = np.sqrt(mean_squared_error(test, sarima_forecast))
    st.write(f"SARIMA RMSE: {rmse_sarima:,.3f}")

    # Determine best model
    rmse_dict = {"Baseline": rmse_baseline, "ARIMA": rmse_arima, "SARIMA": rmse_sarima}
    best_rmse = min(rmse_dict.values())
    best_models = [name for name, rmse in rmse_dict.items() if rmse == best_rmse]
    st.markdown(f"### Best model: **:green[{best_models}]**")

    # Plot
    plt.figure(figsize=(14,8))
    plt.plot(train, label="Train")
    plt.plot(test, label="Actual (Test)", color="#ff7f0e")
    if "SARIMA" in best_models:
        plt.plot(sarima_forecast, label="SARIMA Forecast", color="#2ca02c", linestyle="--")
    if "ARIMA" in best_models:
        plt.plot(arima_forecast, label="ARIMA Forecast", color="#2ca02c", linestyle="--")
    if "Baseline" in best_models:
        plt.plot(baseline_pred, label="Baseline Forecast", color="#2ca02c", linestyle="--")
    plt.legend(fontsize = 16)
    plt.xlabel("Date", fontsize=20,labelpad=16) # Change font size here
    plt.ylabel("Percentage of Recyclables", fontsize=20,labelpad=16)
    plt.title(f"{best_models} Model", fontsize = 24)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    st.pyplot(plt)
