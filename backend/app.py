import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# TODO: Uncomment and configure when integrating real Gemini API
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

MEMORY_FILE = "memory.json"

# --- Helper Functions ---

def read_memory():
    """Reads data from the memory file."""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                content = f.read()
                if not content:
                    return {} # Return empty dict if file is empty
                return json.loads(content)
        else:
            return {} # Return empty dict if file doesn't exist
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading memory file: {e}")
        return {} # Return empty dict on error

def write_memory(data):
    """Writes data to the memory file."""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error writing memory file: {e}")

# --- AI Simulation ---

def call_gemini_api(prompt):
    """
    Calls the actual Google Gemini API.
    Replace this with actual API calls when ready.
    """
    print("\n--- Calling Real Gemini API ---")
    print(f"PROMPT:\n{prompt}")
    print("------------------------------\n")

    ### START AI API CALL PLACEHOLDER ###
    # TODO: Integrate Google Gemini API here
    try:
        # 1. Configure the API key (ideally loaded securely)
        api_key = "AIzaSyAXjhxNabbFpclHXc6FAnBBcESt0fo5LbU"
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment variables.")
            # Handle error appropriately, maybe return a default error JSON
            # Return JSON string directly, as the caller expects a string
            return json.dumps({"status": "error", "message": "API key not configured"})
        genai.configure(api_key=api_key)

        # 2. Create a GenerativeModel instance
        # Using gemini-1.5-flash-latest as requested
        model = genai.GenerativeModel('gemini-2.0-flash')

        # 3. Generate content
        response = model.generate_content(prompt)

        # --- Response Cleaning (Crucial!) ---
        # Remove potential markdown backticks and 'json' identifier
        cleaned_text = response.text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:].strip() # Remove ```json and surrounding whitespace
        elif cleaned_text.startswith('```'): # Handle case where it might just start with ```
             cleaned_text = cleaned_text[3:].strip()
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3].strip() # Remove ``` and surrounding whitespace

        # Assuming the response contains the JSON string directly in response.text
        # You might need to adjust parsing based on the actual Gemini response structure
        # Return the cleaned string, let the endpoint handle JSON parsing
        print(f"RAW AI RESPONSE (Cleaned):\n{cleaned_text}")
        return cleaned_text

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Return an error JSON string that the calling function can parse
        return json.dumps({"status": "error", "message": f"AI API call failed: {e}"})

    # --- Simulation Logic (REMOVE THIS BLOCK WHEN INTEGRATING REAL API) ---
    # simulated_response_json_string = "{}" # Default empty JSON
    #
    # if "Analyze the input" in prompt:
    #     # Simulate response for /api/analyze_form
    #     # ... (simulation code removed) ...
    # elif "generate exactly 3 learning paths" in prompt:
    #     # Simulate response for /api/get_learning_paths
    #     # ... (simulation code removed) ...
    # elif "VERY FIRST learning item" in prompt:
    #      # Simulate response for /api/start_quiz
    #     # ... (simulation code removed) ...
    # elif "Analyze the user's answer" in prompt:
    #     # Simulate response for /api/submit_answer (always ends session for MVP)
    #     # ... (simulation code removed) ...
    # --- End Simulation Logic ---

    ### END AI API CALL PLACEHOLDER ###

    # print(f"SIMULATED RESPONSE:\n{simulated_response_json_string}")
    # return simulated_response_json_string

# --- API Endpoints ---

