import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import firestore

# Load environment variables from .env file
load_dotenv()

# --- Firestore Client Initialization ---
# Use Application Default Credentials (ADC) which Cloud Run provides automatically.
# For local development, ensure you've run `gcloud auth application-default login`
# or set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
try:
    db = firestore.Client()
    # For this MVP, we'll use a fixed document ID. In a real app, this
    # would likely be tied to a user ID or session ID.
    SESSION_COLLECTION = "user_sessions" # Name of the Firestore collection
    SESSION_DOC_ID = "default_user_session" # Fixed document ID for MVP
except Exception as e:
    print(f"FATAL: Failed to initialize Firestore client: {e}")
    print("Ensure Application Default Credentials (ADC) are set up or GOOGLE_APPLICATION_CREDENTIALS env var points to a valid service account key.")
    # Depending on requirements, you might exit or handle this differently.
    # For now, the app might fail later if 'db' is None.
    db = None

app = Flask(__name__, static_folder='frontend_build', static_url_path='')
CORS(app)  # Enable CORS for all routes

# MEMORY_FILE = "memory.json" # <-- No longer needed

# --- Helper Functions (Updated for Firestore) ---

def read_memory():
    """Reads session data from a Firestore document."""
    if not db:
        print("Error: Firestore client not initialized.")
        return {}
    try:
        doc_ref = db.collection(SESSION_COLLECTION).document(SESSION_DOC_ID)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"Firestore document '{SESSION_DOC_ID}' not found in collection '{SESSION_COLLECTION}'. Returning empty state.")
            return {} # Return empty dict if document doesn't exist
    except Exception as e:
        print(f"Error reading memory from Firestore: {e}")
        return {} # Return empty dict on error

def write_memory(data):
    """Writes session data to a Firestore document."""
    if not db:
        print("Error: Firestore client not initialized. Cannot write memory.")
        return
    try:
        doc_ref = db.collection(SESSION_COLLECTION).document(SESSION_DOC_ID)
        # Use set with merge=True to create or update the document
        # without overwriting fields not present in the 'data' dict.
        doc_ref.set(data, merge=True)
    except Exception as e:
        print(f"Error writing memory to Firestore: {e}")

# --- AI Simulation (Keep API Key handling from previous step) ---

def call_gemini_api(prompt):
    """
    Calls the actual Google Gemini API using API key from environment variable.
    """
    print("\n--- Calling Real Gemini API ---")
    print(f"PROMPT:\n{prompt}")
    print("------------------------------\n")

    try:
        # 1. Configure the API key (Load securely from environment)
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment variables.")
            return json.dumps({"status": "error", "message": "API key not configured"})
        genai.configure(api_key=api_key)

        # 2. Create a GenerativeModel instance
        # Consider 'gemini-1.5-flash-latest' or 'gemini-1.5-pro-latest'
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 3. Generate content
        response = model.generate_content(prompt)

        # --- Response Cleaning ---
        cleaned_text = response.text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:].strip()
        elif cleaned_text.startswith('```'):
             cleaned_text = cleaned_text[3:].strip()
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3].strip()

        print(f"RAW AI RESPONSE (Cleaned):\n{cleaned_text}")
        return cleaned_text

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return json.dumps({"status": "error", "message": f"AI API call failed: {e}"})

# --- API Endpoints (No changes needed inside endpoints, they use read/write_memory) ---

