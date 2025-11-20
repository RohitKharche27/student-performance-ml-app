# app.py
import streamlit as st
import pandas as pd
import pickle
import os
import time

# ---------------- Session state defaults ----------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "theme" not in st.session_state:
    st.session_state.theme = "Business Gradient"
if "size" not in st.session_state:
    st.session_state.size = "Normal"

# ---------------- Helper: CSS builder (compact, unique UI) ----------------
def build_css(theme_name: str, size_name: str) -> str:
    # compact size settings
    if size_name == "Compact":
        base_font = "14px"
        label_size = "13px"
        input_height = "40px"
        input_font = "14px"
        header_size = "18px"
        card_padding = "10px"
    elif size_name == "Large":
        base_font = "18px"
        label_size = "20px"
        input_height = "64px"
        input_font = "20px"
        header_size = "28px"
        card_padding = "22px"
    else:  # Normal
        base_font = "16px"
        label_size = "16px"
        input_height = "52px"
        input_font = "16px"
        header_size = "22px"
        card_padding = "16px"

    # theme-specific colors (kept professional)
    if theme_name == "Light Corporate":
        bg = "linear-gradient(180deg,#f6fbff 0%, #ffffff 100%)"
        accent_start = "#0b63a6"
        accent_end = "#0f9cf0"
        text_color = "#0b2440"
        glass_bg = "rgba(255,255,255,0.95)"
        input_bg = "rgba(255,255,255,1)"
        input_border = "rgba(10,50,80,0.08)"
        result_text = "#05204a"
    elif theme_name == "Dark Pro":
        bg = "linear-gradient(180deg,#05060a 0%, #071625 100%)"
        accent_start = "#00b4d8"
        accent_end = "#0077b6"
        text_color = "#e6f0fb"
        glass_bg = "rgba(255,255,255,0.02)"
        input_bg = "rgba(255,255,255,0.02)"
        input_border = "rgba(255,255,255,0.06)"
        result_text = "#e6f0fb"
    else:  # Business Gradient (default)
        bg = "linear-gradient(180deg, #071028 0%, #0b3b57 45%, #0b63a6 100%)"
        accent_start = "#0b63a6"
        accent_end = "#0f9cf0"
        text_color = "#e6f0fb"
        glass_bg = "rgba(255,255,255,0.03)"
        input_bg = "rgba(255,255,255,0.06)"
        input_border = "rgba(255,255,255,0.12)"
        result_text = "#ffffff"

    css = f"""
    <style>
    :root{{ --accent-start:{accent_start}; --accent-end:{accent_end}; --text-color:{text_color}; }}

    .stApp {{
        background: {bg};
        color: {text_color} !important;
        font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        padding: 10px 12px;
        font-size: {base_font};
    }}

    /* --- Top compact header (single line title) --- */
    .top-header {{
        display:flex;
        align-items:center;
        gap:10px;
        padding:6px 8px;
        border-radius:10px;
        margin-bottom:6px;
        background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border:1px solid rgba(255,255,255,0.03);
    }}
    .app-icon {{
        width:44px; height:44px; border-radius:10px;
        background:linear-gradient(135deg,var(--accent-start),var(--accent-end));
        display:flex; align-items:center; justify-content:center;
        font-size:20px; color:white; box-shadow:0 6px 18px rgba(11,99,166,0.18);
    }}
    .app-title {{ font-weight:800; font-size:{header_size}; margin:0; padding:0; }}
    .app-sub {{ font-size:12px; opacity:0.9; margin:0; color: rgba(255,255,255,0.85); }}

    /* --- Main card (unique UI, compact) --- */
    .input-card {{
        background: rgba(255,255,255,0.035);
        border-radius: 14px;
        padding: {card_padding};
        border: 1px solid rgba(255,255,255,0.04);
        box-shadow: 0 8px 30px rgba(2,6,23,0.45);
        margin-bottom: 8px;
    }}

    /* label with small icon bubble */
    .input-row {{
        display:flex;
        flex-direction:column;
        gap:4px;
        margin-bottom:6px;
    }}
    .label-wrap {{
        display:flex; align-items:center; gap:8px;
    }}
    .label-icon {{
        width:28px; height:28px; border-radius:8px;
        background: linear-gradient(135deg,var(--accent-start),var(--accent-end));
        display:inline-flex; align-items:center; justify-content:center; color:white; font-size:14px;
        box-shadow: 0 6px 14px rgba(11,99,166,0.14);
    }}
    .label-text {{ font-weight:700; font-size:{label_size}; margin:0; color: var(--text-color); }}

    /* input control styling (compact, tighter spacing) */
    .stNumberInput>div>div>input,
    .stTextInput>div>div>input {{
        height: {input_height} !important;
        padding: 6px 12px !important;
        font-size: {input_font} !important;
        border-radius: 10px !important;
        border: 2px solid {input_border} !important;
        background: {input_bg} !important;
        color: {text_color} !important;
        transition: box-shadow .12s ease, border-color .12s ease;
    }}
    .stNumberInput>div>div>input:focus,
    .stTextInput>div>div>input:focus {{
        outline:none !important;
        box-shadow: 0 8px 22px rgba(11,99,166,0.18) !important;
        border-color: rgba(79,172,254,0.9) !important;
    }}

    /* reduce extra vertical gaps Streamlit adds around controls */
    .stNumberInput, .stTextInput {{
        margin-bottom: 2px !important;
        padding-bottom: 0 !important;
    }}

    /* predict button */
    .stButton>button {{
        width:100%;
        padding:10px 12px;
        border-radius:12px;
        background: linear-gradient(90deg,var(--accent-start),var(--accent-end));
        color:white;
        font-weight:800;
        box-shadow: 0 12px 30px rgba(11,99,166,0.18);
    }}

    /* result dark box compact */
    .result-dark {{
        background: rgba(0,0,0,0.55);
        padding: 10px;
        border-radius: 12px;
        font-size: 16px;
        color: {result_text};
        font-weight:900;
        text-align:center;
        margin-top:8px;
        border: 1px solid rgba(255,255,255,0.06);
    }}

    /* small muted */
    .small-muted {{ font-size:12px; color: rgba(255,255,255,0.85); text-align:center; margin-top:6px; }}

    /* remove extra paddings Streamlit sometimes adds (attempts) */
    .css-1v3fvcr, .css-1d391kg {{ padding-top:0 !important; padding-bottom:0 !important; }}

    /* responsive tweaks */
    @media(max-width:600px) {{
        .app-title {{ font-size:18px; }}
        .app-icon {{ width:40px; height:40px; font-size:18px; }}
    }}
    </style>
    """
    return css

