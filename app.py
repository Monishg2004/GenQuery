import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

database_path = 'Music.db' 
# Configure page settings
st.set_page_config(
    page_title="GenQuery 2.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main content background and padding */
    .main {
        background-color: #f9f9f9; /* Light gray for better contrast */
        padding: 2rem;
    }

    /* Sidebar styling */
    .css-1d391kg {
        padding: 2rem 1rem;
        background-color: #ffffff; /* White background for sidebar */
        color: #333333; /* Dark text for readability */
    }

    /* Heading styles */
    h1 {
        color: #1E88E5; /* Blue for headings */
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    h2 {
        color: #0277BD;
        font-size: 2rem !important;
    }
    h3 {
        color: #0288D1;
        font-size: 1.5rem !important;
    }

    /* Sidebar image positioning */
    .stSidebar > div:first-child {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .stSidebar img {
        max-width: 80%;
        border-radius: 10px;
    }

    /* Styling for cards */
    .stcard {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        color: #333333; /* Ensure readable text */
    }

    /* Buttons */
    .stButton > button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Feature cards for home page */
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #1E88E5;
    }

    /* Card Styling */
    .card {
        background-color: #ffffff; /* Light background for cards */
        color: #333333; /* Dark text for readability */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center;
        margin: 1rem 0;
    }

    .card:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        transform: scale(1.02);
    }

    .card img {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
    }

    /* Fix for full white content areas */
    .stMarkdown, .stDataFrame, .stCodeBlock {
        background-color: #ffffff; /* Ensure white background for markdown and code */
        color: #333333; /* Ensure dark text for readability */
    }

    /* Streamlit's default text areas */
    textarea {
        background-color: #f9f9f9; /* Light gray for contrast */
        color: #333333; /* Dark text */
    }

    /* Plotly chart background */
    .stPlotlyChart {
        background-color: #ffffff !important; /* Ensure white chart background */
    }
</style>

""", unsafe_allow_html=True)


def validate_db_file(file):
    """Validate if the uploaded file is a SQLite database"""
    try:
        conn = sqlite3.connect(file.name)
        cursor = conn.cursor()
        # Try to get table names to verify it's a valid SQLite database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        return True, tables
    except Exception as e:
        return False, str(e)

def get_table_schema(db_path):
    """Get schema information for all tables in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema_info[table_name] = [
            {"name": col[1], "type": col[2]} for col in columns
        ]
    
    conn.close()
    return schema_info

def handle_db_upload():
    """Handle database file upload and return relevant information"""
    st.write("### Upload Your Database")
    uploaded_file = st.file_uploader("Choose a SQLite database file", type=['db', 'sqlite', 'sqlite3'])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_db.db", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Validate the database
        is_valid, tables = validate_db_file(uploaded_file)
        
        if is_valid:
            schema_info = get_table_schema("temp_db.db")
            
            # Display database information
            st.success("Database successfully uploaded!")
            
            with st.expander("📚 Database Schema"):
                for table_name, columns in schema_info.items():
                    st.write(f"**Table: {table_name}**")
                    col_info = pd.DataFrame(columns)
                    st.dataframe(col_info)
            
            return "temp_db.db", schema_info
        else:
            st.error(f"Invalid database file: {tables}")
            return None, None
    
    return None, None

def configure():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel("gemini-pro")

def get_gemini_response(input_text, prompt_template):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt_template + "\n\n" + input_text)
    return response.text

def generate_sql_query(model, input_text):
    template = """
    Create a SQL query for the following request:
    {text}
    Return only the SQL query without any explanation or formatting.
    """
    formatted_template = template.format(text=input_text)
    response = model.generate_content(formatted_template)
    return response.text.strip()

def generate_expected_output(model, sql_query):
    template = """
    Show the expected output format for this SQL query:
    {query}
    Provide a sample table response without explanation.
    """
    formatted_template = template.format(query=sql_query)
    response = model.generate_content(formatted_template)
    return response.text.strip()

def generate_explanation(model, sql_query):
    template = """
    Explain this SQL query in simple terms:
    {query}
    """
    formatted_template = template.format(query=sql_query)
    response = model.generate_content(formatted_template)
    return response.text.strip()

def sql_formatter(model, sql_code):
    template = """
    Format this SQL code for better readability:
    {code}
    Return only the formatted SQL code.
    """
    formatted_template = template.format(code=sql_code)
    response = model.generate_content(formatted_template)
    return response.text.strip()

def query_explainer(model, sql_syntax):
    template = """
    Break down and explain each part of this SQL query:
    {syntax}
    Provide a detailed explanation of each clause and component.
    """
    formatted_template = template.format(syntax=sql_syntax)
    response = model.generate_content(formatted_template)
    return response.text.strip()

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def determine_chart_type(df):
    if len(df.columns) == 2:
        if df.dtypes[1] in ['int64', 'float64'] and len(df) > 1:
            return 'bar'
        elif df.dtypes[1] in ['int64', 'float64'] and len(df) <= 10:
            return 'pie'
    elif len(df.columns) >= 3 and df.dtypes[1] in ['int64', 'float64']:
        return 'line'
    return None

