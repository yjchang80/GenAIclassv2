import os
import openai
import json
import pandas as pd
import time
import re
import markdown
from typing import List, Dict, Optional, Union
from datetime import datetime

class GenAI:
    def __init__(self, openai_api_key):
        self.client = openai.Client(api_key=openai_api_key)
        self.openai_api_key = openai_api_key

    def generate_text(self, prompt, instructions='You are a helpful AI travel assistant', model="gpt-4o", output_type='text', temperature=1):
        try:
            completion = self.client.chat.completions.create(
                model=model,
                temperature=temperature,
                response_format={"type": output_type},
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ]
            )
            response = completion.choices[0].message.content
            return response
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return "Sorry, I couldn't generate a response at the moment."

    def analyze_mbti(self, tweets_df):
        try:
            sample_tweets = tweets_df.sample(min(50, len(tweets_df)))
            tweets_text = "\n---\n".join(sample_tweets['text'].tolist())
            
            prompt = f"""
            Based on the following tweets, analyze the likely MBTI (Myers-Briggs Type Indicator) personality type.
            Tweets:
            {tweets_text}
            Return JSON:
            {{
                "mbti_type": "XXXX",
                "scores": {{
                    "E": 0-100,
                    "I": 0-100,
                    "N": 0-100,
                    "S": 0-100,
                    "F": 0-100,
                    "T": 0-100,
                    "J": 0-100,
                    "P": 0-100
                }},
                "explanation": "Brief explanation"
            }}
            """

            response = self.generate_text(
                prompt,
                instructions="You are an AI psychologist specializing in personality analysis. Return only valid JSON.",
                output_type="json_object"
            )

            if isinstance(response, str):
                response = json.loads(response)

            mbti_type = response.get("mbti_type", "ENFP")
            scores = response.get("scores", {
                "E": 50, "I": 50, "N": 50, "S": 50, "F": 50, "T": 50, "J": 50, "P": 50
            })

            return mbti_type, scores

        except Exception as e:
            print(f"Error analyzing MBTI: {str(e)}")
            return "ENFP", {"E": 60, "I": 40, "N": 70, "S": 30, "F": 65, "T": 35, "J": 45, "P": 55}

    def create_detailed_travel_plan(
        self, 
        mbti_type: str,
        city: str, 
        country: str, 
        duration: int,
        num_travelers: int,
        budget: str,
        travel_style: List[str],
        accommodation_type: str,
        must_see_attractions: Optional[str] = '',
        food_preferences: Optional[str] = '',
        start_date: Optional[datetime] = None
    ):
        """
        Create a comprehensive travel plan with detailed considerations

        Parameters:
        ----------
        mbti_type : str
            Traveler's MBTI personality type
        city : str
            Destination city
        country : str
            Destination country
        duration : int
            Trip duration in days
        num_travelers : int
            Number of people traveling
        budget : str
            Budget range (Budget/Moderate/Luxury/Ultra-Luxury)
        travel_style : List[str]
            Preferred travel styles
        accommodation_type : str
            Preferred accommodation type
        must_see_attractions : Optional[str], optional
            Specific attractions to include, by default ''
        food_preferences : Optional[str], optional
            Dietary restrictions or preferences, by default ''
        start_date : Optional[datetime], optional
            Planned start date of the trip, by default None

        Returns:
        -------
        Dict
            Comprehensive travel plan with details
        """
        try:
            # Construct a detailed prompt incorporating all parameters
            prompt = f"""
            Create a comprehensive {duration}-day travel plan for an {mbti_type} traveler visiting {city}, {country}.

            Trip Specifics:
            - Number of Travelers: {num_travelers}
            - Budget Level: {budget}
            - Travel Styles: {', '.join(travel_style)}
            - Accommodation Preference: {accommodation_type}

            Detailed Requirements:
            1. Personalized Itinerary for {mbti_type}
               - Align activities with {mbti_type} personality traits
               - Balance structured and spontaneous experiences

            2. Daily Breakdown
               - Morning activities
               - Lunch and dining recommendations
               - Afternoon explorations
               - Dinner suggestions
               - Evening entertainment

            3. Transportation
               - Recommended transit options
               - Estimated travel times
               - Transportation budget estimates

            4. Accommodation
               - {accommodation_type} recommendations
               - Estimated nightly costs
               - Proximity to key attractions

            5. Budget Considerations
               - Estimated daily expenses
               - Breakdown by category (lodging, food, activities, transport)
               - Options for budget optimization

            6. Additional Considerations
               - Must-See Attractions: {must_see_attractions or 'None specified'}
               - Food Preferences/Restrictions: {food_preferences or 'None specified'}

            7. Unique Experiences
               - Local hidden gems
               - Cultural insights
               - Experiences tailored to {mbti_type}

            Output Format:
            - Markdown with clear sections
            - Engaging and informative
            - Include estimated timings and costs
            - Provide practical travel tips
            - Include related websites URL for places if possible
            """

            # Use system instructions to further guide the AI
            instructions = f"""
            You are an expert travel planner specializing in personalized, detailed itineraries.
            Focus on creating a comprehensive, engaging plan that considers:
            - Traveler's personality type
            - Budget constraints
            - Personal preferences
            - Unique local experiences
            Provide actionable, specific recommendations.
            """

            # Generate the travel plan using the AI
            response = self.generate_text(
                prompt, 
                instructions=instructions, 
                model="gpt-4", 
                temperature=0.7
            )

            # Prepare the travel plan dictionary
            travel_plan = {
                "mbti_type": mbti_type,
                "destination": f"{city}, {country}",
                "duration": duration,
                "plan_markdown": response,
                "plan_html": markdown.markdown(response)
            }

            return travel_plan

        except Exception as e:
            # Error handling with a fallback plan
            print(f"Error creating detailed travel plan: {str(e)}")
            fallback_plan = f"""
            # Travel Plan for {mbti_type} in {city}, {country}

            ## Overview
            Unfortunately, a detailed plan could not be generated at this time.

            ### Recommendations
            - Conduct further research about {city}
            - Consult local travel guides
            - Remain flexible in your travel plans

            **Apologies for the inconvenience**
            """

            return {
                "mbti_type": mbti_type,
                "destination": f"{city}, {country}",
                "duration": duration,
                "plan_markdown": fallback_plan,
                "plan_html": markdown.markdown(fallback_plan)
            }

    def generate_travel_recommendations(self, preferences, mbti_type):
        try:
            prompt = f"""
            Based on the following preferences and MBTI type, create a high-level travel plan:
            MBTI Type: {mbti_type}
            Preferences:
            - Country: {preferences.get('country', '')}
            - City: {preferences.get('city', '')}
            - Travel Style: {', '.join(preferences.get('travel_style', []))}
            - Food Preferences: {preferences.get('food_preferences', '')}
            - Must-See Attractions: {preferences.get('must_see_attractions', '')}
            Create JSON output with:
            - tourist_attractions
            - recommended_neighborhoods
            - restaurants
            - hidden_experiences
            """

            instructions = "You are a professional travel advisor. Output only JSON."

            response = self.generate_text(prompt, instructions=instructions, output_type="json_object", model="gpt-4", temperature=0.7)

            if isinstance(response, str):
                response = json.loads(response)

            return response

        except Exception as e:
            print(f"Error generating travel recommendations: {str(e)}")
            return {}

    def generate_daily_itinerary(self, day_number, date, preferences, selected_options):
        try:
            selected_summary = "\n".join([f"- {opt['type']}: {opt['selected']}" for opt in selected_options])

            prompt = f"""
            Create a detailed Day {day_number} itinerary for {date.strftime('%A, %B %d')}:
            Selected options:
            {selected_summary}
            City: {preferences.get('city', '')}
            Travel Style: {', '.join(preferences.get('travel_style', []))}
            Structure:
            - Morning: 2-3 activities
            - Afternoon: 2-3 activities
            - Evening: 1-2 activities
            - Creative day theme
            - End with a fun motivational note
            Output JSON: theme, morning, afternoon, evening, notes
            """

            instructions = "You are a travel itinerary planner. Only output valid JSON."

            response = self.generate_text(prompt, instructions=instructions, output_type="json_object", model="gpt-4", temperature=0.7)

            if isinstance(response, str):
                response = json.loads(response)

            return response

        except Exception as e:
            print(f"Error generating daily itinerary: {str(e)}")
            return {
                "theme": "Exploration Day",
                "morning": [],
                "afternoon": [],
                "evening": [],
                "notes": "Enjoy your day!"
            }
        
    def generate_image(self, prompt, size="1024x1024", quality="standard", n=1):
        """
        Generates an image using DALL-E 3 based on the given prompt.
        
        Parameters:
        ----------
        prompt : str
            Text description for the image to generate.
        size : str
            Size of the generated image (e.g., "1024x1024", "1792x1024", "1024x1792").
        quality : str
            Quality of the generated image ("standard" or "hd").
        n : int
            Number of images to generate.
            
        Returns:
        -------
        str
            URL of the generated image.
        """
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            # Return the image URL
            return response.data[0].url
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None