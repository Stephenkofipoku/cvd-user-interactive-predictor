from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import gspread
from google.oauth2.service_account import Credentials
import joblib

# Set up credentials and authorize the Google Sheets API
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Create Flask app instance
app = Flask(__name__)

def authorize_google_sheets():
    """Authorize and return the Google Sheets client."""
    creds = Credentials.from_service_account_file('creds.json')
    scoped_creds = creds.with_scopes(SCOPE)
    gspread_client = gspread.authorize(scoped_creds)
    return gspread_client

# Load the dataset from Google Sheets
def load_dataset():
    client = authorize_google_sheets()
    sheet = client.open('cvddataset').sheet1
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    return df

# Define features and target
df = load_dataset()
features = df.drop("TenYearCHD", axis=1)
target = df["TenYearCHD"]

# Load the trained model, label encoder, and scaler
model = joblib.load('https://docs.google.com/spreadsheets/d/1kRXbEr_BYg6MqaL7znP5SXXrgBB0HPRJ4WXMZ4ldOFM/edit?usp=sharing')
label_encoder = LabelEncoder()
scaler = StandardScaler()

# Fit the label encoder and scaler on your data
label_encoder.fit(features["sex"])  # Assuming "sex" is a categorical column
scaler.fit(features)  # Fit scaler on your features

# Predict function
def predict_cvd_risk(data):
    """Predict CVD risk using the loaded model, label encoder, and scaler."""
    # Encode categorical variables in the input data
    data["sex"] = label_encoder.transform([data["sex"]])[0]
    # Repeat encoding for other categorical variables

    # Standardize input data
    scaled_data = scaler.transform([data.values])

    # Make prediction
    prediction = model.predict(scaled_data)
    return prediction[0]

# Flask routes
@app.route('/')
def index():
    """Render the index.html template."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to receive JSON data and return CVD risk prediction."""
    data = request.get_json()

    try:
        result = predict_cvd_risk(data)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