@app.route('/api/analyze_form', methods=['POST'])
def analyze_form():
    """Agent 1: Analyzes the initial user form and stores analysis."""
    try:
        data = request.get_json()
        print("Received form data:", data) # Debugging: Print received data

        # --- Extract all fields from the request ---
        goal = data.get('goal')
        familiarity = data.get('familiarity')
        styles = data.get('styles')
        time_available = data.get('timeAvailable') # Frontend sends camelCase
        specific_focus = data.get('specificFocus')
        achieve_goal = data.get('achieveGoal') # Frontend sends camelCase
        session_scope = data.get('sessionScope') # Frontend sends camelCase

        # Basic validation (can be expanded)
        if not all([goal, familiarity, styles, time_available, achieve_goal, session_scope]):
             # Check if styles is an empty list, which is valid if user selected none (though form requires one)
             if not styles and isinstance(styles, list):
                 pass # Allow empty list for styles if validation changes later
             else:
                print("Validation failed. Missing fields:", {
                    "goal": goal, "familiarity": familiarity, "styles": styles,
                    "timeAvailable": time_available, "achieveGoal": achieve_goal,
                    "sessionScope": session_scope
                })
                # Be more specific about missing fields in the error message
                missing = [k for k, v in {
                    "goal": goal, "familiarity": familiarity, "styles": styles,
                    "timeAvailable": time_available, "achieveGoal": achieve_goal,
                    "sessionScope": session_scope
                }.items() if not v and not (k == 'styles' and isinstance(v, list))] # Check for falsy values, except empty list for styles
                return jsonify({"status": "error", "message": f"Missing required form fields: {', '.join(missing)}"}), 400


        # --- Construct the analysis object ---
        # This is the object that will be stored in memory (Firestore)
        analysis = {
            "learning_goal": goal,
            "familiarity_level": familiarity,
            "preferred_styles": styles,
            "time_available_per_session": time_available,
            "specific_focus_notes": specific_focus or "None", # Handle optional field
            "immediate_achievement_goal": achieve_goal, # Store the new field
            "desired_session_scope": session_scope # Store the new field
        }

        # --- AI Call (Optional for this step, but could be used for deeper analysis) ---
        # ... (optional AI call logic remains the same) ...

        # --- Store analysis in memory (Firestore) ---
        # Prepare the data to write: only the analysis, clearing old state.
        # Firestore's set(merge=True) handles overwriting/creating fields.
        # We want to ensure old path/interaction data is explicitly removed.
        memory_to_write = {
            'analysis': analysis,
            'chosen_path': firestore.DELETE_FIELD, # Explicitly delete old fields
            'current_interaction': firestore.DELETE_FIELD,
            'final_summary': firestore.DELETE_FIELD
        }
        write_memory(memory_to_write) # This now writes to Firestore

        print("Analysis stored in Firestore:", analysis) # Debugging

        return jsonify({"status": "success", "message": "Form analyzed successfully."})

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON data received."}), 400
    except Exception as e:
        print(f"Error in /api/analyze_form: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An internal server error occurred during form analysis."}), 500

