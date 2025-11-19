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

# ---------------- Helper: CSS builder ----------------
def build_css(theme_name: str, size_name: str) -> str:
    # size settings
    if size_name == "Compact":
        base_font = "14px"
        label_size = "13px"
        input_height = "38px"
        header_size = "18px"
    elif size_name == "Large":
        base_font = "18px"
        label_size = "18px"
        input_height = "54px"
        header_size = "26px"
    else:  # Normal
        base_font = "16px"
        label_size = "15px"
        input_height = "46px"
        header_size = "22px"

    # theme-specific colors
    if theme_name == "Light Corporate":
        bg = "linear-gradient(180deg,#f6fbff 0%, #ffffff 100%)"
        accent_start = "#0b63a6"
        accent_end = "#0f9cf0"
        text_color = "#0b2440"
        glass_bg = "rgba(255,255,255,0.9)"
        input_bg = "rgba(255,255,255,1)"
        input_border = "rgba(10,50,80,0.08)"
        result_bg = "linear-gradient(90deg,#e6f1ff,#dbeeff)"
        result_text = "#05204a"
    elif theme_name == "Dark Pro":
        bg = "linear-gradient(180deg,#070816 0%, #0b2b3a 100%)"
        accent_start = "#00b4d8"
        accent_end = "#0077b6"
        text_color = "#e6f0fb"
        glass_bg = "rgba(255,255,255,0.03)"
        input_bg = "rgba(255,255,255,0.02)"
        input_border = "rgba(255,255,255,0.06)"
        result_bg = "linear-gradient(90deg,#0b2638,#071827)"
        result_text = "#e6f0fb"
    else:  # Business Gradient (default)
        bg = "linear-gradient(180deg, #0f172a 0%, #0b4f6c 45%, #0b63a6 100%)"
        accent_start = "#0b63a6"
        accent_end = "#0f9cf0"
        text_color = "#e6f0fb"
        glass_bg = "rgba(255,255,255,0.04)"
        input_bg = "rgba(255,255,255,0.10)"
        input_border = "rgba(255,255,255,0.18)"
        result_bg = "linear-gradient(90deg,#0ea5a0,#06b6d4)"
        result_text = "#ffffff"

    css = f"""
    <style>
    .stApp {{
        background: {bg};
        color: {text_color} !important;
        font-family: "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        padding: 14px;
        font-size: {base_font};
    }}
    /* Top navbar simulated */
    .nav {{
        display:flex;
        gap:8px;
        justify-content:center;
        margin-bottom:12px;
    }}
    .nav button {{
        background: transparent;
        color: {text_color};
        border: 1px solid rgba(255,255,255,0.06);
        padding:8px 14px;
        border-radius: 10px;
        font-weight:700;
        cursor:pointer;
    }}
    .nav button.active {{
        background: linear-gradient(90deg,{accent_start},{accent_end});
        color: white;
        box-shadow: 0 8px 24px rgba(11,99,166,0.18);
    }}

    .header {{
        background: {glass_bg};
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        text-align:center;
    }}
    .header h1 {{ margin: 0; font-size: {header_size}; font-weight:800; }}
    .header p {{ margin: 6px 0 0; opacity:0.95; }}

    .input-card {{
        background: {glass_bg};
        padding: 14px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        margin-bottom: 12px;
    }}
    label {{ font-weight:700 !important; font-size:{label_size} !important; color:inherit !important; display:block; margin-bottom:6px; }}

    .stNumberInput>div>div>input,
    .stTextInput>div>div>input {{
        height:{input_height};
        padding: 10px 12px;
        font-size: {base_font};
        border-radius: 8px;
        border: 1px solid {input_border};
        background: {input_bg};
        color: inherit !important;
    }}
    .stNumberInput>div>div>input:focus,
    .stTextInput>div>div>input:focus {{
        outline: none;
        box-shadow: 0 6px 18px rgba(11,99,166,0.12);
    }}

    .stButton>button {{
        width: 100%;
        background: linear-gradient(90deg,{accent_start},{accent_end});
        color: white;
        font-weight:800;
        padding: 12px 16px;
        border-radius: 10px;
        border: none;
        font-size: {base_font};
        box-shadow:0 8px 24px rgba(11,99,166,0.18);
    }}

    .result-dark {{
        background: rgba(0,0,0,0.55);
        backdrop-filter: blur(6px);
        padding: 14px;
        border-radius: 12px;
        font-size: 18px;
        color: {result_text};
        font-weight: 900;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.06);
        margin-top: 10px;
    }}

    .footer {{ text-align:center; margin-top:12px; color: rgba(255,255,255,0.85); font-size:13px; }}
    .small-muted {{ font-size:12px; opacity:0.9; text-align:center; margin-top:8px; }}
    </style>
    """
    return css

# ---------------- Top controls: theme & size ----------------
# Put theme & size selectors in a compact horizontal layout
cols = st.columns([1, 2, 2, 1])
with cols[0]:
    st.write("")  # spacer
with cols[1]:
    theme_sel = st.selectbox("Theme", ["Business Gradient", "Light Corporate", "Dark Pro"], index=["Business Gradient","Light Corporate","Dark Pro"].index(st.session_state.theme))
