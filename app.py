import streamlit as st
import pandas as pd
import pickle
import os
import time
import numpy as np

# ---------------- Page config ----------------
st.set_page_config(
    page_title="✨ Student Performance Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Custom CSS (attractive) ----------------
st.markdown(
    """
    <style>
    /* Background & fonts */
    .stApp {
        background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
        font-family: "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Header card */
    .header-card {
        background: linear-gradient(90deg,#0ea5e9 0%,#7dd3fc 100%);
        color: white;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 30px rgba(13, 71, 161, 0.12);
        margin-bottom: 18px;
    }
    .header-title {
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        padding: 0;
    }
    .header-sub {
        opacity: 0.95;
        margin-top: 6px;
        font-size: 14px;
    }

    /* Card */
    .card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(20,20,40,0.06);
        margin-bottom: 20px;
    }

    /* Big Predict button */
    .stButton>button.predict-btn {
        background: linear-gradient(90deg,#06b6d4,#7c3aed);
        color: white;
        font-weight: 700;
        padding: 12px 20px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 20px rgba(124,58,237,0.18);
    }
    .stButton>button.predict-btn:active { transform: translateY(1px); }

    /* Result badge */
    .result-badge {
        background: linear-gradient(90deg,#10b981,#34d399);
        color: white;
        padding: 10px 14px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 18px;
        display: inline-block;
    }

    /* Inputs spacing */
    .stNumberInput>div>label {
        font-weight: 600;
    }

    /* small muted text */
    .muted { color: #586069; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Header ----------------
st.markdown(
    f"""
    <div class="header-card">
      <div style="display:flex; align-items:center; gap:12px;">
        <div style="font-size:36px;">🎓</div>
        <div>
          <div class="header-title">Student Performance Studio</div>
          <div class="header-sub">Beautiful UI • Quick presets • Smart input detection</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.write("Use presets or tweak inputs manually.")
    csv_path = "student_scores (1).csv"
    if not os.path.exists(csv_path):
        st.error("Dataset not found in app folder.")
        st.stop()

    df = pd.read_csv(csv_path)
    # detect target
    cols_lower = [c.lower() for c in df.columns]
    target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
    feature_cols = [c for c in df.columns if c != target_col]

    st.markdown(f"**Detected features:** {', '.join(feature_cols)}")
    st.markdown("---")

    # Preset selector: show 3 sample rows if available
    st.markdown("### 🎯 Quick presets")
    preset_names = ["— select preset —"]
    sample_rows = []
    if len(df) > 0:
        # pick up to 6 distinct rows as presets
        sample_rows = df.head(6).to_dict(orient="records")
        for i, r in enumerate(sample_rows):
            preset_names.append(f"Preset {i+1}: {', '.join([str(r[c]) for c in feature_cols])}")
    preset = st.selectbox("Choose a preset", preset_names)

    st.markdown("---")
    st.markdown("### 🎨 Style")
    theme = st.radio("Theme accent", ["Cool blue", "Purple pop", "Emerald"], index=0)
    st.markdown("---")
    st.markdown("<div class='muted'>Made with ❤ — change presets to autofill inputs</div>", unsafe_allow_html=True)

# ---------------- Load Model ----------------
model_path = "student_score.pkl"
if not os.path.exists(model_path):
    st.error("Model file `student_score.pkl` not found in app folder.")
    st.stop()

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Failed to load model: {e}")
    st.stop()

expected_features = getattr(model, "n_features_in_", None)

# ---------------- Main input area ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("## ✨ Enter Student Details")
st.markdown("<div class='muted'>Fill the inputs — or pick a preset from the sidebar to autofill.</div>", unsafe_allow_html=True)

# layout: two columns if many features, else single row
cols_layout = 2 if len(feature_cols) > 2 else len(feature_cols)
input_cols = st.columns(cols_layout)

# compute defaults from data
defaults = {}
for c in feature_cols:
    coldata = df[c].dropna()
    if pd.api.types.is_numeric_dtype(coldata):
        defaults[c] = float(round(coldata.mean(), 2))
    else:
        defaults[c] = str(coldata.mode().iloc[0]) if not coldata.mode().empty else ""

# fill from preset if chosen
preset_values = None
if preset != "— select preset —":
    # find which sample row matched index of chosen preset
    idx = preset_names.index(preset) - 1
    if 0 <= idx < len(sample_rows):
        preset_values = sample_rows[idx]

# Create inputs
user_inputs = {}
for i, feat in enumerate(feature_cols):
    col_index = i % cols_layout
    with input_cols[col_index]:
        label = f"🔹 {feat.replace('_', ' ')}"
        coldata = df[feat].dropna()
        if pd.api.types.is_numeric_dtype(coldata):
            min_val = float(coldata.min())
            max_val = float(coldata.max())
            step = (max_val - min_val) / 100 if max_val != min_val else 1.0
            default_val = float(preset_values[feat]) if preset_values else defaults[feat]
            val = st.number_input(label, value=default_val, min_value=min_val - abs(min_val)*0.5, max_value=max_val + abs(max_val)*0.5, step=step, format="%.2f")
        else:
            default_val = str(preset_values[feat]) if preset_values else defaults[feat]
            val = st.text_input(label, value=default_val)
        user_inputs[feat] = val

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Action / Predict UI ----------------
# create a centered big predict button by using columns
left_col, mid_col, right_col = st.columns([1, 2, 1])
with mid_col:
    # use markdown to place button with custom class
    predict_clicked = st.button("🚀 Predict Score", key="predict_btn", help="Click to predict", on_click=None)

# show small info line
st.write("")  # spacing

# ---------------- Prediction Logic ----------------
if predict_clicked:
    # Prepare feature vector in feature_cols order
    X = []
    for c in feature_cols:
        v = user_inputs[c]
        try:
            X.append(float(v))
        except:
            X.append(v)

    # Feature count check
    if expected_features is not None and expected_features != len(X):
        st.error(
            f"⚠️ Model expects {expected_features} features but you provided {len(X)}.\n\n"
            "Please ensure the CSV and model were trained on the same feature set (same order & count)."
        )
    else:
        # show progress bar while "thinking"
        progress = st.progress(0)
        status_text = st.empty()
        for pct in range(0, 101, 10):
            progress.progress(pct)
            status_text.markdown(f"Processing... **{pct}%**")
            time.sleep(0.04)
        status_text.empty()

        # attempt prediction
        try:
            pred = model.predict([X])
            score = pred[0]
            # nice result display
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:14px;">
                  <div class="result-badge">🏆 {score}</div>
                  <div>
                    <div style="font-weight:700; font-size:18px;">Predicted Score</div>
                    <div class="muted">Based on inputs you provided</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # celebration for high scores
            try:
                numeric_score = float(score)
            except:
                numeric_score = None

            if numeric_score is not None:
                # small interpretation
                if numeric_score >= 85:
                    st.success("Excellent performance! 🎉")
                    st.balloons()
                elif numeric_score >= 70:
                    st.success("Great job! Keep it up! ✨")
                elif numeric_score >= 50:
                    st.info("Fair — there's room to improve. 🚀")
                else:
                    st.warning("Needs improvement — provide more study hours and assignments. 💪")

                # show a simple bar representing score
                st.progress(min(max(int(numeric_score), 0), 100))

            # show suggestion tips (basic heuristic)
            st.markdown("### 🔎 Suggestions (quick)")
            suggs = []
            # simple rule-based tips using detected column names
            def contains(k): return any(k in c.lower() for c in feature_cols)

            if contains("hour") or contains("study"):
                suggs.append("Increase study hours gradually and maintain a study schedule.")
            if contains("attendance"):
                suggs.append("Improve attendance — consistent presence helps retention.")
            if contains("assign"):
                suggs.append("Submit assignments on time and review feedback.")
            if suggs:
                for s in suggs:
                    st.markdown(f"- {s}")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("<div class='muted'>Tip: If the model complains about feature count, retrain it using the same features shown in the sidebar.</div>", unsafe_allow_html=True)
