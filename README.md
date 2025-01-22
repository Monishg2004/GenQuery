# GenQuery - AI-Powered SQL Assistant🤖

GenQuery 2.0 is an intelligent SQL assistant that helps users write, format, and understand SQL queries using Google's Gemini AI. The application provides an intuitive interface for database interaction and SQL learning.

## 🌟 Features

- **SQL Query Generator**: Transform natural language into precise SQL queries.
- **SQL Formatter**: Beautify and format SQL code for better readability.
- **Query Explainer**: Get detailed explanations of SQL queries.
- **Data Analysis**: Visualize query results with interactive charts.
- **Learning Resources**: Access comprehensive SQL learning materials.

## 🔧 Technologies Used

- Streamlit
- Google Gemini AI
- SQLite3
- Pandas
- Plotly Express
- Python-dotenv

## 🗈 Prerequisites

- Python 3.7+
- Google API Key for Gemini AI
- SQLite database

## 🚀 Installation

1. Clone the repository:

```bash
https://github.com/Monishg2004/GenQuery.git
cd genquery
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Google API key:

```
GOOGLE_API_KEY=your_api_key_here
```

## 💻 Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Navigate to `http://localhost:8501` in your web browser.

3. Use the sidebar to access different features:

   - Home
   - SQL Generator
   - SQL Formatter
   - Query Explainer
   - Data Analysis
   - Learning Resources

## 📒 Sample Database

The application comes with a sample Music database. You can:

- Download the database from the provided link in the Data Analysis section.
- View the ER diagram to understand the database structure.
- Try sample questions provided in the interface.

## 📈 Future Enhancements

- Integration with cloud databases.
- Advanced charting options with Plotly.
- Export query results to CSV and Excel.
- AI-powered optimization suggestions for SQL queries.

##

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing.
- Streamlit for the web interface.
- SQLite for database management.
- Plotly for data visualization.

