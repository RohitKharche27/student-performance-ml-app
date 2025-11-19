# app.py
import sys
import traceback

try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import pickle
    import os
    import matplotlib.pyplot as plt
    from sklearn.exceptions import NotFittedError
except Exception as e:
    # If an import fails display a clear error in-streamlit if streamlit is available,
    # otherwise print a helpful message to stdout (useful when running locally).
    msg = "".join(traceback.format_exception_only(type(e), e)).strip()
    try:
        import streamlit as st  # try again to show the error inside streamlit
        st.set_page_config(page_title="App Import Error", layout="centered")
        st.title("⚠️ Import / Module Error")
        st.error("A required Python module is missing or failed to import.")
        st.write("**Error:**")
        st.code(msg)
        st.write("**Traceback:**")
        st.code("".join(traceback.format_exception(type(e), e, e.__traceback__)))
        st.markdown("---")
        st.write("**Fix:** Install the missing package(s). Example:")
        st.code("pip install -r requirements.txt")
    except Exception:
        # If streamlit itself can't import, print out the message (so logs contain it)
        print("IMPORT ERROR:", msg)
        print("Full traceback:")
        traceback.print_exc()
    # stop further execution
    sys.exit(1)

# ---- normal app code below ----
st.set_page_config(page_title="Student Score Predictor", page_icon="🎓", layout="wide")

st.title("🎓 Student Score Predictor (Debug-friendly)")

st.write("This app will show a clear message if imports are missing. If you see this, imports succeeded.")

# Try to load model & dataset but keep robust error messages
MODEL_PATHS = [
    "/mnt/data/student_score.pkl",
    "student_score.pkl",
    "Student_model.pkl",
    "student_model.pkl",
]

CSV_PATHS = [
    "/mnt/data/student_scores (1).csv",
    "/mnt/data/student_scores.csv",
    "student_scores.csv",
    "student_score_data.csv",
]

def try_load_model():
    for p in MODEL_PATHS:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    model = pickle.load(f)
                return model, p, None
            except Exception as e:
                return None, p, str(e)
    return None, None, "No model file found in known locations."

def try_load_csv():
    for p in CSV_PATHS:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                return df, p, None
            except Exception as e:
                return None, p, str(e)
    return None, None, "No CSV found in known locations."

model, model_path, model_err = try_load_model()
df, csv_path, csv_err = try_load_csv()

st.subheader("Model status")
if model:
    st.success(f"Loaded model from: `{model_path}`")
else:
    st.warning("Model not loaded.")
    st.write("Tried paths:")
    st.write(MODEL_PATHS)
    st.error(f"Details: {model_err}")

st.subheader("Dataset status")
if df is not None:
    st.success(f"Loaded dataset from: `{csv_path}` — rows:{df.shape[0]} cols:{df.shape[1]}")
    st.dataframe(df.head(8))
else:
    st.warning("Dataset not loaded.")
    st.write("Tried paths:")
    st.write(CSV_PATHS)
    st.error(f"Details: {csv_err}")

st.markdown("---")
st.write("Use the sidebar to upload a model (.pkl) or dataset (.csv) if needed.")

uploaded_model = st.sidebar.file_uploader("Upload model (.pkl)", type=["pkl"])
if uploaded_model is not None:
    try:
        model = pickle.load(uploaded_model)
        st.sidebar.success("Uploaded and loaded model.")
    except Exception as e:
        st.sidebar.error(f"Failed to load uploaded model: {e}")

uploaded_csv = st.sidebar.file_uploader("Upload dataset (.csv)", type=["csv"])
if uploaded_csv is not None:
    try:
        df = pd.read_csv(uploaded_csv)
        st.sidebar.success("Uploaded and loaded CSV.")
    except Exception as e:
        st.sidebar.error(f"Failed to read uploaded CSV: {e}")

# Minimal prediction UI (only active if model exists)
if model is not None:
    st.markdown("### Predict")
    hours = st.number_input("Hours Studied", value=5.0, min_value=0.0, step=0.5)
    attendance = st.slider("Attendance (%)", 0, 100, 85)
    assignments = st.number_input("Assignments Submitted", value=8, min_value=0)
    if st.button("Predict"):
        try:
            X = np.array([[hours, attendance, assignments]])
            pred = model.predict(X)
            st.success(f"Predicted Score: {float(pred[0]):.2f}")
        except Exception as e:
            st.error("Prediction failed. See error below:")
            st.code(str(e))
            st.write("Hint: The model may expect a different number/order of features or a preprocessing pipeline.")
else:
    st.info("Upload or place a compatible `student_score.pkl` model to enable predictions.")