def generate_chart(df, chart_type):
    if chart_type == 'bar':
        fig = px.bar(df, x=df.columns[0], y=df.columns[1],
                     title=f"{df.columns[0]} vs. {df.columns[1]}",
                     template="plotly_white", color=df.columns[0])
    elif chart_type == 'pie':
        fig = px.pie(df, names=df.columns[0], values=df.columns[1],
                     title=f"Distribution of {df.columns[0]}",
                     template="plotly_white")
    elif chart_type == 'line':
        fig = px.line(df, x=df.columns[0], y=df.columns[1],
                     title=f"{df.columns[1]} Over {df.columns[0]}",
                     template="plotly_white", markers=True)
    else:
        st.write("No suitable chart type determined for this data.")
        return
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

def get_sql_query_from_response(response):
    """
    Extracts a valid SQL query from the response text.
    
    Parameters:
        response (str): The response text generated by the Gemini model.
    
    Returns:
        str: The extracted SQL query, or None if no valid SQL query is found.
    """
    try:
        # Remove any unnecessary text around the SQL query
        # Assuming the response is plain text with the SQL query
        sql_query = response.strip()
        
        # Validate that the response starts with common SQL keywords
        if sql_query.lower().startswith(("select", "insert", "update", "delete", "create", "drop")):
            return sql_query
        else:
            return None
    except Exception as e:
        st.error(f"Error extracting SQL query: {e}")
        return None

    # File upload section
def learning_data():
    st.title("Your Data & SQL Learning Resources")
    
    # SQL Learning Resources Section
    with st.expander("📚 SQL Learning Resources", expanded=True):
        st.markdown("""
        ### 🎥 Video Tutorials
        1. [SQL Tutorial for Beginners](https://www.youtube.com/watch?v=HXV3zeQKqGY) - freeCodeCamp (4 hours comprehensive course)
        2. [SQL for Data Analysis](https://www.youtube.com/watch?v=hhh6sYQxMM8) - Programming with Mosh
        3. [SQL Crash Course](https://www.youtube.com/watch?v=p3qvj9hO_Bo) - WebDevSimplified
        
        ### 📖 Learning Websites
        1. [W3Schools SQL Tutorial](https://www.w3schools.com/sql/) - Interactive tutorials with examples
        2. [SQLBolt](https://sqlbolt.com/) - Interactive SQL lessons
        3. [Mode SQL Tutorial](https://mode.com/sql-tutorial/) - Comprehensive SQL guide
        4. [PostgreSQL Tutorial](https://www.postgresqltutorial.com/) - PostgreSQL specific tutorials
        
        ### 📝 Practice Resources
        1. [LeetCode Database Problems](https://leetcode.com/study-plan/sql/)
        2. [HackerRank SQL Challenges](https://www.hackerrank.com/domains/sql)
        3. [SQLZoo](https://sqlzoo.net/) - Interactive SQL exercises
        
        ### 📑 Cheat Sheets
        1. [SQL Cheat Sheet PDF](https://learnsql.com/blog/sql-basics-cheat-sheet/)
        2. [PostgreSQL Cheat Sheet](https://www.postgresqltutorial.com/postgresql-cheat-sheet/)
        """)
    
   
    
  