with cols[2]:
    size_sel = st.selectbox("Size", ["Compact", "Normal", "Large"], index=["Compact","Normal","Large"].index(st.session_state.size))
with cols[3]:
    # simple nav sim: show current page
    st.write(f" ")  # placeholder

# Apply selection to session state and CSS
if theme_sel != st.session_state.theme:
    st.session_state.theme = theme_sel
if size_sel != st.session_state.size:
    st.session_state.size = size_sel

st.markdown(build_css(st.session_state.theme, st.session_state.size), unsafe_allow_html=True)

# ---------------- Navbar (Home / About / Contact) ----------------
def set_page(p):
    st.session_state.page = p

nav_cols = st.columns([1,1,1])
pages = ["Home", "About", "Contact"]
for i, p in enumerate(pages):
    if nav_cols[i].button(p, key=f"nav_{p}"):
        set_page(p)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ---------------- Content: Home / About / Contact ----------------
if st.session_state.page == "Home":
    # Header
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown("<h1>📊 Smart Student Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p>Professional clean mobile interface — enter values and tap Predict</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Load CSV & Model (same checks as before)
    CSV_PATH = "student_scores (1).csv"
    MODEL_PATH = "student_score.pkl"

    if not os.path.exists(CSV_PATH):
        st.error("Dataset CSV not found. Upload `student_scores (1).csv` to the app folder.")
        st.stop()
    if not os.path.exists(MODEL_PATH):
        st.error("Model file `student_score.pkl` not found in app folder.")
        st.stop()

    # read CSV
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()

    cols_lower = [c.lower() for c in df.columns]
    target_col = df.columns[cols_lower.index("score")] if "score" in cols_lower else None
    feature_cols = [c for c in df.columns if c != target_col]

    if len(feature_cols) == 0:
        st.error("No input features detected in CSV. Ensure CSV has input columns.")
        st.stop()

    # load model
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        st.stop()

    expected_features = getattr(model, "n_features_in_", None)

    # Input card
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("Enter input values")
    user_inputs = {}
    for i, feat in enumerate(feature_cols, start=1):
        label = f"{i}. {feat.replace('_',' ')}"  # show real names
        col_series = df[feat].dropna()
        if pd.api.types.is_numeric_dtype(col_series):
            default = float(round(col_series.mean(), 2))
            user_inputs[feat] = st.number_input(label, value=default, step=1.0, format="%.2f", key=f"inp_{i}")
        else:
            default = str(col_series.mode().iloc[0]) if not col_series.mode().empty else ""
            user_inputs[feat] = st.text_input(label, value=default, key=f"inp_{i}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Predict button
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    predict_clicked = st.button("Predict Score")

    if predict_clicked:
        X = []
        conversion_error = False
        for feat in feature_cols:
            val = user_inputs[feat]
            try:
                X.append(float(val))
            except:
                conversion_error = True
                break
        if conversion_error:
            st.error("Please enter valid numeric values.")
        else:
            if expected_features and expected_features != len(X):
                st.error(f"Model expects {expected_features} features but got {len(X)}.")
            else:
                prog = st.progress(0)
                for pct in range(0, 101, 25):
                    prog.progress(pct)
                    time.sleep(0.04)
                prog.empty()
                pred = model.predict([X])[0]
                st.markdown(f"<div class='result-dark'>🏆 Predicted Score: {pred}</div>", unsafe_allow_html=True)
                # Feedback
                try:
                    sc = float(pred)
                    if sc >= 85:
                        st.success("Excellent result!")
                        st.balloons()
                    elif sc >= 70:
                        st.success("Very good performance")
                    elif sc >= 50:
                        st.info("Fair — opportunity to improve.")
                    else:
                        st.warning("Needs improvement.")
                except:
                    pass

    st.markdown("<div class='small-muted'>Smart Student Analyzer</div>", unsafe_allow_html=True)

elif st.session_state.page == "About":
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown("<h1>About</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        """
        **Smart Student Analyzer** — professional prediction UI built with Streamlit.
        - Mobile-first, professional gradient themes.
        - Auto-detects features from your CSV and uses your pickled model.
        - Theme & size controls for different devices and tastes.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown(
        """
        1. Place `student_scores (1).csv` and `student_score.pkl` in the same folder as this app.  
        2. Enter the feature values (labels are read from CSV).  
        3. Tap **Predict Score** — the app sends the values to your loaded scikit-learn model and displays result.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("<div class='small-muted'>Made for smooth, professional demos and quick deployments.</div>", unsafe_allow_html=True)

else:  # Contact
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown("<h1>Contact</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        """
        Need help integrating or customizing this app?  
        - **Email:** your-email@example.com  
        - **GitHub:** github.com/your-repo  
        - **Phone:** +1-234-567-890
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("Or drop a message below:")
    name = st.text_input("Your name")
    email = st.text_input("Email")
    message = st.text_area("Message")
    if st.button("Send Message"):
        # For demo only — no real sending. Replace with actual sending code if needed.
        st.success("Thanks — your message has been recorded (demo).")
        st.write("We would contact you at:", email)

# ---------------- Footer ----------------
st.markdown("<div class='footer'>Smart Student Analyzer</div>", unsafe_allow_html=True)
