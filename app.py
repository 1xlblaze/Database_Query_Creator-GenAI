import streamlit as st
import os
import json
import google.generativeai as genai

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except ImportError:
    st.error("Please install python-dotenv: pip install python-dotenv")
    st.stop()
except Exception as e:
    st.error(f"Error loading API key: {e}")
    st.stop()


def get_gemini_response(prompt):
    """Generate a response using the Gemini model."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt])

        # Return the response text directly, ensuring it's properly handled
        return response.text.strip() if hasattr(response, 'text') else "Error: Unexpected response format from Gemini."
    except Exception as e:
        return f"Error from Gemini: {e}"


def load_schema(filepath="schema.json"):
    """Load the database schema from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def build_initial_prompt(schema, user_question):
    """
    Construct an initial prompt with schema details and specific instructions.
    The prompt gives structured guidance to Gemini for better SQL generation.
    """
    schema_description = json.dumps(schema, indent=2)
    prompt = f"""
You are an expert SQL query generator. I will provide you with a database schema and a user query. Use the schema to generate the most appropriate SQL query.

Dataset Schema:
{schema_description}

User Query: "{user_question}"

Instructions:
1. Use only the columns and tables provided in the schema. Do not assume the existence of additional data or relationships.
2. If the query is ambiguous or lacks clarity, ask for more specific details instead of guessing.
3. Ensure the SQL query is syntactically correct and optimized (e.g., use indexes, minimize unnecessary joins).
4. Include a `LIMIT 100` clause for large datasets, unless specified otherwise.
5. Avoid `SELECT *`; always specify columns.
6. Validate that all table names and column names match those in the schema.
"""
    return prompt


def build_refinement_prompt(query, schema, error_message=None):
    """
    Build a prompt for refining the query, including the previous query and any errors.
    """
    schema_description = json.dumps(schema, indent=2)
    
    base_prompt = f"""
You are an expert SQL query generator. Below is a database schema and a previous SQL query with errors.

Dataset Schema:
{schema_description}

Previous SQL Query:
{query}

Instructions:
1. Correct the SQL query based on the schema. Ensure all tables and columns are valid.
2. Ensure correct SQL syntax and optimize the query (e.g., use indexes, minimize unnecessary joins).
3. Include a `LIMIT 100` clause for large datasets unless specified otherwise.
4. Avoid `SELECT *`; always specify columns.
"""

    if error_message:
        # If there's an error message, include that in the prompt for more targeted refinement
        base_prompt += f"\nError in the query: {error_message}\nPlease correct the query accordingly."
    
    return base_prompt


def iterative_refinement(query, schema):
    """
    Use Gemini in a feedback loop to iteratively refine the SQL query.
    """
    refined_query = query
    error_message = None
    
    iterations = 0
    max_iterations = 5  # Set a limit to avoid infinite loops
    
    while iterations < max_iterations:
        iterations += 1
        
        # Validate using Gemini's own schema compliance based on errors in previous iteration
        prompt = build_refinement_prompt(refined_query, schema, error_message)
        refined_query = get_gemini_response(prompt)
        
        # Check if the query still has errors; if yes, refine further
        if "error" in refined_query.lower():
            error_message = refined_query
        else:
            break  # Exit the loop if query is valid

    return refined_query


# Load the schema and check if it's available
schema = load_schema()
if schema is None:
    st.error("Error loading schema.json. Please ensure the file exists and is valid JSON.")
    st.stop()

st.set_page_config(page_title="Intelligent SQL Query Generator", page_icon=":robot:")
st.title("Gemini-powered SQL Query Generator with Dynamic Interaction")

# User Input Section
user_question = st.text_input("Ask your question in natural language:", key="input", placeholder="e.g., Show me the list of users from India")

# Generate the SQL query
submit = st.button("Generate SQL")

if submit:
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        # Build the initial prompt for Gemini using the schema and user's question
        prompt = build_initial_prompt(schema, user_question)
        response = get_gemini_response(prompt)

        st.subheader("Response from Gemini:")
        if "Error" in response:
            st.error(response)  # Display Gemini errors
        else:
            st.text(response)

            # Validate and optimize the query using iterative refinement
            refined_query = iterative_refinement(response, schema)

            # Check if Gemini's response contains questions for the user
            if "?" in refined_query:  # Assuming questions will have a "?" character
                st.warning("Gemini requires more information to refine the SQL query.")
                follow_up_answer = st.text_input("Answer Gemini's question to provide more details:")

                if st.button("Submit Details"):
                    refined_prompt = f"{prompt}\nAdditional User Details: {follow_up_answer}"
                    refined_response = get_gemini_response(refined_prompt)
                    st.subheader("Refined SQL Query:")
                    st.code(refined_response, language="sql")
            else:
                st.success("SQL query generated successfully!")
                st.code(refined_query, language="sql")
