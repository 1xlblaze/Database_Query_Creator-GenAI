import streamlit as st
import os
import json
import google.generativeai as genai
import psycopg2

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

# Database connection details
host = "34.100.240.197"
port = 5444
database = "hackathon"
user = "hackathon"
password = "hackathon2024"

refined = ""
initial = ""
query = ""
# Function to connect to the database
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


def build_refinement_prompt(query, schema, error_message=""):
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

Past error message: {error_message}
"""

    if error_message:
        # If there's an error message, include that in the prompt for more targeted refinement
        base_prompt += f"\nError in the query: {error_message}\nPlease correct the query accordingly."
    
    return base_prompt



def build_refinement_prompt_for_query_execution(query, schema, error_message="", user_training_question = ""):
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

User Requirement : {user_training_question}

Instructions:
1. Correct the SQL query based on the schema. Ensure all tables and columns are valid.
2. Ensure correct SQL syntax and optimize the query (e.g., use indexes, minimize unnecessary joins).
3. Include a `LIMIT 100` clause for large datasets unless specified otherwise.
4. Avoid `SELECT *`; always specify columns.

Past error message: {error_message}

Parameters:
Take sample values on the basis of schema {schema_description} in {query} with problem statement {user_training_question}
"""

    if error_message:
        # If there's an error message, include that in the prompt for more targeted refinement
        base_prompt += f"\nError in the query: {error_message}\nPlease correct the query accordingly."
    
    return base_prompt


def build_initial_prompt_for_query_execution(schema, user_question , user_training_question):
    """
    Construct an initial prompt with schema details and specific instructions.
    The prompt gives structured guidance to Gemini for better SQL generation.
    """
    schema_description = json.dumps(schema, indent=2)
    prompt = f"""
You are an expert SQL query generator. I will provide you with a database schema and a user query. Use the schema to generate the most appropriate SQL query.

Dataset Schema:
{schema_description}

Query: "{user_question}"
User Requirement : {user_training_question}

Instructions:
1. Use only the columns and tables provided in the schema. Do not assume the existence of additional data or relationships.
2. If the query is ambiguous or lacks clarity, ask for more specific details instead of guessing.
3. Ensure the SQL query is syntactically correct and optimized (e.g., use indexes, minimize unnecessary joins).
4. Include a `LIMIT 100` clause for large datasets, unless specified otherwise.
5. Avoid `SELECT *`; always specify columns.
6. Validate that all table names and column names match those in the schema.

Parameters:
Take sample values on the basis of {schema_description} in {user_question} as described with problem statement {user_training_question}
"""
    return prompt


def iterative_refinement(query, schema, error_message="" ,flag=0):
    """
    Use Gemini in a feedback loop to iteratively refine the SQL query.
    """
    refined_query = query
    #error_message = None
    
    iterations = 0
    max_iterations = 5  # Set a limit to avoid infinite loops
    
    while iterations < max_iterations:
        iterations += 1
        
        # Validate using Gemini's own schema compliance based on errors in previous iteration
        if flag == 1 :
            prompt = build_refinement_prompt_for_query_execution(refined_query, schema, error_message, user_training_question)
        else:
            prompt = build_refinement_prompt(refined_query, schema, error_message)
        refined_query = get_gemini_response(prompt)
        
        # Check if the query still has errors; if yes, refine further
        if "error" in refined_query.lower():
            error_message = refined_query
        else:
            break  # Exit the loop if query is valid
    
    return refined_query

def execute_query(connection, query):
    """Executes the given SQL query and returns the result."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return str(e)

def clean_query_for_execution(gemini_response):
    """
    Clean the query generated by Gemini and remove any SQL-related tags or formatting.
    """
    # Strip out any `sql` tags or unwanted formatting
    if gemini_response.startswith("```sql") and gemini_response.endswith("```"):
        gemini_response = gemini_response[6:-3].strip()  # Remove the ```sql and ending ```
    return gemini_response.strip()

# After generating the response from Gemini
#refined_query = get_gemini_response(prompt)



# Load the schema and check if it's available
schema = load_schema()
if schema is None:
    st.error("Error loading schema.json. Please ensure the file exists and is valid JSON.")
    st.stop()

st.set_page_config(page_title="PlutoAI", page_icon=":robot:")

# Pluto AI title with description and logo
st.markdown(
    """
    <div style='display: flex; align-items: center; justify-content: center;'>
        <img src='https://storage.googleapis.com/hackathon-pluto-ai-solution/logo%20pluto%20ai.png' alt='Pluto AI Logo' style='width: 50px; height: 50px; margin-right: 15px;'/>
        <div>
            <h1 style='margin: 0; padding: 0; font-size: 2.5em;'>Pluto AI</h1>
            <p style='font-size: 1.2em; margin-top: 5px;'>A Human Language to SQL Query Converter</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Gemini-powered SQL Query Generator with Dynamic Interaction")

