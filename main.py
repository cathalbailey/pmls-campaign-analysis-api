from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# 1. Load and prepare data (runs once when the app starts)
file_path = "/Users/cathalbailey/Documents/Data Science Institute/PMLS/"
df_purchase = pd.read_csv(file_path + "Purchase Data 1.csv")
df_response = pd.read_csv(file_path + "Response Data.csv")

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
    return "<h2>Campaign Analysis API</h2><p>Go to <a href='/campaign-analysis'>/campaign-analysis</a> to view results.</p>"

@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    # Generate the 4 tables
    t1 = calculate_table(df, 'Gender_Label')
    t2 = calculate_table(df, 'Age_Group')
    t3 = calculate_table(df, 'Last_Quarter_Purchase')
    t4 = calculate_table(df, 'Product_Usage')
    
    # Convert DataFrames to HTML tables
    html_content = f"""
    <html>
        <head>
            <title>Campaign Analysis Results</title>
            <style>
                table {{ border-collapse: collapse; margin-bottom: 25px; width: 50%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h3 {{ font-family: Arial, sans-serif; }}
            </style>
        </head>
        <body>
            <h2>Marketing Campaign Analysis Results</h2>
            <h3>1. Gender vs Campaign Response</h3>
            {t1.to_html(index=False)}
            
            <h3>2. Age Group vs Campaign Response</h3>
            {t2.to_html(index=False)}
            
            <h3>3. Purchase in Last Quarter vs Campaign Response</h3>
            {t3.to_html(index=False)}
            
            <h3>4. Product Usage vs Campaign Response</h3>
            {t4.to_html(index=False)}
        </body>
    </html>
    """
    return html_content
