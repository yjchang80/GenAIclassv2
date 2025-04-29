import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import random

def analyze_twitter_data(df, genai):
    """
    Analyzes Twitter data to determine MBTI personality type.
    
    Parameters:
    ----------
    df : pandas.DataFrame
        DataFrame containing Twitter data.
    genai : GenAI
        Instance of the GenAI class for text generation.
        
    Returns:
    -------
    tuple
        (mbti_type, mbti_scores) - MBTI type and dimension scores.
    """
    # Generate MBTI analysis
    mbti_type, mbti_scores = genai.analyze_mbti(df)
    return mbti_type, mbti_scores

def generate_mbti_radar_chart(mbti_scores):
    """
    Generates a radar chart visualization of MBTI scores.
    
    Parameters:
    ----------
    mbti_scores : dict
        Dictionary containing scores for each MBTI dimension.
        
    Returns:
    -------
    plotly.graph_objects.Figure
        Radar chart figure.
    """
    # Create two radar charts: one for E/I vs N/S and one for T/F vs J/P
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'polar'}, {'type': 'polar'}]],
        subplot_titles=("Extraversion/Introversion & Intuition/Sensing", 
                        "Thinking/Feeling & Judging/Perceiving")
    )
    
    # First radar chart: E/I and N/S
    fig.add_trace(
        go.Scatterpolar(
            r=[mbti_scores['E'], mbti_scores['N'], mbti_scores['I'], mbti_scores['S']],
            theta=['Extraversion (E)', 'Intuition (N)', 'Introversion (I)', 'Sensing (S)'],
            fill='toself',
            name='Mind & Energy',
            line=dict(color='#4361ee')
        ),
        row=1, col=1
    )
    
    # Second radar chart: T/F and J/P
    fig.add_trace(
        go.Scatterpolar(
            r=[mbti_scores['T'], mbti_scores['J'], mbti_scores['F'], mbti_scores['P']],
            theta=['Thinking (T)', 'Judging (J)', 'Feeling (F)', 'Perceiving (P)'],
            fill='toself',
            name='Nature & Tactics',
            line=dict(color='#f72585')
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        polar2=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=500,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor='#f8f9fa',
        plot_bgcolor='#f8f9fa'
    )
    
    return fig

def create_travel_plan(preferences, mbti, genai):
    """
    Creates a comprehensive travel plan based on user preferences and MBTI.
    
    Parameters:
    ----------
    preferences : dict
        Dictionary containing user travel preferences.
    mbti : str
        MBTI personality type.
    genai : GenAI
        Instance of the GenAI class for text generation.
        
    Returns:
    -------
    dict
        Dictionary containing the complete travel plan.
    """
    # Generate travel recommendations
    travel_plan = genai.generate_travel_recommendations(preferences, mbti)
    return travel_plan

def extract_text_from_url(url):
    """
    Extracts the main text content from a URL.
    
    Parameters:
    ----------
    url : str
        URL to extract content from.
        
    Returns:
    -------
    str
        Extracted text content.
    """
    try:
        # Request the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Return a summary (first 500 characters)
        return text[:500] + "..." if len(text) > 500 else text
        
    except Exception as e:
        print(f"Error extracting text from URL: {str(e)}")
        return f"Failed to extract content from {url}. Please enter a topic directly."

def generate_daily_itinerary(day_number, date, preferences, travel_plan, choice_history, genai):
    """
    Generates a detailed daily itinerary based on preferences and choices.
    
    Parameters:
    ----------
    day_number : int
        The day number of the trip.
    date : datetime.date
        The date of the itinerary.
    preferences : dict
        User travel preferences.
    travel_plan : dict
        The complete travel plan.
    choice_history : list
        List of user choice history.
    genai : GenAI
        Instance of the GenAI class for text generation.
        
    Returns:
    -------
    dict
        Dictionary containing the daily itinerary.
    """
    # Create a simplified list of selected options from choice history
    selected_options = []
    for choice in choice_history:
        selected_options.append({
            'type': choice['type'],
            'selected': choice['selected']
        })
    
    # Generate daily itinerary
    daily_plan = genai.generate_daily_itinerary(day_number, date, preferences, selected_options)
    
    # Assign random coordinates for map visualization (in a real app, these would be real coordinates)
    # This is just for demonstration purposes
    base_lat = 40.7128  # Example: NYC latitude
    base_lon = -74.0060  # Example: NYC longitude
    
    for time_of_day in ['morning', 'afternoon', 'evening']:
        for i, activity in enumerate(daily_plan[time_of_day]):
            if 'location' not in activity or 'lat' not in activity['location']:
                # Generate random coordinates near the base point
                random_lat = base_lat + (random.random() - 0.5) * 0.05
                random_lon = base_lon + (random.random() - 0.5) * 0.05
                
                activity['location'] = {
                    'name': activity['description'].split(':')[0] if ':' in activity['description'] else activity['description'],
                    'lat': random_lat,
                    'lon': random_lon
                }
    
    return daily_plan

def get_attraction_options(city, country, travel_styles):
    """
    Gets attraction options based on location and travel styles.
    This is a placeholder function - in a real app, this would call an external API.
    
    Parameters:
    ----------
    city : str
        City name.
    country : str
        Country name.
    travel_styles : list
        List of preferred travel styles.
        
    Returns:
    -------
    list
        List of attraction options.
    """
    # Placeholder attractions - in a real app, these would come from an API
    attractions = [
        {
            "name": f"Main Museum in {city}",
            "description": "A world-class museum featuring local history and art.",
            "match_reason": "Perfect for cultural enthusiasts",
            "price": "$15"
        },
        {
            "name": f"{city} Historical District",
            "description": "Beautiful historic architecture and charming streets.",
            "match_reason": "Great for photography and history lovers",
            "price": "Free"
        },
        {
            "name": f"{city} Nature Park",
            "description": "Expansive park with hiking trails and scenic views.",
            "match_reason": "Ideal for nature and adventure lovers",
            "price": "$5"
        }
    ]
    
    return attractions

def get_accommodation_options(city, country, budget_level):
    """
    Gets accommodation options based on location and budget.
    This is a placeholder function - in a real app, this would call an external API.
    
    Parameters:
    ----------
    city : str
        City name.
    country : str
        Country name.
    budget_level : str
        Budget level indicator (e.g., "$", "$$").
        
    Returns:
    -------
    list
        List of accommodation options.
    """
    # Placeholder accommodations - in a real app, these would come from an API
    accommodations = [
        {
            "name": f"Central Hotel {city}",
            "price_level": budget_level,
            "description": "Comfortable hotel in the heart of the city.",
            "features": "Free WiFi, breakfast included, central location"
        },
        {
            "name": f"Boutique Stay {city}",
            "price_level": budget_level,
            "description": "Charming boutique hotel with unique character.",
            "features": "Artisan design, rooftop terrace, complimentary drinks"
        },
        {
            "name": f"{city} Riverside Inn",
            "price_level": budget_level[:-1] if len(budget_level) > 1 else "$",
            "description": "Peaceful accommodation with water views.",
            "features": "River views, quiet location, free parking"
        }
    ]
    
    return accommodations

def get_restaurant_options(city, country, food_preferences):
    """
    Gets restaurant options based on location and food preferences.
    This is a placeholder function - in a real app, this would call an external API.
    
    Parameters:
    ----------
    city : str
        City name.
    country : str
        Country name.
    food_preferences : str
        Food preferences or restrictions.
        
    Returns:
    -------
    list
        List of restaurant options.
    """
    # Placeholder restaurants - in a real app, these would come from an API
    restaurants = [
        {
            "name": f"Authentic {country} Cuisine",
            "cuisine": "Local",
            "price_level": "$$",
            "description": f"Traditional {country} dishes in a cozy atmosphere."
        },
        {
            "name": "International Fusion",
            "cuisine": "Fusion",
            "price_level": "$$$",
            "description": "Creative dishes combining local and international flavors."
        },
        {
            "name": f"{city} Street Food Market",
            "cuisine": "Various",
            "price_level": "$",
            "description": "Diverse selection of affordable local street food options."
        }
    ]
    
    return restaurants

def get_hidden_spots(city, country, travel_styles):
    """
    Gets hidden spots based on location and travel preferences.
    This is a placeholder function - in a real app, this would call an external API.
    
    Parameters:
    ----------
    city : str
        City name.
    country : str
        Country name.
    travel_styles : list
        List of preferred travel styles.
        
    Returns:
    -------
    list
        List of hidden spot options.
    """
    # Placeholder hidden spots - in a real app, these would come from an API
    hidden_spots = [
        {
            "name": f"Secret Viewpoint in {city}",
            "description": "A little-known spot with panoramic views of the city.",
            "why_special": "Few tourists know about this location, perfect for sunset photos."
        },
        {
            "name": f"Hidden Courtyard Café",
            "description": "Charming café tucked away in a historic courtyard.",
            "why_special": "Local favorite with authentic atmosphere and great coffee."
        },
        {
            "name": f"{city} Underground Art Space",
            "description": "Alternative art gallery showcasing local artists.",
            "why_special": "Off the tourist track, showing the contemporary culture of the city."
        }
    ]
    
    return hidden_spots

def get_transportation_options(city, country):
    """
    Gets transportation options based on location.
    This is a placeholder function - in a real app, this would call an external API.
    
    Parameters:
    ----------
    city : str
        City name.
    country : str
        Country name.
        
    Returns:
    -------
    dict
        Dictionary containing transportation options.
    """
    # Placeholder transportation options - in a real app, these would come from an API
    transportation = {
        "local_options": f"Public transit, taxis, and bike rentals are available throughout {city}.",
        "recommendation": "Public transportation is the most efficient way to get around the city center.",
        "transportation_tips": f"Consider purchasing a {city} transit pass to save money on multiple rides."
    }
    
    return transportation

def optimize_route(locations):
    """
    Optimizes a route between multiple locations.
    This is a placeholder function - in a real app, this would use a routing algorithm.
    
    Parameters:
    ----------
    locations : list
        List of location dictionaries with lat/lon coordinates.
        
    Returns:
    -------
    list
        Optimized list of locations in visit order.
    """
    # In a real app, this would implement a traveling salesman problem solution
    # For this demo, we'll just return the original order
    return locations

def generate_daily_itinerary_image(genai, day_number, daily_plan, preferences):
    """
    Generates an image of key attractions for a daily itinerary using DALL-E.
    """
    try:
        city = preferences.get('city', '')
        country = preferences.get('country', '')
        
        # Select top 2 attractions for the day (one from morning and one from afternoon)
        attractions = []
        
        if daily_plan.get('morning') and len(daily_plan.get('morning')) > 0:
            if isinstance(daily_plan['morning'][0], dict):
                attractions.append(daily_plan['morning'][0].get('description', ''))
            else:
                attractions.append(daily_plan['morning'][0])
                
        if daily_plan.get('afternoon') and len(daily_plan.get('afternoon')) > 0:
            if isinstance(daily_plan['afternoon'][0], dict):
                attractions.append(daily_plan['afternoon'][0].get('description', ''))
            else:
                attractions.append(daily_plan['afternoon'][0])
        
        # Generate a generic image if no attractions are specified
        if not attractions:
            prompt = f"A photorealistic image of a famous landmark or tourist attraction in {city}, {country}. No text, no borders."
        else:
            # Generate image of main attraction (not a collage or multi-panel image)
            attraction = attractions[0] if len(attractions) > 0 else f"landmark in {city}"
            prompt = f"A photorealistic image of {attraction} in {city}, {country}. No text, no borders, no collage. Just one clear image of the attraction."
        
        # Generate the image
        image_url = genai.generate_image(
            prompt=prompt.strip(),
            size="1024x1024",
            quality="standard"
        )
        
        return image_url
    
    except Exception as e:
        print(f"Error generating daily itinerary image: {str(e)}")
        return None