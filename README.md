# Generative-AI : Database Query Creator
Problem Statement: Database Query Creator 

Problem Overview: In the era of data-driven decision-making, businesses and individuals often struggle with the complexity of constructing efficient and accurate database queries. The objective of this challenge is to develop a Database Query Helper that leverages Generative AI to assist users in formulating, optimizing, and troubleshooting SQL queries.

Challenge: You have to build a query helper tools feature that assists users in crafting SQL queries based on the documented schema. You will be given some sample schema and sample natural language queries. The tool should be able to convert similar queries to their corresponding SQL statements. 

Overview
This project translates human-readable questions into precise SQL queries using Google
Cloud's Gemini AI model. It iteratively refines the queries to ensure accuracy and proper
execution. Designed for seamless interaction with databases, the app makes querying as
simple as asking a question.

Key Features
  Natural Language Input: Users can input queries in plain language.
  Iterative Query Refinement: Improves SQL queries by handling syntax errors and database schema compliance.
  Database Connection: Executes refined queries directly on the connected database for real-time results.
  Error Handling: Detects and fixes query errors iteratively for reliable execution. 
  Optimized Queries: Generates queries that avoid common issues, like unnecessary joins, and includes clauses like LIMIT 100.


This project features a user-friendly interface, is deployed on Google Cloud, and
includes a GitHub pipeline that automatically builds and restarts the application, ensuring
real-time reflection of code changes.


Setup Guide

Prerequisites
1. Install Docker on your machine and start the vpn so that the app can connect with the
hackathon database.
2. Clone the project repository from the provided code in the gcp bucket.


Steps to Setup and Run the Project

1) Build the Docker image
   
docker build -t sql-converter .

2) Run the Docker container:

docker run -p 8501:8501 sql-converter

3) Access the App:
The app will be available at http://localhost:port