@app.route('/api/analyze_form', methods=['POST'])
def analyze_form():
    """Agent 1: Analyzes the user's profile form."""
    try:
        form_data = request.get_json()
        if not form_data:
            return jsonify({"status": "error", "message": "No form data received."}), 400

        # Basic validation (can be expanded)
        required_fields = ['goal', 'familiarity', 'styles', 'time_available']
        if not all(field in form_data for field in required_fields):
             return jsonify({"status": "error", "message": "Missing required form fields."}), 400

        memory = read_memory()
        memory['form_data'] = form_data # Store raw form data
        write_memory(memory)

        # Construct prompt for AI analysis
        prompt = f"""
        Analyze the input user profile data and generate a structured summary.
        Input Data:
        Learning Goal: {form_data.get('goal')}
        Current Familiarity: {form_data.get('familiarity')}
        Preferred Learning Styles: {', '.join(form_data.get('styles', []))}
        Available Time: {form_data.get('time_available')}
        Specific Focus (Optional): {form_data.get('specific_focus', 'None')}

        Output a JSON object with the following keys:
        - goal: The user's learning goal.
        - level: The user's familiarity level.
        - preferred_styles: A list of the user's preferred learning styles.
        - session_duration_category: The user's available time category.
        - specific_focus: The user's specific focus, or null if not provided.
        - user_summary: A brief natural language summary of the user's profile.
        """

        simulated_response_str = call_gemini_api(prompt)
        # --- EDIT: Added error check for API call failure ---
        try:
            # Attempt to parse the response from call_gemini_api
            analysis_dict = json.loads(simulated_response_str)
            # Check if the AI returned an error structure itself
            if isinstance(analysis_dict, dict) and analysis_dict.get("status") == "error":
                 print(f"AI API returned an error: {analysis_dict.get('message')}")
                 # Propagate the error message from the AI call
                 return jsonify({"status": "error", "message": analysis_dict.get('message', 'AI processing error')}), 500
        except json.JSONDecodeError:
            print(f"Error decoding AI JSON response for analyze_form. Raw response: {simulated_response_str}")
            return jsonify({"status": "error", "message": "Failed to parse AI response (analyze_form)."}), 500
        # --- End EDIT ---

        # Store the analysis result
        memory = read_memory() # Re-read memory in case it changed
        memory['analysis'] = analysis_dict
        write_memory(memory)

        return jsonify({"status": "success", "message": "Form analyzed.", "analysis": analysis_dict})

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON data received."}), 400
    except Exception as e:
        print(f"Error in /api/analyze_form: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/api/get_learning_paths', methods=['GET'])
def get_learning_paths():
    """Agent 2 - Part 1: Generates learning paths based on analysis."""
    try:
        memory = read_memory()
        analysis = memory.get('analysis')

        if not analysis:
            return jsonify({"status": "error", "message": "User analysis not found. Please submit the form first."}), 404

        # Construct prompt for path generation
        prompt = f"""
        Based on the following user profile analysis, generate exactly 3 distinct learning path options suitable for a short session ({analysis.get('session_duration_category', 'approx 15-30 mins')}).

        User Profile Analysis:
        {json.dumps(analysis, indent=2)}

        Focus on the user's goal: "{analysis.get('goal')}" and level: "{analysis.get('level')}".
        Consider preferred styles: {', '.join(analysis.get('preferred_styles', []))}.
        If a specific focus exists ({analysis.get('specific_focus')}), incorporate it into at least one path.

        Output a JSON array where each element is an object with these keys:
        - name: A short, descriptive name for the path (e.g., "Core Concepts Review", "Practical Example Task").
        - duration: An estimated duration string (e.g., "Approx. 15 mins").
        - overview: A brief (1-2 sentence) overview of what the path covers.
        """

        simulated_response_str = call_gemini_api(prompt)
        # --- EDIT: Added error check for API call failure ---
        try:
            path_list = json.loads(simulated_response_str) # Parse the JSON string from AI
            # Check if the AI returned an error structure itself (less likely for a list, but good practice)
            if isinstance(path_list, dict) and path_list.get("status") == "error":
                 print(f"AI API returned an error: {path_list.get('message')}")
                 return jsonify({"status": "error", "message": path_list.get('message', 'AI processing error')}), 500
            # Basic validation that we got a list
            if not isinstance(path_list, list):
                print(f"AI response for paths was not a list. Raw response: {simulated_response_str}")
                raise json.JSONDecodeError("AI response was not a list", simulated_response_str, 0)

        except json.JSONDecodeError:
             # This might happen if the simulated response is malformed OR if the real AI response isn't valid JSON
            print(f"Error decoding AI JSON response for paths. Raw response: {simulated_response_str}")
            return jsonify({"status": "error", "message": "Failed to parse AI response (get_learning_paths)."}), 500
        # --- End EDIT ---

        # No need to store paths in memory for this simple MVP flow

        return jsonify({"status": "success", "paths": path_list})

    except json.JSONDecodeError:
         # This might happen if the simulated response is malformed
        print(f"Error decoding simulated JSON for paths.")
        return jsonify({"status": "error", "message": "Error generating learning paths."}), 500
    except Exception as e:
        print(f"Error in /api/get_learning_paths: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/api/start_quiz', methods=['POST'])
def start_quiz():
    """Agent 2 - Part 2a: Starts the interaction based on chosen path."""
    try:
        data = request.get_json()
        chosen_path_name = data.get('chosen_path_name')

        if not chosen_path_name:
            return jsonify({"status": "error", "message": "No path name provided."}), 400

        memory = read_memory()
        analysis = memory.get('analysis')

        if not analysis:
            return jsonify({"status": "error", "message": "User analysis not found. Please submit the form first."}), 404

        memory['chosen_path'] = chosen_path_name
        write_memory(memory)

        # Construct prompt for the first interaction item
        prompt = f"""
        The user has provided their profile analysis and chosen a learning path.
        Generate the VERY FIRST learning item (material and a question) for an interactive session.

        User Profile Analysis:
        {json.dumps(analysis, indent=2)}

        Chosen Learning Path: "{chosen_path_name}"

        Keep the material concise and the question engaging, suitable for the user's level ({analysis.get('level')}).
        The goal is to start the learning process based on the chosen path.

        Output a JSON object with the following keys:
        - material: A string containing the initial learning material (text, explanation, concept).
        - question_for_user: A string containing a question for the user to answer based on the material.
        - session_finished: A boolean, set to false for this initial step.
        """

        simulated_response_str = call_gemini_api(prompt)
        # --- EDIT: Added error check for API call failure ---
        try:
            interaction_dict = json.loads(simulated_response_str) # Parse the JSON string from AI
            # Check if the AI returned an error structure itself
            if isinstance(interaction_dict, dict) and interaction_dict.get("status") == "error":
                 print(f"AI API returned an error: {interaction_dict.get('message')}")
                 return jsonify({"status": "error", "message": interaction_dict.get('message', 'AI processing error')}), 500
        except json.JSONDecodeError:
            print(f"Error decoding AI JSON response for quiz start. Raw response: {simulated_response_str}")
            return jsonify({"status": "error", "message": "Failed to parse AI response (start_quiz)."}), 500
        # --- End EDIT ---

        # Store the current interaction state
        memory = read_memory() # Re-read
        memory['current_interaction'] = interaction_dict
        write_memory(memory)

        return jsonify({"status": "success", "interaction": interaction_dict})

    except json.JSONDecodeError:
        print(f"Error decoding simulated JSON for quiz start.")
        return jsonify({"status": "error", "message": "Error starting interaction."}), 500
    except Exception as e:
        print(f"Error in /api/start_quiz: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Agent 2 - Part 2b: Processes user answer and provides feedback/next step."""
    try:
        data = request.get_json()
        user_answer = data.get('answer')

        if user_answer is None: # Allow empty string answers, but not missing key
            return jsonify({"status": "error", "message": "No answer provided."}), 400

        memory = read_memory()
        analysis = memory.get('analysis')
        chosen_path = memory.get('chosen_path')
        current_interaction = memory.get('current_interaction')

        if not all([analysis, chosen_path, current_interaction]):
            return jsonify({"status": "error", "message": "Session context not found. Please start over."}), 404

        # Construct prompt for feedback/next step
        prompt = f"""
        Analyze the user's answer in the context of the ongoing learning session and provide the next step or conclude the session.

        User Profile Analysis:
        {json.dumps(analysis, indent=2)}

        Chosen Learning Path: "{chosen_path}"

        Previous Interaction Step:
        Material Presented: {current_interaction.get('material')}
        Question Asked: {current_interaction.get('question_for_user')}

        User's Answer: "{user_answer}"

        For this MVP simulation: Always conclude the session after the first answer.
        Provide a brief summary acknowledging their participation.

        Output a JSON object with the following keys:
        - material: null (since session is ending)
        - question_for_user: null (since session is ending)
        - session_finished: boolean, set to true.
        - summary: A brief concluding summary string for the user.
        """

        simulated_response_str = call_gemini_api(prompt)
        # --- EDIT: Added error check for API call failure ---
        try:
            next_step_dict = json.loads(simulated_response_str) # Parse the JSON string from AI
             # Check if the AI returned an error structure itself
            if isinstance(next_step_dict, dict) and next_step_dict.get("status") == "error":
                 print(f"AI API returned an error: {next_step_dict.get('message')}")
                 return jsonify({"status": "error", "message": next_step_dict.get('message', 'AI processing error')}), 500
        except json.JSONDecodeError:
            print(f"Error decoding AI JSON response for answer submission. Raw response: {simulated_response_str}")
            return jsonify({"status": "error", "message": "Failed to parse AI response (submit_answer)."}), 500
        # --- End EDIT ---

        # Update memory
        memory = read_memory() # Re-read
        memory['current_interaction'] = next_step_dict # Update interaction state
        if next_step_dict.get('session_finished'):
            memory['final_summary'] = next_step_dict.get('summary')
        write_memory(memory)

        return jsonify({"status": "success", "interaction": next_step_dict})

    except json.JSONDecodeError:
        print(f"Error decoding simulated JSON for answer submission.")
        return jsonify({"status": "error", "message": "Error processing answer."}), 500
    except Exception as e:
        print(f"Error in /api/submit_answer: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

# --- Initialization and Run ---

if __name__ == '__main__':
    # Ensure memory file exists
    if not os.path.exists(MEMORY_FILE):
        write_memory({}) # Create an empty JSON file if it doesn't exist

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True) # Debug=True for development