# ---------------- Sidebar: navigation + theme + size (kept but compact) ----------------
st.sidebar.title("Menu")
page = st.sidebar.radio("", ("Home", "About", "Contact"), index=("Home","About","Contact").index(st.session_state.page))
st.session_state.page = page

st.sidebar.markdown("---")
st.sidebar.title("Appearance")
theme = st.sidebar.selectbox("Theme", ["Business Gradient", "Light Corporate", "Dark Pro"], index=["Business Gradient","Light Corporate","Dark Pro"].index(st.session_state.theme))
size = st.sidebar.selectbox("Size", ["Compact", "Normal", "Large"], index=["Compact","Normal","Large"].index(st.session_state.size))

# update session state
if theme != st.session_state.theme:
    st.session_state.theme = theme
if size != st.session_state.size:
    st.session_state.size = size

# apply CSS
st.markdown(build_css(st.session_state.theme, st.session_state.size), unsafe_allow_html=True)

# ---------------- Utility loader ----------------
def load_model_and_df():
    CSV_PATH = "student_scores (1).csv"
    MODEL_PATH = "student_score.pkl"
    if not os.path.exists(CSV_PATH) or not os.path.exists(MODEL_PATH):
        return None, None, "missing"
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        return None, None, f"csv_err:{e}"
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        return None, None, f"model_err:{e}"
    return df, model, None

