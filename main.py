from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# 1. Load and prepare data
df_purchase = pd.read_csv("Purchase Data 1.csv")
df_response = pd.read_csv("Response Data.csv")

df = pd.merge(df_purchase, df_response, on="Custid")

# Apply assumptions
df['Gender_Label'] = df['Gender'].map({1: 'Male', 2: 'Female'})
df['Age_Group'] = df['Age'].map({1: '<30', 2: '30-50', 3: '>50'})
df['Last_Quarter_Purchase'] = df['Pre_Month'].map({1: 'Yes', 2: 'No'})

bins = [0, 4, 8, float('inf')]
labels = ['1-4', '5-8', '>8']
df['Product_Usage'] = pd.cut(df['N_Products'], bins=bins, labels=labels)

def calculate_table(dataframe, group_column):
    summary = dataframe.groupby(group_column, observed=False)['Response'].agg(
        Total_Customers='count',
        Responded_Customers='sum',
        Response_Rate_Pct=lambda x: round(x.mean() * 100, 2)
    ).reset_index()
    return summary

@app.get("/", response_class=HTMLResponse)
def home():
    return "
