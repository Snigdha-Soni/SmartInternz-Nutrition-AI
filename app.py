from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import pandas as pd
import requests

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini response
def get_gemini_response(input_text, image, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content([input_text, image[0], prompt])
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

# Function to set up image format
def input_image_setup(upload_file):
    if upload_file is not None:
        bytes_data = upload_file.getvalue()
        image_parts = [
            {
                "mime_type": upload_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded!")

# Function to get fitness data from a tracker API
def get_fitness_data(user_id, api_key):
    try:
        response = requests.get(f"https://api.fitness-tracker.com/users/{user_id}/data", headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return f"An error occurred: {e}"

# Function to save data to CSV
def save_data_to_csv(input_text, image_name, response, fitness_data=None, filename='user_data_log.csv'):
    data = {
        'Input Prompt': [input_text],
        'Image': [image_name],
        'Response': [response],
        'Fitness Data': [fitness_data] if fitness_data else [None]
    }
    df = pd.DataFrame(data)
    df.to_csv(filename, mode='a', header=False, index=False)

# Define prompt for Gemini model
input_prompt = """As an expert nutritionist known as NutriSense AI, your task is to analyze the food items presented in the image provided. 
Please calculate the total caloric content and offer a detailed breakdown of each food item with its corresponding calorie count in the following format:
1. Item1 - number of calories
2. Item2 - number of calories
...
Additionally, provide an assessment of the meal's overall healthiness. Finally, include a percentage-based breakdown of the meal's nutritional components, including carbohydrates, fats, fibers, sugars, and other essential dietary elements necessary for a balanced diet.
After analyzing a meal, you could rate it on to 5 ⭐️ Star for healthiness.
"""

# Initialize Streamlit app
st.set_page_config(page_title="AI Nutritionist App")

st.header("AI Nutritionist App")
input_text = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
user_id = st.text_input("Enter your fitness tracker user ID (optional)", key="user_id")
api_key = st.text_input("Enter your fitness tracker API key (optional)", key="api_key")
image = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = image.resize((800, 800))  # Resize image for faster processing
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit = st.button("Tell me the total calories")
 # Call the model and display results here

if submit:
    with st.spinner('Analyzing the image...'):
        try:
            image_data = input_image_setup(uploaded_file)
            response = get_gemini_response(input_text, image_data, input_prompt)
            st.success("Analysis complete!")
            st.subheader("The Response is")
            st.write(response)
            
            # Save analysis to log
            save_data_to_csv(input_text, uploaded_file.name, response)
            
            # Fetch and display fitness data if user ID and API key are provided
            if user_id and api_key:
                fitness_data = get_fitness_data(user_id, api_key)
                st.subheader("Fitness Data")
                st.write(fitness_data)
                # Save fitness data to log
                save_data_to_csv(input_text, uploaded_file.name, response, fitness_data)
            else:
                st.info("Fitness tracker data is not provided.")
                
            st.success("Data saved and fitness information processed (if provided).")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Function to save meal log to CSV
def save_meal_log(input_text, image_name, response):
    log = pd.DataFrame({
        'Input Prompt': [input_text],
        'Image': [image_name],
        'Response': [response]
    })
    log.to_csv('meal_log.csv', mode='a', header=False, index=False)
