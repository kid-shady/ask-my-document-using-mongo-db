import streamlit as st
import requests

# FastAPI base URL
API_BASE_URL = "http://localhost:8000"

st.title("Ask my documents")

# Document Upload Section
st.header("📄 Upload Documents")
uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files and st.button("Upload Documents"):
    with st.spinner("Uploading documents..."):
        files = [("files", (file.name, file.getvalue(), "application/pdf")) for file in uploaded_files]
        try:
            response = requests.post(f"{API_BASE_URL}/upload/", files=files)
            if response.status_code == 200:
                st.success(f"✅ {response.json()['message']}")
            else:
                st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")

# Query Section
st.header("❓ Ask Questions")
query = st.text_input("Enter your question:")

if query and st.button("Get Answer"):
    with st.spinner("Processing query..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/query/",
                json={"query": query}
            )
            if response.status_code == 200:
                st.write("**Answer:**")
                st.write(response.json()["response"])
            else:
                st.error(f"❌ Query failed: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")