# User Input Section
user_question = st.text_input("Ask your question in natural language:", key="input", placeholder="e.g., Show me the list of sample mcat ids")
user_training_question = user_question
# Generate the SQL query
submit = st.button("Generate SQL")
if submit:
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        # Build the initial prompt for Gemini using the schema and user's question
        prompt = build_initial_prompt(schema, user_question)
        response = get_gemini_response(prompt)
       
        response = clean_query_for_execution(response)
        initial = response
        st.session_state.initial = initial
        
        st.subheader("Initial Query (Query A)")
        if "Error" in response:
            st.error(response)  # Display Gemini errors
        else:
            st.code(response,language="sql")

            # Validate and optimize the query using iterative refinement
            # follow_up_answer = st.text_input("For iterative refinement on initial response, add your queries in detail:(optional)", key = "iterative_refinement")


            # sub = st.button("Generate after iterative refinement")
            # # Check if Gemini's response contains questions for the user
            # if sub:  # Assuming questions will have a "?" character
                #st.warning("Gemini requires more information to refine the SQL query.")
                #follow_up_answer = st.text_input("Answer Gemini's question to provide more details:")
            st.subheader("Refined SQL Query (Query B)")  # Debugging log
            refined_prompt = f"{prompt}\n"
            refined_query = iterative_refinement(response, schema)
            refined_response = get_gemini_response(refined_prompt)
            refined_query = clean_query_for_execution(refined_response)
            st.session_state.refined = refined_query
            refined = refined_response
            
            st.code(refined_query, language="sql")
            #st.success("SQL iterative query generated successfully!")
                
                # sub = st.button("Connect to Database and fetch query result")
                # if sub: 

# Database connection details
host = "34.100.240.197"
port = 5444
database = "hackathon"
user = "hackathon"
password = "hackathon2024"

# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        st.success("Connected to the database successfully!")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to the database: {e}")
        return None

# Streamlit UI


st.subheader("Connect to database for initial query execution")

# Connect to the database when the button is clicked
# if st.button("Connect to Database"):
#     try:
#         connection = connect_to_db()
#         if connection:
#             st.write("Connection object:", connection)
#             st.write("Executing query...")
#             query_results = execute_query(connection, query)
#             print(query)
#             if query_results:
#                 st.write("Query Results:")
#                 st.dataframe(query_results)  # Display results in a table
#     except Exception as e:
#         st.write(refined_query)
#         st.error(f"Error executing query: {e}")
user_choice = st.text_input("Choose query option: Enter '1' for Initial Query (Query A) or '2' for Refined Query (Query B). Default is Query A.")
submit =  st.button("Submit")
if submit:
    try:
        # Convert user input to integer
        user_choice = int(user_choice)
    except ValueError:
        st.error("Please enter 1 or 2")
        user_choice = 2
    retries = 0
    max_retries = 5
    success = False
    refined_query = None
    # response = any
    # prompt = build_initial_prompt_for_query_execution(schema, user_question)
    refined_query = st.session_state.initial if user_choice == 1 else st.session_state.refined
    st.write(user_training_question)
    #refined_query = refined
    if user_choice == 1: 
        st.code(st.session_state.initial, language="sql")
        #st.write(st.session_state.initial_query)

        prompt = build_initial_prompt_for_query_execution(schema , refined_query, user_training_question)
        refined_query = get_gemini_response(prompt)
        refined_query = clean_query_for_execution(refined_query)
        #refined_query = initial
    else:
        st.code(st.session_state.refined, language="sql")
        st.write(refined)
        prompt = build_refinement_prompt_for_query_execution(refined_query, schema , "", user_training_question)
        refined_query = get_gemini_response(prompt)
        refined_query = clean_query_for_execution(refined_query)
        #refined_query = refined
    st.write("executing query for sql result with database : your choosen one query with random values")
    st.code(refined_query, language = "sql")
    error_message= ""
    while retries < max_retries and not success:
        try:
            connection = connect_to_db()
            if connection:
                st.write("Connection object:", connection)
                st.write("Executing first query...")
                query_results = execute_query(connection, refined_query)
                print(query_results)
                if query_results:
                    st.write("Query Results:")
                    st.dataframe(query_results)  # Display results in a table
                    success = True  # Exit the loop on success
                else:
                    st.write("Query executed successfully but no results found.")
                    success = True  # Consider it a success and exit without retrying    
        except Exception as e:
            st.write(f"Error executing initial query: {e}")
            st.write("model doing iterative refinement with previous errors")
            error_message = error_message+str(e)
            # Trigger iterative refinement if there's an error
            #prompt = build_refinement_prompt(refined_query, schema, e)
            refined_query = iterative_refinement(refined_query,schema,error_message, 1)
            refined_query = clean_query_for_execution(refined_query)
            
            # Show the refined query and retry        try:

            st.write("Refined SQL Query:")
            st.code(refined_query, language="sql")
            retries += 1
            #refined_query = refined_query  # Update the query to the refined one

    if not success:
        st.error("Failed to execute the query after 5 attempts.")
