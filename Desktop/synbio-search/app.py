import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# 1. Page Configuration
st.set_page_config(page_title="SynBio Search Engine", page_icon="🧬", layout="wide")
st.title("🧬 SynBio Function-to-Tool Search")
st.write("Type what you want to achieve in plain English, and the AI will match you with the right software.")

# 2. Load your database dynamically from the same directory as app.py
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "tools.csv")
    return pd.read_csv(file_path)

df = load_data()

# 3. Pull key securely from Streamlit Secrets (Invisible to public)
openai_key = st.secrets["OPENAI_API_KEY"]

if not openai_key:
    st.error("System configuration error: Missing API Key.")
else:
    client = OpenAI(api_key=openai_key)
    
    # 4. User Input
    user_query = st.text_input("What are you trying to do?", placeholder="e.g., I want to model a genetic toggle switch...")

    if user_query:
        with st.spinner("Analyzing tools..."):
            db_context = df.to_string(index=False)
            
            system_prompt = (
                "You are an expert synthetic biology assistant. Your job is to look at the provided database "
                "of tools and recommend the best software based on the user's request.\n\n"
                "Database:\n"
                f"{db_context}\n\n"
                "Instructions:\n"
                "1. Only recommend tools that are present in the provided database.\n"
                "2. Explain *why* the tool fits the user's intent in 1-2 sentences.\n"
                "3. Present the results cleanly using markdown (Name, Category, Input, Output, and Link)."
            )
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Find the best tools for: {user_query}"}
                    ],
                    temperature=0.2
                )
                
                st.subheader("Recommended Tools")
                st.markdown(response.choices[0].message.content)
                
            except Exception as e:
                st.error("An execution error occurred. Please try again later.")
