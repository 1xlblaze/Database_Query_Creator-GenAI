🌟 Generative-AI: Database Query Creator

📝 Problem Statement:

In the era of data-driven decision-making, constructing efficient and accurate database queries can be challenging for businesses and individuals. This project aims to solve this by developing a Database Query Helper using Generative AI that assists users in formulating, optimizing, and troubleshooting SQL queries.
🚀 Project Overview:

This project leverages Google Cloud's Gemini AI model to translate human-readable questions into precise SQL queries. It iteratively refines these queries to ensure accuracy and proper execution, making database interaction as easy as asking a question.
🛠️ Key Features:

    Natural Language Input: Users can craft queries in simple, plain language.
    Iterative Query Refinement: Automatically refines SQL queries to fix syntax errors and align them with the database schema.
    Database Connection: Executes refined queries directly on the connected database to provide real-time results.
    Error Handling: Identifies and fixes query errors for reliable execution.
    Optimized Queries: Generates efficient SQL statements that minimize common issues (e.g., unnecessary joins) and includes performance-oriented clauses like LIMIT 100.

    Bonus: The project features a user-friendly interface and is seamlessly deployed on Google Cloud, with a GitHub pipeline that automatically builds and restarts the application for real-time code updates.

📦 Setup Guide

Before you begin, ensure you have Docker installed and a working VPN connection for database access.
Prerequisites:

    Docker: Install Docker and verify it's running on your machine.
    Clone the Repository: Clone the project repository from the code provided in Generative-AI repository

Steps to Setup and Run the Project:
   Build the Docker Image:

      docker build -t sql-converter .

   Run the Docker Container:
   
     docker run -p 8501:8501 sql-converter

  Access the App:

     Open your browser and go to: http://localhost:8501

💡 Usage Instructions:

    Input Natural Language Query: Type your question in plain English.
    Review SQL Output: The app will generate an SQL statement based on your input.
    Iterative Refinement: If needed, the app will auto-correct or refine the query for errors and optimization.

🌐 Project Deployment & Pipeline:

This app is hosted on Google Cloud, with a GitHub Actions pipeline that automates the build process. The pipeline automatically builds and redeploys the application on code changes, ensuring zero downtime and real-time reflection of updates.
🤝 Contributing:

We welcome contributions! If you'd like to contribute, please follow these steps:

    Fork the repository.
    Create a new branch (git checkout -b feature/new-feature).
    Commit your changes (git commit -m 'Add a new feature').
    Push to the branch (git push origin feature/new-feature).
    Create a pull request.

📝 License:

This project is licensed under the MIT License. See the LICENSE file for more information.
🙌 Acknowledgements:

Special thanks to the Google Cloud Gemini AI team for providing the robust AI model, and all contributors who helped shape this project.
📧 Contact:

For any queries or issues, feel free to reach out to us via GitHub or email.
