import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import re
from datetime import datetime, timedelta
from typing import List
from genai import GenAI
from utils import (
    analyze_twitter_data,
    generate_mbti_radar_chart,
    create_travel_plan,
    generate_daily_itinerary,
    generate_daily_itinerary_image,
    optimize_route,
    get_accommodation_options,
    get_restaurant_options,
    get_attraction_options,
    get_hidden_spots,
    get_transportation_options
)

# Load environment variables
load_dotenv()
openai_api_key = st.secrets["OPENAI_API_KEY"]
genai = GenAI(openai_api_key)

# Configure page settings
st.set_page_config(
    page_title="Dream Destination",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling (existing CSS code remains the same)
st.markdown("""
<style>
:root {
    --primary-color: #4361ee;
    --secondary-color: #3f37c9;
    --accent-color: #f72585;
    --background-color: #f8f9fa;
    --text-color: #212529;
}

body {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='%234361ee' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 5 2 2 5 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z'%3E%3C/path%3E%3C/svg%3E"), auto;
}

.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

.stButton>button {
    background-color: var(--primary-color);
    color: white;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    transition: all 0.3s;
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='%23f72585' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 5 2 2 5 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z'%3E%3C/path%3E%3C/svg%3E"), pointer;
}

.stButton>button:hover {
    background-color: var(--secondary-color);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
}

h1, h2, h3 {
    color: var(--primary-color);
}

.highlight-card {
    border: 1px solid #e9ecef;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    background-color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    transition: all 0.3s;
}

.highlight-card:hover {
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    transform: translateY(-5px);
}

.travel-option {
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='%233f37c9' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 5 2 2 5 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z'%3E%3C/path%3E%3C/svg%3E"), pointer;
    transition: all 0.2s;
}

.travel-option:hover {
    border-color: var(--accent-color);
    background-color: #f8f9fa;
}

.travel-option.selected {
    border-color: var(--primary-color);
    background-color: rgba(67, 97, 238, 0.1);
}

.drag-item {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 5px;
    background-color: white;
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='%234361ee' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 5 2 2 5 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z'%3E%3C/path%3E%3C/svg%3E"), grab;
}

/* Additional cursor styles for other interactive elements */
.stSelectbox__control, 
.stMultiSelect__control, 
.stTextInput__input, 
.stDateInput__input,
.stFileUploader {
    cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='%23f72585' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 5 2 2 5 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z'%3E%3C/path%3E%3C/svg%3E"), text;
}

/* New styles for daily itinerary cards */
.day-card {
    border: 1px solid #e9ecef;
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 3rem;
    background-color: white;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s;
    overflow: hidden;
}

.day-card:hover {
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
}

.day-title {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    color: var(--primary-color);
    border-bottom: 3px solid var(--accent-color);
    padding-bottom: 0.8rem;
    text-transform: capitalize;
}

.activity-section {
    margin-bottom: 2rem;
    padding-left: 1rem;
    border-left: 3px solid #e9ecef;
}

.activity-time {
    font-weight: bold;
    color: var(--accent-color);
    font-size: 1.3rem;
    margin-bottom: 1rem;
}

.activity-image-container {
    margin: 1.5rem 0 2.5rem 0;
    text-align: center;
    position: relative;
}

.activity-image-container::before {
    content: '';
    position: absolute;
    top: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 50%;
    height: 5px;
    background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
}

.activity-image-container::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 50%;
    height: 5px;
    background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
}

.activity-image {
    border-radius: 15px;
    max-width: 100%;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    transition: all 0.3s;
    border: 1px solid #f0f0f0;
}

.activity-image:hover {
    transform: scale(1.02);
}

/* Style for activity descriptions */
.activity-description {
    padding: 0.8rem;
    background-color: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 0.8rem;
    transition: all 0.2s;
    border-left: 3px solid var(--primary-color);
}

.activity-description:hover {
    background-color: #f0f4ff;
    transform: translateX(5px);
}
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">✈️ Dream Destination</h1>
    <p style="font-size: 1.2rem; color: #6c757d;">Your AI-powered personalized travel companion</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'twitter_data' not in st.session_state:
    st.session_state.twitter_data = None
if 'mbti' not in st.session_state:
    st.session_state.mbti = None
if 'mbti_scores' not in st.session_state:
    st.session_state.mbti_scores = None
if 'travel_preferences' not in st.session_state:
    st.session_state.travel_preferences = {}
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'daily_itineraries' not in st.session_state:
    st.session_state.daily_itineraries = []
if 'daily_images' not in st.session_state:
    st.session_state.daily_images = []

# Sidebar Navigation
st.sidebar.markdown("## Navigation")
pages = [
    "Home - Personality Analysis",
    "Travel Preferences",
    "Travel Plan Generator",
    "Daily Visual Itinerary",  # New page
    "Download Travel Plan"
]

# Navigation buttons in sidebar
for i, page_name in enumerate(pages):
    if st.sidebar.button(page_name, key=f"nav_{i}"):
        st.session_state.page = i

# Display current progress
st.sidebar.progress((st.session_state.page) / (len(pages) - 1))

# Page content based on current page
if st.session_state.page == 0:
    # Divide the entire page into two columns: 2/3 for functions, 1/3 for image and inspiration
    left_col, right_col = st.columns([2, 1])

    # Left side: Title and App Functions
    with left_col:

        st.header("Personality Analysis")
        st.markdown("Upload your Twitter data to analyze your personality and travel preferences.")

        uploaded_file = st.file_uploader("Upload CSV file containing tweets", type=['csv'])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                required_columns = ['text', 'favorite_count', 'view_count']
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    with st.spinner("Analyzing your Twitter data..."):
                        # Calculate engagement and clean data
                        df['engagement'] = df['favorite_count'] / df['view_count']
                        df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['engagement'])

                        # Save data to session state
                        st.session_state.twitter_data = df

                        # Perform MBTI analysis
                        mbti, mbti_scores = analyze_twitter_data(df, genai)
                        st.session_state.mbti = mbti
                        st.session_state.mbti_scores = mbti_scores

                        # Show MBTI result and radar chart
                        col_a, col_b = st.columns([2, 3])
                        with col_a:
                            st.markdown(f"""
                            <div class="highlight-card">
                                <h2 style="text-align: center;">Your MBTI Type</h2>
                                <h1 style="text-align: center; font-size: 3rem; color: var(--accent-color);">{mbti}</h1>
                                <p style="text-align: center;">{genai.generate_text(f"Describe the {mbti} personality type in 1-2 sentences, focusing on travel preferences.")}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_b:
                            fig = generate_mbti_radar_chart(mbti_scores)
                            st.plotly_chart(fig, use_container_width=True)

                        # Navigation button
                        if st.button("Proceed to Travel Preferences", key="proceed_to_preferences"):
                            st.session_state.page = 1
                            st.rerun()

            except Exception as e:
                st.error(f"Error analyzing the data: {str(e)}")

        # Sample data button
        if st.button("Use Sample Data Instead"):
            with st.spinner("Loading sample data..."):
                # Provide sample MBTI and scores
                sample_mbti = "ENFP"
                sample_scores = {
                    'E': 75, 'I': 25,
                    'N': 80, 'S': 20,
                    'F': 65, 'T': 35,
                    'P': 70, 'J': 30
                }
                st.session_state.mbti = sample_mbti
                st.session_state.mbti_scores = sample_scores

                # Show sample MBTI results
                col_a, col_b = st.columns([2, 3])
                with col_a:
                    st.markdown(f"""
                    <div class="highlight-card">
                        <h2 style="text-align: center;">Your MBTI Type</h2>
                        <h1 style="text-align: center; font-size: 3rem; color: var(--accent-color);">{sample_mbti}</h1>
                        <p style="text-align: center;">{genai.generate_text(f"Describe the {sample_mbti} personality type in 1-2 sentences, focusing on travel preferences.")}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    fig = generate_mbti_radar_chart(sample_scores)
                    st.plotly_chart(fig, use_container_width=True)

                if st.button("Proceed to Travel Preferences", key="proceed_from_sample"):
                    st.session_state.page = 1
                    st.rerun()

    # Right side: Travel image and MBTI-based travel importance text
    with right_col:
        with st.spinner("Generating inspirational content..."):
            try:
                # Generate travel-related image
                travel_image_url = genai.generate_image(
                    "a breathtaking travel destination, dreamy, colorful, relaxing vibes, photorealistic, no text"
                )
                if travel_image_url:
                    st.image(travel_image_url, caption="Imagine Your Dream Destination", use_container_width=True)
                else:
                    st.warning("Could not load travel image at the moment.")

                # Generate motivational text about MBTI-based travel planning
                importance_text = genai.generate_text(
                    "Write a short motivational paragraph (maximum 3 sentences) explaining why creating a travel plan based on MBTI personality type is important and enhances travel experiences.",
                    instructions="You are a travel inspiration writer. Make it motivational, focused on MBTI personalization benefits.",
                    temperature=0.7
                )
                st.markdown(f"""
                <div class="highlight-card" style="margin-top: 1rem;">
                    <h3 style="text-align: center;">✈️ Why Personality-based Travel Planning Matters</h3>
                    <p style="text-align: center;">{importance_text}</p>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error generating right panel content: {str(e)}")

elif st.session_state.page == 1:
    # Travel Preferences Page
    st.header("Travel Preferences")
    st.markdown("Tell us about your dream trip so we can customize your perfect itinerary.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Destination Card
        with st.container():
            st.subheader("Destination")
            country = st.text_input("Country", value=st.session_state.travel_preferences.get('country', ''))
            city = st.text_input("City", value=st.session_state.travel_preferences.get('city', ''))
        
        # Travel Dates Card
        with st.container():
            st.subheader("Travel Dates")
            col1a, col1b = st.columns(2)
            with col1a:
                start_date = st.date_input("Start Date", value=None)
            with col1b:
                end_date = st.date_input("End Date", value=None)
    
    with col2:
        # Travel Details Card
        with st.container():
            st.subheader("Travel Details")
            num_travelers = st.number_input("Number of Travelers", min_value=1, max_value=10, value=st.session_state.travel_preferences.get('num_travelers', 1))
            
            budget_options = {
                "Budget": "$",
                "Moderate": "$$",
                "Luxury": "$$$",
                "Ultra-Luxury": "$$$$"
            }
            budget = st.select_slider(
                "Budget Range",
                options=list(budget_options.keys()),
                value=st.session_state.travel_preferences.get('budget', 'Moderate')
            )
            
            travel_style = st.multiselect(
                "Travel Style (Select up to 3)",
                ["Adventure", "Relaxation", "Cultural", "Foodie", "Nature", "Shopping", "Nightlife", "Historical", "Family-friendly"],
                default=st.session_state.travel_preferences.get('travel_style', ["Cultural"])
            )
            
            # Limit selection to 3 options
            if len(travel_style) > 3:
                st.warning("Please select a maximum of 3 travel styles.")
                travel_style = travel_style[:3]
    
    # Additional Preferences Card
    with st.container():
        st.subheader("Additional Preferences")
        accommodation_type = st.selectbox(
            "Preferred Accommodation Type",
            ["Any", "Hotel", "Hostel", "Apartment", "Resort", "Boutique Hotel", "Bed & Breakfast"],
            index=["Any", "Hotel", "Hostel", "Apartment", "Resort", "Boutique Hotel", "Bed & Breakfast"].index(st.session_state.travel_preferences.get('accommodation_type', 'Any'))
        )
        
        col3, col4 = st.columns(2)
        with col3:
            must_see_attractions = st.text_area("Must-See Attractions (one per line)", value=st.session_state.travel_preferences.get('must_see_attractions', ''))
        with col4:
            food_preferences = st.text_area("Food Preferences or Restrictions", value=st.session_state.travel_preferences.get('food_preferences', ''))
    
    # Save preferences
    if st.button("Save Preferences and Generate Plan"):
        if not country or not city:
            st.error("Please enter both country and city.")
        elif not start_date or not end_date:
            st.error("Please select both start and end dates.")
        elif start_date >= end_date:
            st.error("End date must be after start date.")
        elif len(travel_style) > 3:
            st.error("Please select a maximum of 3 travel styles.")
        else:
            # Save preferences to session state
            st.session_state.travel_preferences = {
                'country': country,
                'city': city,
                'start_date': start_date,
                'end_date': end_date,
                'num_travelers': num_travelers,
                'budget': budget,
                'budget_level': budget_options[budget],
                'travel_style': travel_style,
                'accommodation_type': accommodation_type,
                'must_see_attractions': must_see_attractions,
                'food_preferences': food_preferences,
                'duration': (end_date - start_date).days + 1  # Calculate trip duration in days
            }
            
            # Proceed to next page
            st.session_state.page = 2
            st.rerun()

elif st.session_state.page == 2:
    # Travel Plan Generator Page
    st.header("Your Personalized Travel Plan")
    
    # Display selected preferences
    preferences = st.session_state.travel_preferences
    mbti = st.session_state.mbti
    
    st.markdown(f"""
    <div class="highlight-card">
        <h3>Trip Details</h3>
        <p><strong>Destination:</strong> {preferences['city']}, {preferences['country']}</p>
        <p><strong>Dates:</strong> {preferences['start_date']} to {preferences['end_date']} ({preferences['duration']} days)</p>
        <p><strong>Budget:</strong> {preferences['budget']} ({preferences['budget_level']})</p>
        <p><strong>Travel Style:</strong> {', '.join(preferences['travel_style'])}</p>
        <p><strong>MBTI Personality:</strong> {mbti}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'travel_plan' not in st.session_state or not st.session_state.travel_plan:
        with st.spinner("Creating your personalized travel plan based on your MBTI personality type..."):
            # Create detailed travel plan
            travel_plan = genai.create_detailed_travel_plan(
                mbti_type=mbti,
                city=preferences['city'],
                country=preferences['country'],
                duration=preferences['duration'],
                num_travelers=preferences['num_travelers'],
                budget=preferences['budget'],
                travel_style=preferences['travel_style'],
                accommodation_type=preferences['accommodation_type'],
                must_see_attractions=preferences.get('must_see_attractions', ''),
                food_preferences=preferences.get('food_preferences', ''),
                start_date=preferences.get('start_date')
            )
            st.session_state.travel_plan = travel_plan
    
    # Display the travel plan
    st.markdown(f"""
    <div class="highlight-card">
        <h2 style="text-align:center">✨ {st.session_state.travel_plan['mbti_type']} Travel Plan for {st.session_state.travel_plan['destination']} ✨</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Use the HTML version of the plan for better formatting
    st.markdown(st.session_state.travel_plan['plan_html'], unsafe_allow_html=True)

    # Add navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Preferences"):
            st.session_state.page = 1
            st.rerun()
    with col2:
        if st.button("Generate Daily Visual Itinerary"):
            st.session_state.page = 3
            st.rerun()
    with col3:
        if st.button("Skip to Download Travel Plan"):
            st.session_state.page = 4
            st.rerun()

elif st.session_state.page == 3:
    # New Page: Daily Visual Itinerary
    st.header("Daily Visual Itinerary")
    
    preferences = st.session_state.travel_preferences
    travel_plan = st.session_state.travel_plan
    
    if not travel_plan:
        st.warning("Please complete the Travel Plan Generator step first.")
        if st.button("Go to Travel Plan Generator"):
            st.session_state.page = 2
            st.rerun()
    else:
        st.markdown(f"""
        <div class="highlight-card">
            <h3>Trip Overview</h3>
            <p><strong>Destination:</strong> {preferences['city']}, {preferences['country']}</p>
            <p><strong>Duration:</strong> {preferences['duration']} days</p>
            <p><strong>Dates:</strong> {preferences['start_date']} to {preferences['end_date']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate daily itineraries and images if not already generated
        if len(st.session_state.daily_itineraries) < preferences['duration']:
            with st.spinner("Generating daily itineraries with visuals... This may take a minute..."):
                # Clear existing data
                st.session_state.daily_itineraries = []
                st.session_state.daily_images = []
                
                # Get start date
                start_date = preferences['start_date']
                
                # Create empty choice history for the first iteration
                choice_history = []
                
                # Generate itinerary for each day
                for day in range(1, preferences['duration'] + 1):
                    current_date = start_date + timedelta(days=day-1)
                    
                    # Generate daily itinerary 
                    daily_plan = generate_daily_itinerary(
                        day_number=day,
                        date=current_date,
                        preferences=preferences,
                        travel_plan=travel_plan,
                        choice_history=choice_history,
                        genai=genai
                    )
                    
                    # Add to choice history for next iteration
                    choice_history.append({
                        'type': 'day_plan',
                        'selected': daily_plan['theme']
                    })
                    
                    # Generate image for the day using helper function
                    try:
                        # Generate image
                        image_url = generate_daily_itinerary_image(
                            genai=genai,
                            day_number=day,
                            daily_plan=daily_plan,
                            preferences=preferences
                        )
                        
                        # Store daily plan and image URL
                        st.session_state.daily_itineraries.append(daily_plan)
                        st.session_state.daily_images.append(image_url)
                        
                        # Wait briefly between image generation requests to avoid rate limits
                        import time
                        time.sleep(1)
                    except Exception as e:
                        st.error(f"Error generating image for Day {day}: {str(e)}")
                        st.session_state.daily_itineraries.append(daily_plan)
                        st.session_state.daily_images.append(None)
        
        # Display daily itineraries with generated images
    for day, (daily_plan, image_url) in enumerate(zip(st.session_state.daily_itineraries, st.session_state.daily_images), 1):
        current_date = preferences['start_date'] + timedelta(days=day-1)
        
        st.markdown(f"""
        <div class="day-card">
            <h2 class="day-title">Day {day}: {daily_plan['theme']} - {current_date.strftime('%A, %B %d')}</h2>
        """, unsafe_allow_html=True)
        
        # Display the image only
        if image_url:
            st.markdown(f"""
            <div class="activity-image-container">
                <img src="{image_url}" alt="Day {day} - {daily_plan['theme']}" class="activity-image">
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close day-card div

    # Navigation buttons placed after the loop (only displayed once)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Travel Plan", key="back_to_travel_plan_button"):
            st.session_state.page = 2
            st.rerun()
    with col2:
        if st.button("Go to Download Travel Plan", key="go_to_download_from_visual"):
            st.session_state.page = 4
            st.rerun()

elif st.session_state.page == 4:
    # Download Travel Plan page (previously page 3, now page 4)
    st.header("Download Your Travel Plan")
    
    preferences = st.session_state.travel_preferences
    travel_plan = st.session_state.travel_plan
    
    if not travel_plan:
        st.warning("Please complete the Travel Plan Generator step first.")
        if st.button("Go to Travel Plan Generator"):
            st.session_state.page = 2
            st.rerun()
    else:
        # Display plan summary
        st.markdown(f"""
        <div class="highlight-card">
            <h3>Trip Details</h3>
            <p><strong>Destination:</strong> {preferences['city']}, {preferences['country']}</p>
            <p><strong>Dates:</strong> {preferences['start_date']} to {preferences['end_date']} ({preferences['duration']} days)</p>
            <p><strong>Travel Plan:</strong> {travel_plan['title'] if 'title' in travel_plan else 'Your Personalized Itinerary'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Generation options
        st.subheader("PDF Export Options")
        
        col1, col2 = st.columns(2)
        with col1:
            include_attractions = st.checkbox("Include Top Attractions", value=True)
            include_restaurants = st.checkbox("Include Restaurant Recommendations", value=True)
            include_daily_images = st.checkbox("Include Daily Itinerary Images", value=True, 
                help="Include the AI-generated images for each day of your itinerary")
        
        with col2:
            include_map = st.checkbox("Include City Map", value=True)
            include_budget = st.checkbox("Include Budget Breakdown", value=True)
            include_weather = st.checkbox("Include Weather Forecast", value=False,
                help="Add weather forecast information for your travel dates")
        
        # PDF Theme options
        st.subheader("PDF Theme")
        pdf_theme = st.radio(
            "Select PDF Theme",
            ["Professional", "Adventure", "Luxury", "Minimalist"],
            horizontal=True
        )
        
        # Example PDF preview image
        st.subheader("Preview")
        st.info("PDF Preview would appear here in a real application.")
        
        # Generate PDF button
        if st.button("Generate Travel Plan PDF"):
            with st.spinner("Generating your PDF travel plan..."):
                # In a real application, this would generate a PDF with the selected options
                # For this example, we'll just show a success message
                st.success("Your travel plan PDF has been generated!")
                
                # Add a dummy download button (in a real app, this would download the actual PDF)
                st.download_button(
                    label="Download PDF",
                    data=travel_plan['plan_markdown'],  # This would be the actual PDF data in a real app
                    file_name=f"{preferences['city']}_{preferences['country']}_travel_plan.pdf",
                    mime="application/pdf"
                )
                
        # Alternative download formats
        st.subheader("Alternative Download Formats")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="Download as Markdown",
                data=travel_plan['plan_markdown'],
                file_name=f"{preferences['city']}_travel_plan.md",
                mime="text/markdown"
            )
        
        with col2:
            # In a real app, this would convert to HTML format
            if st.button("Download as HTML"):
                st.info("HTML download would be available here in a real application.")
        
        with col3:
            # In a real app, this would convert to DOCX format
            if st.button("Download as Word Document"):
                st.info("Word document download would be available here in a real application.")
