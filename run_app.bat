@echo off
setlocal
python -m pip install -r requirements.txt
streamlit run app.py
