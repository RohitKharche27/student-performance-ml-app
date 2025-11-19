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
    /* Page */
    .main {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
        font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    /* Card */
    .card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(20,20,40,0.06);
        margin-bottom: 20px;
    }
    /* Title */
    h1, .stMarkdown h1 {
        color: #0b4f6c;
    }
    /* Button */
    .stButton>button {
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
    }
    /* Small text */
    .small {
        font-size: 0.9rem;
        color: #444;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Title / description ---------------------------------------------------
st.title("📚 Student Performance Predictor")
st.write("Use the inputs below (auto-detected from the dataset) to predict student Score using the trained model.")
st.markdown("---")

# --- Load dataset (to infer column names / defaults) -----------------------
csv_path = "student_scores (1).csv"
if not os.path.exists(csv_path):
    st.error(f"Dataset not found at `{csv_path}`. Please upload the CSV to the same folder.")
    st.stop()

try:
    df = pd.read_csv(csv_path)
except Exception as e:
    st.error(f"Could not read CSV file: {e}")
    st.stop()

# infer features: all columns except a column named like 'score' (case-insensitive)
target_col = None
cols_lower = [c.lower() for c in df.columns]
if "score" in cols_lower:
    target_col = df.columns[cols_lower.index("score")]

feature_cols = [c for c in df.columns if c != target_col]
if len(feature_cols) == 0:
    st.error("No feature columns found in the CSV (all columns look like the target). Please provide a dataset with at least one input feature.")
    st.stop()

# show dataset summary
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Dataset preview & summary")
    st.write(f"Detected features: **{', '.join(feature_cols)}**" + (f" — target: **{target_col}**" if target_col else ""))
    st.dataframe(df.head(8))
    st.markdown("</div>", unsafe_allow_html=True)

# --- Load model ------------------------------------------------------------
model_path = "student_score.pkl"
if not os.path.exists(model_path):
    st.error(f"Model file not found at `{model_path}`. Please place `student_score.pkl` in the app folder.")
    st.stop()

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# try to get required number of features (if sklearn model)
expected_features = None
if hasattr(model, "n_features_in_"):
    expected_features = int(getattr(model, "n_features_in_"))

# --- User Inputs (dynamically built from dataset features) -----------------
st.markdown("## Enter student details")
input_values = []
cols = st.columns(len(feature_cols))

for i, feat in enumerate(feature_cols):
    # compute a helpful default (mean) and bounds from dataset
    col_data = df[feat].dropna()
    try:
        default = float(round(col_data.mean(), 2))
    except Exception:
        default = 0.0
    # determine min/max for nicer UI if numeric
    if pd.api.types.is_numeric_dtype(col_data):
        min_val = float(col_data.min())
        max_val = float(col_data.max())
        step = (max_val - min_val) / 100 if max_val != min_val else 1.0
        with cols[i]:
            val = st.number_input(feat, value=default, min_value=min_val - abs(min_val)*0.5, max_value=max_val + abs(max_val)*0.5, step=step, format="%.2f")
    else:
        # treat as text input if non-numeric
        with cols[i]:
            val = st.text_input(feat, value=str(default))
    input_values.append(val)

# --- Predict button -------------------------------------------------------
if st.button("Predict"):
    # convert inputs to numeric array where possible
    X = []
    for v in input_values:
        try:
            X.append(float(v))
        except Exception:
            # if some features are non-numeric, keep as-is (model may accept)
            X.append(v)
    # validation if model expects a certain number of features
    if expected_features is not None:
        if expected_features != len(X):
            st.error(
                f"The loaded model expects {expected_features} features, but you're providing {len(X)}.\n\n"
                "Possible fixes:\n"
                " - Ensure the model was trained on the same feature set as this CSV (feature order & count).\n"
                " - If the model expects additional engineered features, either retrain the model or provide those inputs.\n"
                " - As a temporary workaround, you can modify the code to append default values to match the expected feature count."
            )
        else:
            try:
                pred = model.predict([X])
                st.success(f"Predicted Score: **{pred[0]}**")
            except Exception as e:
                st.error(f"Prediction failed: {e}")
    else:
        # model doesn't expose n_features_in_ — try to predict and handle exceptions
        try:
            pred = model.predict([X])
            st.success(f"Predicted Score: **{pred[0]}**")
        except Exception as e:
            st.error(
                "Prediction failed. The model raised an error when predicting with the provided inputs.\n\n"
                f"Error: {e}\n\n"
                "If you see a feature count mismatch (e.g. `X has 3 features but model expects 4`), you need to provide the same features the model was trained on."
            )

# --- Footer / tips --------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div class="small">
    Tip: If prediction fails because of mismatched feature count, open the training script or re-train the model using exactly these input columns:
    <ul>
      <li><b>Hours_Studied</b></li>
      <li><b>Attendance</b></li>
      <li><b>Assignments_Submitted</b></li>
    </ul>
    Or modify the app to include the missing engineered feature(s).</div>
    """,
    unsafe_allow_html=True,
)
