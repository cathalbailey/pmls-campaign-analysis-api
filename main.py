from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI(title="Campaign Analysis API", version="1.0")

# Load and prepare data (from PMLS-assignment1.ipynb)
df_purchase = pd.read_csv("Purchase Data 1.csv")
df_response = pd.read_csv("Response Data.csv")

df = pd.merge(df_purchase, df_response, on="Custid")

# Apply transformations
df['Gender_Label'] = df['Gender'].map({1: 'Male', 2: 'Female'})
df['Age_Group'] = df['Age'].map({1: '<30', 2: '30-50', 3: '>50'})
df['Last_Quarter_Purchase'] = df['Pre_Month'].map({1: 'Yes', 2: 'No'})

# Product Usage categorization
bins = [0, 4, 8, float('inf')]
labels = ['1-4', '5-8', '>8']
df['Product_Usage'] = pd.cut(df['N_Products'], bins=bins, labels=labels)

# Helper function from notebook
def get_response_rate_table(dataframe, group_column):
    summary = dataframe.groupby(group_column, observed=False)['Response'].agg(
        Total_Customers='count',
        Responded_Customers='sum',
        Response_Rate_Pct=lambda x: round(x.mean() * 100, 2)
    ).reset_index()
    return summary

# Generate analysis tables
t1_gender = get_response_rate_table(df, 'Gender_Label')
t2_age = get_response_rate_table(df, 'Age_Group')
t3_quarter = get_response_rate_table(df, 'Last_Quarter_Purchase')
t4_usage = get_response_rate_table(df, 'Product_Usage')

@app.get("/")
def home():
    return {"message": "Campaign analysis API is live. Visit /campaign-analysis for results."}

@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    """Display campaign analysis results in tabular format"""

    html_content = f"""
    <html>
        <head>
            <title>Campaign Analysis Results</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 30px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 40px;
                }}
                .section {{
                    background-color: white;
                    padding: 25px;
                    margin-bottom: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #007bff;
                    font-size: 18px;
                    margin-top: 0;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 15px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #007bff;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                tr:hover {{
                    background-color: #f0f0f0;
                }}
            </style>
        </head>
        <body>
            <h1>Marketing Campaign Analysis Results</h1>

            <div class="section">
                <h2>Task 1: Gender vs Campaign Response</h2>
                {t1_gender.to_html(index=False, border=0)}
            </div>

            <div class="section">
                <h2>Task 2: Age Group vs Campaign Response</h2>
                {t2_age.to_html(index=False, border=0)}
            </div>

            <div class="section">
                <h2>Task 3: Purchase in Last Quarter vs Campaign Response</h2>
                {t3_quarter.to_html(index=False, border=0)}
            </div>

            <div class="section">
                <h2>Task 4: Product Usage vs Campaign Response</h2>
                {t4_usage.to_html(index=False, border=0)}
            </div>
        </body>
    </html>
    """
    return html_content

# JSON endpoints for Excel Power Query
@app.get("/campaign-analysis/json")
def campaign_analysis_json():
    """Return all campaign analysis results as JSON for Excel Power Query"""
    return {
        "task1_gender": t1_gender.to_dict(orient='records'),
        "task2_age": t2_age.to_dict(orient='records'),
        "task3_quarter": t3_quarter.to_dict(orient='records'),
        "task4_usage": t4_usage.to_dict(orient='records')
    }

@app.get("/campaign-analysis/gender")
def get_gender_table():
    """Return just the gender analysis table as JSON"""
    return t1_gender.to_dict(orient='records')

@app.get("/campaign-analysis/age")
def get_age_table():
    """Return just the age analysis table as JSON"""
    return t2_age.to_dict(orient='records')

@app.get("/campaign-analysis/quarter")
def get_quarter_table():
    """Return just the quarter purchase table as JSON"""
    return t3_quarter.to_dict(orient='records')

@app.get("/campaign-analysis/usage")
def get_usage_table():
    """Return just the product usage table as JSON"""
    return t4_usage.to_dict(orient='records')
