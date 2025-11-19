import streamlit as st
import pandas as pd
import pickle

st.title("Student Performance Prediction App")
st.write("Upload student details to predict performance using the trained model.")

# Load Model
try:
    with open("student_score.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    st.error(f"Error loading model: {e}")

# Input Fields (4 features because your model expects 4)
st.subheader("Enter Student Details")
feature1 = st.number_input("Feature 1", value=0.0)
feature2 = st.number_input("Feature 2", value=0.0)
feature3 = st.number_input("Feature 3", value=0.0)
feature4 = st.number_input("Feature 4", value=0.0)

if st.button("Predict"):
    try:
        input_data = [[feature1, feature2, feature3, feature4]]
        prediction = model.predict(input_data)
        st.success(f"Predicted Output: {prediction[0]}")
    except Exception as e:
        st.error(f"Prediction Error: {e}")

# Load CSV (optional display)
st.subheader("Dataset Preview")
try:
    df = pd.read_csv("student_scores (1).csv")
    st.dataframe(df)
except:
    st.warning("Could not load student_scores (1).csv.")
