# Research Field Explorer 
Final Project for CS411-2024S

## Author
Runqi Liu

## Purpose
The Research Field Explorer is a web application designed to assist users in navigating their interested research fields using keywords. Its target users are undergrad students, grad students, and anyone interested in research and academia. The app provides various functionalities such as checking research trends, discovering top professors, exploring keywords related to universities and professors, and getting recommendations based on research interests.

## Demo Link
https://mediaspace.illinois.edu/media/t/1_mm0wvb2f

## Installation
- **Prerequisite:** Academicworld database setup in MySQL, MongoDB, and Neo4j.
- **Step 1:** Download the python files and requirements.txt
- **Step 2:** Configure mongodb_utils.py, mysql_utils.py, neo4j_utils.py and connect to academicworld database
- **Step 3:** Start the neo4j database before running the APP
- **Step 4:** Install required packages using 'pip install -r requirements.txt'
- **Step 5:** Execute app.py to run the application
- **Step 6:** Navigate to the web app through the provided URL.

## Usage
The Dashboard has 6 widgets, each offering a unique functionality --

**1. Trend of Keywords**   
Users select a research keyword, and the widget displays a line chart showing the publication trends related to a selected research keyword over time.

**2. Top Professors of Keyword**        
Users select a keyword and the year range, and the widget lists the top 10 professors, their institutes and citation scores in a specific field based on keyword-relevant citation (KRC) during the selected time range.

**3. Top Keywords of University**           
Users select an institute, and the widget visualizes the top 10 keywords associated with a university based on professor interest. Keywords are ranked based on the number of professors insterested in the keyword.

**4. Top Keywords of Professor**                  
Users select a professor, and the widget shows the top 10 research keywords of the professor, ranked by citation scores (KRC)

**5. Recommended Professors**                         
Users add their favorite keywords into a list,  and the widget provides recommendations of 5 professors based on favorite keywords, along with their total citation scores and institutes. Professors are ranked by total KRC, which is the sum of KRC of each keyword in the favorite keywords list.

**6. Recommended Universities**                   
Users add their favorite keywords into a list, and the widget suggests 5 universities based on favorite keywords, displaying related professors count and total citation score. Universities are ranked by total KRC, which is a sum of all KRC of favorite keywords of all professors in each university.

## Design
**Architecture:** The application uses Dash for the frontend and Flask for the backend, communicating with databases through APIs. It integrates MongoDB, Neo4j, and MySQL databases. Flask manages server-side operations and facilitates communication.

**Components:**              
* app.py: Frontend implementation using Dash and Flask.
* mongodb_utils.py: Queries data from MongoDB using MongoClient.
* neo4j_utils.py: Queries data from Neo4j using GraphDatabase.
* mysql_utils.py: Queries data from MySQL using mysql.connector.

## Implementation 
* widget 1: Query data from MongoDB database using MongoClient
* widget 2-4: Query data from Neo4j database using GraphDatabase
* widget 5-6: Query data from MySQL database using mysqlconnector
* Web app: Developed using Dash, Dash_bootstrap_components, and Plotly for frontend design and visualization. Backend operations managed through Flask, MongoDB, MySQL, and Neo4j databases.

## Database Techniques 
* Indexing: Added an index to the keyword table based on 'name' column in MySQL for improved query performance.
* Constraint: Implemented a foreign key constraint on the faculty_keyword table on 'keyword_id' in MySQL.
* Trigger: Added a trigger on faculty_keyword in MySQL to check if score is non-negative

## Extra-Credit Capabilities
NA

## Contributions
This project was independently developed by Runqi Liu, with approximately 30 to 40 hours dedicated to its completion.