# ---------------- Page content (compact, unique UI) ----------------
if st.session_state.page == "Home":
    # compact header (single line, no sub-header)
    st.markdown(
        """
        <div class="top-header">
          <div class="app-icon">📊</div>
          <div style="display:flex;flex-direction:column;">
            <div class="app-title">Smart Student Analyzer</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, model, err = load_model_and_df()
    if err == "missing":
        st.error("Place `student_scores (1).csv` and `student_score.pkl` in the app folder.")
        st.stop()
    if err and err.startswith("csv_err"):
        st.error("Could not read CSV.")
        st.stop()
    if err and err.startswith("model_err"):
        st.error("Could not load model.")
        st.stop()

    cols_lower = [c.lower() for c in df.columns]
    target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
    feature_cols = [c for c in df.columns if c != target_col]
    if len(feature_cols) == 0:
        st.error("No input features detected in the CSV.")
        st.stop()

    expected_features = getattr(model, "n_features_in_", None)

    # unique compact input card
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    # small subtitle line (compact)
    st.markdown("<div style='margin-bottom:6px; font-weight:600; color:rgba(255,255,255,0.95)'>Enter values</div>", unsafe_allow_html=True)

    user_inputs = {}
    icons = ["📘", "🎯", "📈", "⏳", "📝", "⭐", "🧠", "📊"]

    for i, feat in enumerate(feature_cols, start=1):
        icon = icons[(i - 1) % len(icons)]
        # very tight label + input block
        st.markdown(
            f"""
            <div class="input-row">
              <div class="label-wrap" style="margin-bottom:2px">
                <div class="label-icon" style="background:linear-gradient(135deg,var(--accent-start),var(--accent-end))">{icon}</div>
                <div class="label-text">{i}. {feat.replace('_', ' ')}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_series = df[feat].dropna()
        key_name = f"inp_{i}_{feat}"

        if pd.api.types.is_numeric_dtype(col_series):
            default = float(round(col_series.mean(), 2))
            # use empty label because we show label via HTML; keep Streamlit spacing minimal
            user_inputs[feat] = st.number_input("", value=default, step=1.0, format="%.2f", key=key_name)
        else:
            default = str(col_series.mode().iloc[0]) if not col_series.mode().empty else ""
            user_inputs[feat] = st.text_input("", value=default, key=key_name)

    st.markdown("</div>", unsafe_allow_html=True)

    # compact predict button
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    predict_clicked = st.button("Predict Score")

    if predict_clicked:
        X = []
        conversion_error = False
        numeric_inputs_below_12 = False
        for feat in feature_cols:
            val = user_inputs[feat]
            if pd.api.types.is_numeric_dtype(df[feat]):
                try:
                    fv = float(val)
                    X.append(fv)
                    if fv < 12:
                        numeric_inputs_below_12 = True
                except:
                    conversion_error = True
                    break
            else:
                X.append(val)

        if conversion_error:
            st.error("Please enter valid numeric values.")
        else:
            if expected_features and expected_features != len(X):
                st.error(f"Model expects {expected_features} features but got {len(X)}.")
            else:
                prog = st.progress(0)
                for pct in range(0, 101, 20):
                    prog.progress(pct)
                    time.sleep(0.03)
                prog.empty()
                try:
                    pred = model.predict([X])[0]

                    # --- New handling to avoid showing negative results ---
                    # If the model returns a numeric negative prediction, convert to a positive decimal.
                    # Also round to 2 decimals for display.
                    display_prediction = pred
                    try:
                        sc = float(pred)
                        if sc < 0:
                            # convert negative to positive decimal (absolute value) and round
                            sc = round(abs(sc), 2)
                            display_prediction = sc
                            # show a short note to user (keeps UX clear)
                            st.info("Negative model output converted to a positive estimate.")
                        else:
                            display_prediction = round(sc, 2)
                    except:
                        # non-numeric prediction (leave as-is)
                        display_prediction = pred

                    st.markdown(f"<div class='result-dark'>🏆 Predicted Score: {display_prediction}</div>", unsafe_allow_html=True)

                    # use sc if numeric for feedback messages
                    try:
                        sc_val = float(display_prediction)
                        if sc_val >= 85:
                            st.success("Excellent result!")
                            st.balloons()
                        elif sc_val >= 70:
                            st.success("Very good performance")
                        elif sc_val >= 50:
                            st.info("Fair — opportunity to improve.")
                        else:
                            st.warning("Needs improvement.")
                    except:
                        pass

                except Exception as e:
                    st.error(f"Prediction failed: {e}")

    # compact helper text, no footer bar
    st.markdown('<div class="small-muted"></div>', unsafe_allow_html=True)

elif st.session_state.page == "About":
    # About Us: add theory + short description
    st.markdown(
        """
        <div style="padding:10px;border-radius:10px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03)">
          <h3 style="margin:0 0 8px 0">About Us</h3>
          <p style="margin:0 0 8px 0; color:rgba(255,255,255,0.9)">
            <strong>Smart Student Analyzer</strong> helps educators and students quickly estimate performance
            using simple, explainable inputs such as study hours, attendance and assignments submitted.
          </p>

          <h4 style="margin:8px 0 6px 0">Learning Theory (brief)</h4>
          <p style="margin:0 0 8px 0; color:rgba(235,245,255,0.9); line-height:1.5">
            Educational research shows that student outcomes are influenced by consistent study time,
            active participation, and timely submission of assignments. This app models the relationship between
            these measurable behaviors and likely performance to give teachers and students a fast, actionable signal.
            It complements formative assessment and is not a substitute for full grading systems.
          </p>

          <h4 style="margin:8px 0 6px 0">How to use</h4>
          <ol style="margin:0 0 8px 18px; color:rgba(235,245,255,0.9)">
            <li>Provide realistic values for Hours Studied, Attendance (%) and Assignments Submitted.</li>
            <li>Tap <em>Predict Score</em> to get an estimate and short feedback.</li>
            <li>Use results as guidance — combine with teacher judgement and assessments.</li>
          </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:  # Contact
    st.markdown(
        """
        <div style="padding:10px;border-radius:10px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.03)">
          <h3 style="margin:0 0 8px 0">Contact Us</h3>
          <p style="margin:0 0 6px 0; color:rgba(255,255,255,0.9)">
            For customization, integration or support please reach out:
          </p>
          <ul style="color:rgba(235,245,255,0.9)">
            <li><strong>Email:</strong> support@smartstudent.ai</li>
            <li><strong>Phone:</strong> +1 (555) 123-4567</li>
            <li><strong>Address:</strong> 123 Education Lane, Knowledge City</li>
          </ul>
          <hr style="border:none;border-top:1px solid rgba(255,255,255,0.03);margin:8px 0" />
          <h4 style="margin:6px 0 6px 0">Send a message</h4>
          <form>
            <!-- placeholder form (Streamlit forms need server-side handling) -->
          </form>
        </div>
        """,
        unsafe_allow_html=True,
    )

# end of file
