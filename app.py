# app.py
import streamlit as st
import pandas as pd
import pickle
import os
import time

# ---------------- Page config ----------------
st.set_page_config(
    page_title="Smart Student Analyzer - Business",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------- Professional Business Gradient CSS ----------------
st.markdown(
    """
    <style>
    /* Base app background: professional navy -> royal blue gradient */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #0b4f6c 45%, #0b63a6 100%);
        color: #e6f0fb !important;
        font-family: "Inter", "Segoe UI", "Roboto", "Helvetica", Arial, sans-serif;
        padding: 14px;
    }

    /* Header card */
    .header {
        background: linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
        border-left: 4px solid rgba(255,255,255,0.08);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 14px;
        box-shadow: 0 6px 20px rgba(2,6,23,0.6);
    }
    .header h1 {
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        color: #fff;
    }
    .header p {
        margin: 6px 0 0;
        font-size: 13px;
        color: #cfe8ff;
        opacity: 0.9;
    }

    /* Input card - subtle glass over gradient */
    .input-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        box-shadow: 0 8px 30px rgba(2,6,23,0.55);
    }

    /* Labels (clear, professional) */
    label {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #eaf6ff !important;
    }

    /* Inputs (tall, touch-friendly) */
    .stNumberInput>div>div>input,
    .stTextInput>div>div>input {
        height: 46px;
        padding: 10px 12px;
        font-size: 15px;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.02);
        color: #eaf6ff !important;
    }

    /* Focus state */
    .stNumberInput>div>div>input:focus,
    .stTextInput>div>div>input:focus {
        outline: 2px solid rgba(11,99,166,0.35);
        box-shadow: 0 6px 18px rgba(11,99,166,0.15);
    }

    /* Predict button: professional blue */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg,#0b63a6,#0f9cf0);
        color: white;
        font-weight: 800;
        padding: 12px 16px;
        border-radius: 10px;
        border: none;
        font-size: 16px;
        box-shadow: 0 8px 24px rgba(11,99,166,0.28);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }

    /* Result box */
    .result {
        background: linear-gradient(90deg,#0ea5a0,#06b6d4);
        color: white;
        padding: 12px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 18px;
        text-align: center;
        margin-top: 12px;
        box-shadow: 0 8px 30px rgba(2,6,23,0.55);
    }

    /* Footer small text */
    .footer {
        color: rgba(235,245,255,0.85);
        font-size: 12px;
        opacity: 0.95;
        margin-top: 12px;
    }

    @media (max-width: 600px) {
        .stApp { padding: 10px; }
        .header h1 { font-size: 20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Header ----------------
st.markdown(
    """
    <div class="header">
      <h1>📊 Smart Student Analyzer — Business Edition</h1>
      <p>Professional prediction tool · Clean corporate gradient · Mobile-friendly</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load CSV and Model ----------------
CSV_PATH = "student_scores (1).csv"
MODEL_PATH = "student_score.pkl"

if not os.path.exists(CSV_PATH):
    st.error("Dataset CSV not found. Please upload `student_scores (1).csv` to the app folder.")
    st.stop()

if not os.path.exists(MODEL_PATH):
    st.error("Model file `student_score.pkl` not found. Please upload it to the app folder.")
    st.stop()

# read CSV
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

# detect target and feature columns
cols_lower = [c.lower() for c in df.columns]
target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
feature_cols = [c for c in df.columns if c != target_col]

if len(feature_cols) == 0:
    st.error("No input features detected in the CSV. Ensure the CSV has at least one input column.")
    st.stop()

# load model
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load model: {e}")
    st.stop()

expected_features = getattr(model, "n_features_in_", None)

# ---------------- Input Section ----------------
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.subheader("Enter input values")

user_inputs = {}
for i, feat in enumerate(feature_cols, start=1):
    label = f"{i}. {feat.replace('_', ' ')}"  # show real names
    col_series = df[feat].dropna()

    if pd.api.types.is_numeric_dtype(col_series):
        default = float(round(col_series.mean(), 2))
        val = st.number_input(label, value=default, step=1.0, format="%.2f", key=f"inp_{i}")
    else:
        default = str(col_series.mode().iloc[0]) if not col_series.mode().empty else ""
        val = st.text_input(label, value=default, key=f"inp_{i}")

    user_inputs[feat] = val

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Predict Button ----------------
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
predict_clicked = st.button("Predict Score")

# ---------------- Prediction Logic ----------------
if predict_clicked:
    X = []
    bad_conversion = False

    for feat in feature_cols:
        v = user_inputs[feat]
        if pd.api.types.is_numeric_dtype(df[feat]):
            try:
                X.append(float(v))
            except Exception:
                bad_conversion = True
                break
        else:
            X.append(v)

    if bad_conversion:
        st.error("Please enter valid numeric values for numeric inputs.")
    else:
        if expected_features is not None and expected_features != len(X):
            st.error(
                f"Feature mismatch: model expects {expected_features} features but you provided {len(X)}.\n\n"
                "Fix: retrain the model with these columns, or provide the missing engineered features."
            )
        else:
            # progress animation
            prog = st.progress(0)
            for pct in range(0, 101, 20):
                prog.progress(pct)
                time.sleep(0.04)
            prog.empty()

            try:
                pred = model.predict([X])[0]
                st.markdown(f"<div class='result'>🏆 Predicted Score: {pred}</div>", unsafe_allow_html=True)

                # interpret
                try:
                    sc = float(pred)
                except:
                    sc = None

                if sc is not None:
                    if sc >= 85:
                        st.success("Outstanding — excellent result! 🎉")
                        st.balloons()
                    elif sc >= 70:
                        st.success("Very good performance! ✨")
                    elif sc >= 50:
                        st.info("Fair — opportunity to improve.")
                    else:
                        st.warning("Needs improvement — consider more practice.")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

# ---------------- Footer ----------------
st.markdown("<div class='footer'>Smart Student Analyzer — Business Edition · Made for professional use</div>", unsafe_allow_html=True)
