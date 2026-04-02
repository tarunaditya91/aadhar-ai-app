import streamlit as st
import requests

st.title("🪪 Aadhaar Verification System")

st.write("Click any image OR upload your own")

API_URL = "http://127.0.0.1:8000/verify-aadhar"

# ---------------------------
# IMAGE PATHS
# ---------------------------
image1_path = "image copy 2.png"
image2_path = "image copy 3.png"

# ---------------------------
# RESULT DISPLAY FUNCTION
# ---------------------------
def show_result(result):
    st.subheader("📊 Result")

    if result.get("status") == "matched":
        st.success("✅ Match Found")
        st.write(f"Match Percentage: {result.get('percentage', 0)}%")
    else:
        st.warning("❌ No Match Found")

    data = result.get("data", {})

    st.write("### Extracted Details:")
    st.write(f"👤 Name: {data.get('name', '-')}")
    st.write(f"📅 DOB: {data.get('dob', '-')}")
    st.write(f"🆔 Aadhaar: {data.get('aadhaar', '-')}")
    st.write(f"⚧ Gender: {data.get('gender', '-')}")


# ---------------------------
# PREDEFINED IMAGES
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.image(image1_path, caption="Aadhaar Image 1", width='stretch')
    if st.button("Verify Image 1"):
        with open(image1_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f})

        result = response.json()
        show_result(result)


with col2:
    st.image(image2_path, caption="Aadhaar Image 2", width='stretch')
    if st.button("Verify Image 2"):
        with open(image2_path, "rb") as f:
            response = requests.post(API_URL, files={"file": f})

        result = response.json()
        show_result(result)

# ---------------------------
# UPLOAD IMAGE
# ---------------------------
st.subheader("📤 Upload Your Own Image")

uploaded_file = st.file_uploader("Choose Aadhaar Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width='stretch')

    if st.button("Verify Uploaded Image"):
        response = requests.post(
            API_URL,
            files={"file": uploaded_file.getvalue()}
        )

        result = response.json()
        show_result(result)