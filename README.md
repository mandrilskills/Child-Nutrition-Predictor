# 🧒 Child Nutrition Risk Predictor

A **Machine Learning web app** built using **Decision Tree Classification** to predict the **nutritional status of children** based on simple lifestyle and physical attributes.

🔗 **Live App**: [https://child-nutrition-predictor.streamlit.app/](https://child-nutrition-predictor.streamlit.app/)

---

## 📌 Problem Statement

This project aims to **identify children at risk of malnutrition** by analyzing key indicators such as:

- Age
- Gender
- Weight
- Height
- Diet and Hygiene Practices

The model predicts whether a child is:
- ✅ **Healthy**
- ⚠️ **At Risk**
- ❌ **Malnourished**

---

## 🛠️ Tech Stack

- **Python 3**
- **Pandas**, **Scikit-learn** for data preprocessing & modeling
- **Decision Tree Classifier** (sklearn)
- **Streamlit** for the web interface
- **CSV-based dataset** (synthetically generated)

---

## 📂 Dataset

The dataset includes the following fields:

| Feature | Description |
|--------|-------------|
| Age | Age of the child (in years) |
| Gender | Male / Female |
| Weight | Weight in kg |
| Height | Height in cm |
| Has_regular_meals | Yes / No |
| Eats_fruits_vegetables | Yes / No |
| Access_clean_water | Yes / No |
| Nutrition_Status | Healthy / At Risk / Malnourished (label) |

---

## 🚀 Features

- 🔍 **Interactive Web UI** – Easy data input for prediction
- 🌳 **Decision Tree Model** – Transparent and interpretable
- 📈 **High Accuracy** – Trained on realistic mock data
- ✅ **No login or sign-up required**

---

## ▶️ How to Use

1. Visit the Streamlit app: [**Child Nutrition Predictor**](https://child-nutrition-predictor.streamlit.app/)
2. Enter the required inputs:
   - Age
   - Gender
   - Weight
   - Height
   - Meal and hygiene info
3. Click **Predict** to see the result.

---

## 🧪 Model Training

- Label Encoding for categorical features
- Train-test split: 80-20
- Fitted with `DecisionTreeClassifier` from `sklearn`

---

## 🤝 Contributing

Pull requests are welcome! Feel free to fork the repo and submit a PR.

---


