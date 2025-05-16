from facebook_business.exceptions import FacebookRequestError
from langchain_google_genai import ChatGoogleGenerativeAI
from prompt import generate_campaign_prompt
from graph import graph
import streamlit as st
import os, base64

# function to execute the user input and create campaign
def generate(brand_name, product_name, campaign_goal, daily_budget, start_date, end_date, page_id, brand_description,
             landing_page, call_to_action, image, tone, image_style_prompt, age_min, age_max, gender,
            interests):

    if image:
        image_path = os.path.join("./Images", image.name)
        with open(image_path, "wb") as f:
            f.write(image.read())
    else:
        image_llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash-exp-image-generation")
        message = {
            "role": "user",
            "content": image_style_prompt,
        }

        response = image_llm.invoke(
            [message],
            generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
        )

        # Obtain image in base64 format from the LLM response
        image_base64 = response.content[1].get("image_url").get("url").split(",")[-1]
        with open(os.path.join("./Images", "ad_image.png"), "wb") as f:
            f.write(base64.b64decode(image_base64))
        image_path = os.path.join("./Images", "ad_image.png")

    
    prompt = generate_campaign_prompt(
        brand_name=brand_name,
        product_name=product_name,
        campaign_goal=campaign_goal,
        daily_budget=daily_budget,
        start_date=start_date,
        end_date=end_date,
        page_id=page_id,
        brand_description=brand_description,
        landing_page=landing_page,
        call_to_action=call_to_action,
        image_path=image_path,
        age_min=age_min,
        age_max=age_max,
        tone=tone,
        gender=gender,
        interests=interests
    )

    # Invoke the graph with user prompt
    try:
        response = graph.invoke({"messages": [{"role": "user", "content": prompt}]})

    except FacebookRequestError as e:
        response = f"### Provide valid access credentials! \nDetails: {e}"

    # Store the response in session state for later access
    st.session_state.generated_response = response


# Streamlit app ui:
 
st.set_page_config(layout="wide")

left_col, right_col = st.columns([0.55,0.45],border=True)

with left_col:
    st.subheader("Campaign Summary:", divider="gray")
    with st.form("Generate Form"):
        with st.expander("1. Brand & Product Details", expanded=True):
            brand_name = st.text_input("Brand Name")
            product_name = st.text_input("Product Name")
            brand_description = st.text_area("Brand Description")
            landing_page = st.text_input("Landing Page URL")
            page_id = st.text_input("Page Id")

        with st.expander("2. Campaign Strategy"):
            campaign_goal = st.selectbox("Campaign Objective", ["Awareness", "Traffic", "Conversions"])
            platform = st.selectbox("Ad Platform", ["Meta", "Google"])
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            daily_budget = st.number_input("Daily Budget ($)", min_value=1)
            bidding_strategy = st.selectbox("Bidding Strategy", ["Lowest Cost", "Cost Cap", "Bid Cap"])
            call_to_action = st.selectbox("Call to Action", ["Learn More", "Shop Now", "Sign Up"])

        with st.expander("3. Target Audience"):
            age_min = st.number_input("Min Age", step=1)
            age_max = st.number_input("Max Age", step=1)
            gender = st.selectbox("Gender", ["All", "Male", "Female", "Other"])
            country = st.text_input("Country")
            interests = st.text_input("Interests (comma-separated)")

        with st.expander("4. Ad Tone & Style"):
            tone = st.selectbox("Tone of Ad", ["Professional", "Witty", "Emotional", "Sarcastic"])
            image_style_prompt = st.text_input("Image Style (optional)", placeholder="e.g., Minimalist, Vibrant, 3D")
        
        image = st.file_uploader("Upload Image:")

        submitted = st.form_submit_button("Generate Campaign")
        if submitted:
            generate(brand_name, product_name, campaign_goal, daily_budget, start_date, end_date, page_id, brand_description,
                landing_page, call_to_action, image, tone, image_style_prompt, age_min, age_max, gender,
                interests)
             
with right_col:
    st.subheader("Agent Output", divider="gray")

    if "generated_response" not in st.session_state:
        st.session_state.generated_response = ""

    st.markdown(st.session_state.generated_response)



