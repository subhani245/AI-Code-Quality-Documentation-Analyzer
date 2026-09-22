# AI-Code-Quality-Documentation-Analyzer
This contains the python files, which it checks the Quality of code/files, like time complexity, number of classes, import statements,also gives scores etc.. Build with effective  Dashboard..
.

🔗 **Live App:** https://ai-code-quality-documentation-analyzer.streamlit.app/

---

## 🚀 Features

* 🧾 **Code Editor** with syntax highlighting
* 🧠 **Automatic Language Detection** (Python, JavaScript, C++)
* ▶ **Python Code Execution** with output + error handling
* 🔎 **Static Code Analysis** (bad practices, debug prints, nested loops)
* ⏱ **Time Complexity Estimation**
* 🤖 **ML-Based Code Quality Prediction (0–10 score)**
* 📊 **Interactive Dashboard UI**

---

## 🧠 How It Works

```
User Code
   ↓
Language Detection
   ↓
Python Execution (if Python)
   ↓
Static Analysis
   ↓
Feature Extraction
   ↓
ML Model Prediction
   ↓
Final Code Quality Score
```

---

## 🛠 Tech Stack

* **Frontend/UI:** Streamlit, streamlit-ace
* **Backend:** Python
* **Machine Learning:** scikit-learn (RandomForestRegressor)
* **Model Handling:** joblib
* **Execution Engine:** subprocess + tempfile

---

## 📁 Project Structure

```
AI-Code-Quality-Analyzer-main/
│
├── app.py
├── analyzer.py
├── documentation_analyzer.py  
├── complexity_analyzer.py
├── feature_extractor.py
├── rules.py
├── code_runner.py
├── language_detector.py
├── train_model.py
├── model.pkl
├── requirements.txt
├── README.md
│
└── files/
    ├── inputf1.py
    ├── inputf2.py
    ├── inputf3.py
    └── project_word_doc.docx
---

## 🤖 ML Model

* **Algorithm:** RandomForestRegressor
* **Output:** Code Quality Score (0–10)

### Features Used:

* Number of lines
* Number of loops
* Number of print statements
* Number of functions
* Bad variable usage

---

## ⚙️ Installation & Run Locally

```bash
git clone https://github.com/subhani245/AI-Code-Quality-Analyzer.git
cd AI-Code-Quality-Analyzer
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔮 Future Improvements

* AST-based code analysis
* Cyclomatic complexity calculation
* Unused variable detection
* Code health visualization (charts)
* Multi-language code execution

---

## 📌 Authors

**Subhani Pathan and pratyush Kumar**