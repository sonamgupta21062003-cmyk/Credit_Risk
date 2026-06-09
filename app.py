import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import joblib
import warnings 

# ====================================
# PAGE CONFIG
# ====================================

st.set_page_config(
    page_title="Credit Risk Prediction",
    page_icon="💳",
    layout="wide"
)

# ====================================
# LOAD MODEL
# ====================================

pipeline = joblib.load("credit_risk_pipeline.pkl")

# ====================================
# DATABASE
# ====================================

def create_table():

    conn = sqlite3.connect("credit_risk.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_age INTEGER,
        person_income REAL,
        loan_amount REAL,
        loan_grade TEXT,
        loan_intent TEXT,
        risk_probability REAL,
        risk_level TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_prediction(
    age,
    income,
    amount,
    grade,
    intent,
    probability,
    risk
):

    conn = sqlite3.connect("credit_risk.db")

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions(
        person_age,
        person_income,
        loan_amount,
        loan_grade,
        loan_intent,
        risk_probability,
        risk_level
    )
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        age,
        income,
        amount,
        grade,
        intent,
        probability,
        risk
    ))

    conn.commit()
    conn.close()


create_table()

# ====================================
# SIDEBAR
# ====================================

st.sidebar.title("💳 Credit Risk Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "Prediction",
        "History",
        "Analytics"
    ]
)


# ====================================
# PREDICTION PAGE
# ====================================
if page == "Prediction":

    st.title("💳 Credit Risk Prediction System")

    col1, col2 = st.columns(2)

    with col1:

        person_age = st.number_input(
            "Age",
            18,
            100,
            30
        )

        person_income = st.number_input(
            "Annual Income",
            1000,
            1000000,
            50000
        )

        person_emp_length = st.number_input(
            "Employment Length",
            0,
            50,
            5
        )

        person_home_ownership = st.selectbox(
            "Home Ownership",
            [
                "RENT",
                "OWN",
                "MORTGAGE",
                "OTHER"
            ]
        )

        cb_person_default_on_file = st.selectbox(
            "Previous Default",
            [
                "N",
                "Y"
            ]
        )

    with col2:

        loan_amnt = st.number_input(
            "Loan Amount",
            1000,
            500000,
            10000
        )

        loan_int_rate = st.number_input(
            "Interest Rate",
            1.0,
            40.0,
            10.0
        )

        loan_percent_income = st.number_input(
            "Loan Percent Income",
            0.01,
            1.0,
            0.20
        )

        cb_person_cred_hist_length = st.number_input(
            "Credit History Length",
            1,
            50,
            5
        )

    loan_intent = st.selectbox(
        "Loan Intent",
        [
            "EDUCATION",
            "MEDICAL",
            "VENTURE",
            "PERSONAL",
            "DEBTCONSOLIDATION",
            "HOMEIMPROVEMENT"
        ]
    )

    loan_grade = st.selectbox(
        "Loan Grade",
        [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G"
        ]
    )
# LoanBurden
loan_burden = st.number_input("Loan Burden")
loan_amount = st.number_input("Loan Amount")
annual_income = st.number_input("Annual Income")

loan_burden = loan_amount / annual_income if annual_income > 0 else 0
if st.button("Predict Risk"):

    loan_burden = loan_amnt / max(person_income, 1)

    if person_income <= 30000:
        income_category = "Low"
    elif person_income <= 70000:
        income_category = "Medium"
    elif person_income <= 150000:
        income_category = "High"
    else:
        income_category = "Very High"

    if person_age <= 25:
        age_group = "18-25"
    elif person_age <= 35:
        age_group = "26-35"
    elif person_age <= 50:
        age_group = "36-50"
    else:
        age_group = "50+"

    input_df = pd.DataFrame({
        
    "LoanBurden": [loan_burden]
})
        
    
st.write("Button Clicked")
if st.button("Suggested Risk"):

    input_df = pd.DataFrame({

         "person_age":[person_age],
        "person_income":[person_income],
        "person_home_ownership":[person_home_ownership],
        "person_emp_length":[person_emp_length],

        "loan_intent":[loan_intent],
        "loan_grade":[loan_grade],

        "loan_amnt":[loan_amnt],
        "loan_int_rate":[loan_int_rate],
        "loan_percent_income":[loan_percent_income],

        "cb_person_default_on_file":[cb_person_default_on_file],
        "cb_person_cred_hist_length":[cb_person_cred_hist_length],

    # engineered features
        "LoanBurden":[loan_burden],
        "IncomeCategory":[income_category],
        "AgeGroup":[age_group]
        })
    

    probability = pipeline.predict_proba(
            input_df
        )[0][1]

    prediction = pipeline.predict(
            input_df
        )[0]

    if probability < 0.30:

            risk = "LOW"
            recommendation = "Approve Loan"

            st.success(
                f"Risk Level : {risk}"
            )

    elif probability < 0.70:

            risk = "MEDIUM"
            recommendation = "Manual Review Required"

            st.warning(
                f"Risk Level : {risk}"
            )

    else:

            risk = "HIGH"
            recommendation = "Reject Loan"

            st.error(
                f"Risk Level : {risk}"
            )

    c1,c2,c3 = st.columns(3)

    c1.metric(
            "Risk Probability",
            f"{probability:.2%}"
        )

    c2.metric(
            "Recommendation",
            recommendation
        )

    c3.metric(
            "Loan Amount",
            f"₹{loan_amnt:,.0f}"
        )

    st.progress(float(probability))

    save_prediction(
            person_age,
            person_income,
            loan_amnt,
            loan_grade,
            loan_intent,
            probability,
            risk
        )

# ====================================
# HISTORY PAGE
# ====================================

elif page == "History":

    st.title("Prediction History")

    conn = sqlite3.connect(
        "credit_risk.db"
    )

    history = pd.read_sql(
        "SELECT * FROM predictions",
        conn
    )

    st.dataframe(
        history,
        use_container_width=True
    )

# ====================================
# ANALYTICS PAGE
# ====================================

elif page == "Analytics":

    st.title("Portfolio Analytics")

    conn = sqlite3.connect(
        "credit_risk.db"
    )

    history = pd.read_sql(
        "SELECT * FROM predictions",
        conn
    )

    if len(history) > 0:

        st.subheader(
            "Risk Distribution"
        )

        st.bar_chart(
            history["risk_level"]
            .value_counts()
        )

        st.subheader(
            "Average Risk"
        )

        st.metric(
            "Average Probability",
            f"{history['risk_probability'].mean():.2%}"
        )

        st.subheader(
            "Loan Grade Risk"
        )

        grade_df = history.groupby(
            "loan_grade"
        )["risk_probability"].mean()

        st.bar_chart(
            grade_df
        )

    else:

        st.info(
            "No prediction history found."
        )