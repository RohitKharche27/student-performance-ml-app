import streamlit as st
import pandas as pd
import pickle
import os
import numpy as np

# --- Page config ------------------------------------------------------------
st.set_page_config(page_title="Student Performance Predictor", layout="centered")

# --- Simple CSS ------------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
        font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(20,20,40,0.06);
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Title ------------------------------------------------------------
st.title("📚 Student Performance Predictor")
st.write("Enter the student details to predict the Score using the trained model.")
st.markdown("---")

# --- Load dataset to auto-detect column names -----------------------
csv_path = "student_scores (1).csv"
if not os.path.exists(csv_path):
    st.error("Dataset file not found. Please upload it to the same folder.")
    st.stop()

df = pd.read_csv(csv_path)

# detect target and feature columns
cols_lower = [c.lower() for c in df.columns]
target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None

feature_cols = [c for c in df.columns if c != target_col]

# --- Load model ------------------------------------------------------
model_path = "student_score.pkl"
if not os.path.exists(model_path):
    st.error("Model file not found. Please upload student_score.pkl.")
    st.stop()

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Could not load model: {e}")
    st.stop()

expected_features = getattr(model, "n_features_in_", None)

# --- Input fields ----------------------------------------------------
st.subheader("Enter Student Inputs")

input_values = []
cols = st.columns(len(feature_cols))

for i, feat in enumerate(feature_cols):
    col_data = df[feat].dropna()

    # Mean as default
    try:
        default = float(round(col_data.mean(), 2))
    except:
        default = 0.0

    # Numeric input
    if pd.api.types.is_numeric_dtype(col_data):
        min_val = float(col_data.min())
        max_val = float(col_data.max())
        step = (max_val - min_val) / 100 if max_val != min_val else 1

        with cols[i]:
            val = st.number_input(feat, value=default, step=step, format="%.2f")
    else:
        with cols[i]:
            val = st.text_input(feat, value=str(default))

    input_values.append(val)

# --- Predict ---------------------------------------------------------
if st.button("Predict Score"):
    X = []
    for v in input_values:
        try:
            X.append(float(v))
        except:
            X.append(v)

    # Check feature count
    if expected_features is not None and expected_features != len(X):
        st.error(
            f"Feature mismatch: model expects {expected_features} inputs but you provided {len(X)}.\n"
            "This means the model was trained on different features."
        )
    else:
        try:
            pred = model.predict([X])
            st.success(f"Predicted Score: **{pred[0]}**")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

st.markdown("---")
