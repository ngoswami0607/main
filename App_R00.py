# App_R00.py

from functions.building_dimension import building_dimension

# Your Streamlit code here
import streamlit as st

def main():
    st.title("Wind Load Calculator")
    building_dimension()  # call your function here

if __name__ == "__main__":
    main()