def main():
    model = configure()

    # Sidebar navigation with label for accessibility
    with st.sidebar:
        st.image("Media\logo.jpg", width=150)
        st.title("Navigation")
        
        selected_page = st.radio(
            "Select a page",
            ['🏠 Home', '📝 SQL Generator', '✨ SQL Formatter', '🔍 Query Explainer', '📊 Data Analysis', '📁 Learning Resource'],
            label_visibility="collapsed"
        )
        
       
                
    if selected_page == '🏠 Home':
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h1>Welcome to GenQuery 2.0 🤖</h1>
                <p style='font-size: 1.2rem; color: #666;'>Your Intelligent SQL Assistant</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class='feature-card'>
                    <h3>📝 SQL Generator</h3>
                    <p>Transform natural language into precise SQL queries instantly.</p>
                </div>
                
                <div class='feature-card'>
                    <h3>✨ SQL Formatter</h3>
                    <p>Beautiful, consistent SQL formatting in one click.</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div class='feature-card'>
                    <h3>🔍 Query Explainer</h3>
                    <p>Understand complex queries with detailed breakdowns.</p>
                </div>
                
                <div class='feature-card'>
                    <h3>📊 Data Analysis</h3>
                    <p>Visualize your data with interactive charts.</p>
                </div>
            """, unsafe_allow_html=True)
            
    elif selected_page == '📁 Learning Resource':
        learning_data()
        

    elif selected_page == '📝 SQL Generator':
        st.markdown("<h1>SQL Query Generator</h1>", unsafe_allow_html=True)
        
        text_input = st.text_area(
            "Enter your query request",
            placeholder="Example: Show me the total sales by product category for the last quarter",
            height=100,
            label_visibility="visible"
        )
        
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            submit = st.button("Generate Query 🚀", use_container_width=True)

        if submit and text_input:
            with st.spinner("🔮 Generating your SQL query..."):
                sql_query = generate_sql_query(model, text_input)
                eoutput = generate_expected_output(model, sql_query)
                explanation = generate_explanation(model, sql_query)

            tab1, tab2, tab3 = st.tabs(["📜 SQL Query", "🎯 Expected Output", "📚 Explanation"])
            
            with tab1:
                st.code(sql_query, language="sql")
            with tab2:
                st.markdown(eoutput)
            with tab3:
                st.markdown(explanation)

    elif selected_page == '✨ SQL Formatter':
        st.markdown("<h1>SQL Formatter</h1>", unsafe_allow_html=True)
        
        sql_input = st.text_area(
            "Enter SQL code to format",
            placeholder="SELECT column_name FROM table_name WHERE condition;",
            height=200,
            label_visibility="visible"
        )
        
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            format_button = st.button("Format SQL ✨", use_container_width=True)

        if format_button and sql_input:
            with st.spinner("✨ Formatting your SQL..."):
                formatted_sql = sql_formatter(model, sql_input)
                st.code(formatted_sql, language='sql')

    elif selected_page == '🔍 Query Explainer':
        st.markdown("<h1>Query Explainer</h1>", unsafe_allow_html=True)
        
        sql_syntax = st.text_area(
            "Enter SQL query to explain",
            placeholder="SELECT * FROM users JOIN orders ON users.id = orders.user_id;",
            height=200,
            label_visibility="visible"
        )
        
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            explain_button = st.button("Explain Query 🔍", use_container_width=True)

        if explain_button and sql_syntax:
            with st.spinner("🔍 Analyzing your query..."):
                explanation = query_explainer(model, sql_syntax)
                st.markdown(explanation)

    elif selected_page == '📊 Data Analysis':
        st.markdown("<h1>Data Analysis & Visualization</h1>", unsafe_allow_html=True)
        
        with st.expander("📚 Resources"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Sample Database**")
                st.markdown("[Download Database](https://storage.googleapis.com/tidb_hack/Music.sql)")
            with col2:
                st.markdown("**ER Diagram**")
                st.markdown("[View ER Diagram](https://storage.googleapis.com/tidb_hack/ER-diagram.jpg)")

        with st.expander("💡 Sample Questions"):
            st.markdown("""
                1. Which top 5 artists have the most albums?
                2. How many total artists are there in the database?
                3. Which genres have the most tracks? Show with a bar chart.
            """)
        
        question = st.text_area(
            "Enter your analysis question",
            placeholder="Example: Show me the top 5 selling products",
            height=100,
            label_visibility="visible"
        )
        # Define the prompt template for data analysis
        prompt = """
        Imagine you're an SQL expert and data visualization advisor adept at translating English questions into precise SQL queries and recommending visualization types for a database named Chinook, which comprises several tables including Employees, Customers, Invoices, Invoice_Items, Artists, Albums, Media_Types, Genres, Tracks, Playlists, and Playlist_Track.

        Here are examples to guide your query generation:

        Example Question 1: "How many unique artists are there?"
        SQL Query: SELECT COUNT(DISTINCT name) FROM Artists;

        Example Question 2: "What are the total number of albums by each artist?"
        SQL Query: SELECT Artists.name, COUNT(Albums.AlbumId) AS total_albums 
        FROM Artists 
        JOIN Albums ON Artists.ArtistId = Albums.ArtistId 
        GROUP BY Artists.name;

        Please format your response with just the SQL query, without any additional text or formatting.
        """   
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            submit = st.button("Analyze Data 📊", use_container_width=True)
   
        if submit and question:
            with st.spinner("📊 Analyzing your data..."):
                response = get_gemini_response(question, prompt)
                sql_query = get_sql_query_from_response(response)

                if sql_query:
                    st.code(sql_query, language='sql')
                    df = read_sql_query(sql_query, database_path)

                    if not df.empty:
                        tab1, tab2 = st.tabs(["📊 Visualization", "📋 Data"])
                        
                        with tab1:
                            chart_type = determine_chart_type(df)
                            if chart_type:
                                generate_chart(df, chart_type)
                            
                        with tab2:
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.error("No results found for the given query.")
                else:
                    st.error("Could not generate a valid SQL query. Please try rephrasing your question.")

if __name__ == "__main__":
    main()