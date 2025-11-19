import streamlit as st
import pandas as pd
import pickle
import os
import time

# ---------------- Page config (mobile-first) ----------------
st.set_page_config(
    page_title="Mobile Student Predictor",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------- Mobile-friendly CSS ----------------
st.markdown(
    """
    <style>
    /* Make the app feel like a mobile UI */
    .stApp {
        background: linear-gradient(180deg,#e6f7ff 0%,#ffffff 100%);
        font-family: "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        padding: 8px 10px;
    }

    /* Header */
    .header {
        background: linear-gradient(90deg,#06b6d4,#3b82f6);
        color: white;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 14px;
    }
    .header h1 {
        margin: 0;
        font-size: 20px;
        letter-spacing: 0.4px;
    }
    .header p {
        margin: 6px 0 0;
        font-size: 12px;
        opacity: 0.95;
    }

    /* Input card */
    .input-card {
        background: rgba(255,255,255,0.85);
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(20,20,40,0.05);
        margin-bottom: 12px;
    }

    /* Large labels and inputs for touch */
    label {
        font-weight: 700 !important;
        font-size: 16px !important;
        margin-bottom: 6px !important;
        display: block;
    }
    .stNumberInput>div>div>input, .stTextInput>div>div>input {
        height:44px;
        padding: 10px 12px;
        font-size: 16px;
        border-radius: 10px;
        border: 1px solid #e6eef8;
    }

    /* Big Predict button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg,#06b6d4,#7c3aed);
        color: white;
        font-weight: 800;
        padding: 14px 18px;
        border-radius: 12px;
        border: none;
        font-size: 16px;
        box-shadow: 0 10px 30px rgba(124,58,237,0.18);
    }

    /* Result area */
    .result {
        background: linear-gradient(90deg,#10b981,#34d399);
        color: white;
        padding: 12px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 18px;
        text-align: center;
    }

    /* Make everything stacked vertically on small screens */
    @media (max-width: 600px) {
        .stApp {
            padding: 6px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Header ----------------
st.markdown(
    """
    <div class="header">
      <h1>📱 Student Performance (Mobile)</h1>
      <p>Tap values, then Predict — feature names are shown below</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load CSV and model ----------------
CSV_PATH = "student_scores (1).csv"
MODEL_PATH = "student_score.pkl"

if not os.path.exists(CSV_PATH):
    st.error("Dataset CSV not found. Please upload `student_scores (1).csv` to the app folder.")
    st.stop()

if not os.path.exists(MODEL_PATH):
    st.error("Model file `student_score.pkl` not found. Please upload it to the app folder.")
    st.stop()

# read CSV (used only to infer feature columns and defaults)
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

# detect target (score) and feature columns
cols_lower = [c.lower() for c in df.columns]
target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
feature_cols = [c for c in df.columns if c != target_col]

if len(feature_cols) == 0:
    st.error("No input features detected in CSV. Ensure the CSV has at least one feature column.")
    st.stop()

# load model
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load model: {e}")
    st.stop()

expected_features = getattr(model, "n_features_in_", None)

# ---------------- Input area (vertical) ----------------
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.subheader("Enter inputs (labels shown)")

# Show all real feature names as labels (no hiding)
user_inputs = {}
for i, feat in enumerate(feature_cols, start=1):
    # human-friendly label: replace underscores
    label = f"{i}. {feat.replace('_', ' ')}"
    col_series = df[feat].dropna()
    if pd.api.types.is_numeric_dtype(col_series):
        default = float(round(col_series.mean(), 2))
        val = st.number_input(label, value=default, step=1.0, format="%.2f", key=f"inp_{i}")
    else:
        default = str(col_series.mode().iloc[0]) if not col_series.mode().empty else ""
        val = st.text_input(label, value=default, key=f"inp_{i}")
    user_inputs[feat] = val

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Predict button ----------------
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
predict_clicked = st.button("🚀 Predict Score")

# ---------------- Prediction logic & result ----------------
if predict_clicked:
    # Build feature vector in the same order as feature_cols
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
                f"Feature count mismatch: model expects {expected_features} features but you provided {len(X)}.\n\n"
                "Fix: retrain the model with these columns or supply the missing features."
            )
        else:
            # small animation/progress
            prog = st.progress(0)
            for pct in range(0, 101, 20):
                prog.progress(pct)
                time.sleep(0.04)
            prog.empty()

            # predict
            try:
                pred = model.predict([X])[0]
                st.markdown(f"<div class='result'>🏆 Predicted Score: {pred}</div>", unsafe_allow_html=True)

                # extra feedback
                try:
                    sc = float(pred)
                except:
                    sc = None

                if sc is not None:
                    if sc >= 85:
                        st.success("Excellent — keep it up! 🎉")
                        st.balloons()
                    elif sc >= 70:
                        st.success("Great performance! ✨")
                    elif sc >= 50:
                        st.info("Fair — room to improve.")
                    else:
                        st.warning("Needs improvement — encourage more study time.")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("<div style='font-size:12px; color:#555;'>Note: Feature names shown above are read directly from the CSV (no hiding). Ensure the model was trained on the same features in the same order.</div>", unsafe_allow_html=True)