@app.route('/api/get_learning_paths', methods=['GET'])
def get_learning_paths():
    """Agent 2 - Part 1: Generates learning paths based on analysis."""
    try:
        memory = read_memory() # Reads from Firestore now
        analysis = memory.get('analysis')

        if not analysis:
            return jsonify({"status": "error", "message": "User analysis not found. Please submit the form first."}), 404

        # Construct prompt for path generation
        prompt = f"""
        Based on the following user profile analysis, generate exactly 3 distinct learning path options suitable for a short session ({analysis.get('session_duration_category', 'approx 15-30 mins')}).

        User Profile Analysis:
        {json.dumps(analysis, indent=2)}

        Focus on the user's goal: "{analysis.get('learning_goal')}" and level: "{analysis.get('familiarity_level')}". # Corrected keys
        Consider preferred styles: {', '.join(analysis.get('preferred_styles', []))}.
        If a specific focus exists ({analysis.get('specific_focus_notes')}), incorporate it into at least one path. # Corrected key

        Output ONLY a valid JSON array where each element is an object with these keys:
        - name: A short, descriptive name for the path (e.g., "Core Concepts Review", "Practical Example Task").
        - duration: An estimated duration string (e.g., "Approx. 15 mins").
        - overview: A brief (1-2 sentence) overview of what the path covers.
        """

        ai_response_str = call_gemini_api(prompt)
        # --- Error check for API call failure ---
        try:
            path_list = json.loads(ai_response_str) # Parse the JSON string from AI
            if isinstance(path_list, dict) and path_list.get("status") == "error":
                 print(f"AI API returned an error: {path_list.get('message')}")
                 return jsonify({"status": "error", "message": path_list.get('message', 'AI processing error')}), 500
            if not isinstance(path_list, list):
                print(f"AI response for paths was not a list. Raw response: {ai_response_str}")
                raise json.JSONDecodeError("AI response was not a list", ai_response_str, 0)

        except json.JSONDecodeError:
            print(f"Error decoding AI JSON response for paths. Raw response: {ai_response_str}")
            return jsonify({"status": "error", "message": "Failed to parse AI response (get_learning_paths)."}), 500
        # --- End Error check ---

        # No need to store paths in memory (Firestore) for this simple MVP flow

        return jsonify({"status": "success", "paths": path_list})

    except Exception as e:
        print(f"Error in /api/get_learning_paths: {e}")
        import traceback
        traceback.print_exc() # Print stack trace for debugging
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/api/start_quiz', methods=['POST'])
def start_quiz():
    """Agent 2 - Part 2a: Starts the interaction based on chosen path."""
    try:
        data = request.get_json()
        chosen_path_name = data.get('chosen_path_name')

        if not chosen_path_name:
            return jsonify({"status": "error", "message": "No path name provided."}), 400

        memory = read_memory() # Reads from Firestore
        analysis = memory.get('analysis')

        if not analysis:
            return jsonify({"status": "error", "message": "User analysis not found. Please submit the form first."}), 404

        # Store chosen path in Firestore before making AI call
        write_memory({'chosen_path': chosen_path_name})

        # Construct prompt for the first interaction item
        prompt = f"""
        Your task is to help the user to upgrade their education process.
        You are a friendly and encouraging AI Learning Mentor, best ever possible on the earth which
        is combining all the learning methods and techniques to personalize education.
        Have in mind that the user is always a student and you are a mentor.

        The user has provided their profile analysis and chosen a learning path.
        Generate the VERY FIRST learning item (material and a question) for an interactive session.

        User Profile Analysis:
        {json.dumps(analysis, indent=2)}

        Chosen Learning Path: "{chosen_path_name}"

        Keep questions engaging, suitable for the user's level ({analysis.get('familiarity_level')}). # Corrected key
        The goal is to start the learning process based on the chosen path.

        Output ONLY a valid JSON object with the following keys:
        - material: A string containing the initial learning material (text, explanation, concept).
        - question_for_user: A string containing a question for the user to answer based on the material.
        - session_finished: A boolean, set to false for this initial step.
        - summary: null # Explicitly null for the first step
        """

        ai_response_str = call_gemini_api(prompt)
        # --- Error check for API call failure ---
        try:
            interaction_dict = json.loads(ai_response_str) # Parse the JSON string from AI
            if isinstance(interaction_dict, dict) and interaction_dict.get("status") == "error":
                 print(f"AI API returned an error: {interaction_dict.get('message')}")
                 return jsonify({"status": "error", "message": interaction_dict.get('message', 'AI processing error')}), 500
            # Basic validation
            if not all(k in interaction_dict for k in ["material", "question_for_user", "session_finished", "summary"]):
                 raise ValueError("AI response missing required keys for interaction.")
            if interaction_dict.get("session_finished") is not False:
                 print("Warning: AI set session_finished to true on the very first step. Forcing false.")
                 interaction_dict["session_finished"] = False # Ensure first step isn't finished
            if interaction_dict.get("summary") is not None:
                 print("Warning: AI provided a summary on the very first step. Forcing null.")
                 interaction_dict["summary"] = None # Ensure first step has no summary

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error decoding/validating AI JSON response for quiz start. Error: {e}. Raw response: {ai_response_str}")
            return jsonify({"status": "error", "message": f"Failed to parse or validate AI response ({type(e).__name__})."}), 500
        # --- End Error check ---

        # Store the current interaction state in Firestore
        memory_to_write = {'current_interaction': interaction_dict}
        write_memory(memory_to_write) # Writes to Firestore

        return jsonify({"status": "success", "interaction": interaction_dict})

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON data received in request."}), 400
    except Exception as e:
        print(f"Error in /api/start_quiz: {e}")
        import traceback
        traceback.print_exc() # Print stack trace for debugging
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """Agent 2 - Part 2b: Processes user answer and provides feedback/next step OR summary."""
    try:
        data = request.get_json()
        user_answer = data.get('answer')

        if user_answer is None: # Allow empty string answers, but not missing key
            return jsonify({"status": "error", "message": "No answer provided."}), 400

        memory = read_memory() # Reads from Firestore
        analysis = memory.get('analysis')
        chosen_path = memory.get('chosen_path')
        current_interaction = memory.get('current_interaction')

        if not all([analysis, chosen_path, current_interaction]):
            return jsonify({"status": "error", "message": "Session context not found. Please start over."}), 404

        # --- Updated Prompt Construction ---
        if user_answer == "SYSTEM_CONTINUE_SIGNAL":
            prompt = f"""
            The user previously reached a session summary point for the path "{chosen_path}" but wants to continue learning on the SAME path.
            Generate the NEXT logical learning item (material and question) based on their profile and the path.

            User Profile Analysis:
            {json.dumps(analysis, indent=2)}

            Chosen Learning Path: "{chosen_path}"

            Last Interaction (before summary):
            Material Presented: {current_interaction.get('material', 'N/A')}
            Question Asked: {current_interaction.get('question_for_user', 'N/A')}

            Task: Generate the next step. Keep material concise and question engaging.

            Output ONLY the required valid JSON object:
            {{
              "material": "...",
              "question_for_user": "...",
              "session_finished": false,
              "summary": null
            }}
            """
        else:
            prompt = f"""
You are an AI Tutor assessing a user's answer during a learning session.

User Profile Analysis:
{json.dumps(analysis, indent=2)}

Chosen Learning Path: "{chosen_path}"

Previous Interaction Step:
Material Presented: {current_interaction.get('material', 'N/A')}
Question Asked: {current_interaction.get('question_for_user', 'N/A')}

User's Latest Answer: "{user_answer}"

Task:
1. Analyze the user's answer based on the previous question, their profile (level: {analysis.get('familiarity_level')}), and the overall goal ('{analysis.get('learning_goal')}'). # Corrected keys
2. Decide if the session should continue with the next logical step in the "{chosen_path}" path OR if the session should end (e.g., the path's objective for this short session is met, user seems stuck, user indicates wanting to stop).
3. Generate a JSON response based on your decision:
   - If CONTINUING: Set 'session_finished' to false. Provide the NEXT piece of 'material' and 'question_for_user'. Set 'summary' to null.
   - If ENDING: Set 'session_finished' to true. Set 'material' and 'question_for_user' to null. Provide a 'summary' which MUST be a JSON object containing:
     - recap: (string) Brief summary of what the user practiced/learned in this interaction block.
     - strengths: (string) Positive feedback or areas where the user did well.
     - areas_for_improvement: (string) Gentle suggestions on what to focus on next or areas that need more practice.
     - next_step_suggestion: (string) A suggestion for what the user could learn or do next time related to their main goal.
     - motivation: (string) A brief encouraging or motivational closing remark.

Output ONLY the required valid JSON object adhering to this structure:
{{
  "material": "..." or null,
  "question_for_user": "..." or null,
  "session_finished": boolean,
  "summary": {{ "recap": "...", "strengths": "...", "areas_for_improvement": "...", "next_step_suggestion": "...", "motivation": "..." }} or null
}}
"""
        # --- End Updated Prompt Construction ---

        ai_response_str = call_gemini_api(prompt)

        # --- Handling the AI Response ---
        try:
            next_step_dict = json.loads(ai_response_str)
            if isinstance(next_step_dict, dict) and next_step_dict.get("status") == "error":
                 print(f"AI API returned an error: {next_step_dict.get('message')}")
                 return jsonify({"status": "error", "message": next_step_dict.get('message', 'AI processing error')}), 500

            # Validate base structure
            if not all(k in next_step_dict for k in ["material", "question_for_user", "session_finished", "summary"]):
                 raise ValueError("AI response missing base keys.")

            # Validate summary structure IF session is finished
            if next_step_dict.get('session_finished') and next_step_dict.get('summary'):
                 summary_obj = next_step_dict['summary']
                 if not isinstance(summary_obj, dict) or not all(k in summary_obj for k in ["recap", "strengths", "areas_for_improvement", "next_step_suggestion", "motivation"]):
                     print(f"Warning: AI finished session but summary structure is incorrect. Raw summary: {summary_obj}")
                     # Fallback: Convert whatever summary we got into a simple string recap
                     next_step_dict['summary'] = {
                         "recap": str(summary_obj),
                         "strengths": "N/A",
                         "areas_for_improvement": "N/A",
                         "next_step_suggestion": "N/A",
                         "motivation": "Keep learning!"
                     }

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error decoding/validating AI JSON response for answer submission. Error: {e}. Raw response: {ai_response_str}")
            return jsonify({"status": "error", "message": f"Failed to parse or validate AI response ({type(e).__name__})."}), 500
        # --- End Handling the AI Response ---

        # Update memory (Firestore)
        memory_to_write = {'current_interaction': next_step_dict}
        # Store the structured summary separately if finished (optional, but can be useful)
        if next_step_dict.get('session_finished'):
            memory_to_write['final_summary'] = next_step_dict.get('summary')
        else:
            # Ensure final_summary field is removed if session is continuing
             memory_to_write['final_summary'] = firestore.DELETE_FIELD

        write_memory(memory_to_write) # Writes to Firestore

        # Return the full interaction object to the frontend
        return jsonify({"status": "success", "interaction": next_step_dict})

    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON data received in request."}), 400
    except Exception as e:
        print(f"Error in /api/submit_answer: {e}")
        import traceback
        traceback.print_exc() # Print stack trace for debugging
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serves the React app's index.html for any non-API path."""
    static_folder = app.static_folder # Should be 'frontend_build'
    index_path = os.path.join(static_folder, 'index.html')
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return app.send_static_file(path)
    elif os.path.exists(index_path):
        return app.send_static_file('index.html')
    else:
        return "Frontend not found!", 404

# --- Initialization and Run ---

if __name__ == '__main__':
    # No need to create local memory file anymore
    # if not os.path.exists(MEMORY_FILE):
    #     write_memory({})

    port = int(os.environ.get("PORT", 8080))
    # Debug=True is fine for local development run via `python app.py`
    # Gunicorn in Dockerfile will handle production settings (debug=False implicitly)
    print("Starting Flask app locally for development (use Gunicorn in production/Docker)")
    app.run(host='0.0.0.0', port=port, debug=True)