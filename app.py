import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("child_nutrition_data.csv")
gender = LabelEncoder()
meals = LabelEncoder()
fruits = LabelEncoder()
water = LabelEncoder()
status = LabelEncoder()

df['Gender'] = gender.fit_transform(df['Gender'])
df['Has_Regular_Meals'] = meals.fit_transform(df['Has_Regular_Meals'])
df['Eats_Fruits_Veggies'] = fruits.fit_transform(df['Eats_Fruits_Veggies'])
df['Clean_Drinking_Water'] = water.fit_transform(df['Clean_Drinking_Water'])
df['Nutrition_Status'] = status.fit_transform(df['Nutrition_Status'])
X = df.drop('Nutrition_Status', axis=1)
y = df['Nutrition_Status']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)
st.title("Child Nutrition Status Predictor")
st.markdown("Predict whether a child is **Healthy**, **At Risk**, or **Malnourished** based on basic inputs.")
age = st.number_input("Age (in years)", min_value=0, max_value=15, value=5)
gender_input = st.selectbox("Gender", ["Male", "Female"])
weight = st.slider("Weight (in kg)", min_value=2.0, max_value=50.0, value=14.0)
height = st.slider("Height (in cm)", min_value=40.0, max_value=150.0, value=95.0)
meals_input = st.selectbox("Has Regular Meals?", ["Yes", "No"])
fruits_input = st.selectbox("Eats Fruits/Vegetables Daily?", ["Yes", "No"])
water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
if st.button("Predict Nutrition Status"):
    try:
        gender_encoded = gender.transform([gender_input])[0]
        meals_encoded = meals.transform([meals_input])[0]
        fruits_encoded = fruits.transform([fruits_input])[0]
        water_encoded = water.transform([water_input])[0]

        input_data = [[age, gender_encoded, weight, height, meals_encoded, fruits_encoded, water_encoded]]
        prediction = clf.predict(input_data)
        predicted_label = status.inverse_transform(prediction)[0]

        st.success(f"Predicted Nutrition Status: **{predicted_label}**")
    except Exception as e:
        st.error("Error in input or model prediction.")