**FinAgent Dashboard**

FinAgent is a financial dashboard application designed to help users manage their budgets, track spending, and plan savings. Built using Python and Streamlit, this project provides an interactive and user-friendly interface for visualizing financial data, analyzing spending habits, and setting financial goals. While the app is fully functional locally, it is not hosted dynamically due to deployment challenges. Instead, screenshots are provided to showcase its features. Initially, we explored using the Plaid API to fetch actual transaction data, but due to a limited dataset, we switched to generating sample data to properly demonstrate the project's capabilities.

**Project Overview**

The goal of FinAgent is to empower users with a simple yet powerful tool to take control of their personal finances. The dashboard allows users to:

- Visualize their budget distribution across needs, wants, and savings.
- Analyze monthly spending patterns through interactive charts.
- Set and track savings goals with a dedicated savings plan feature.
- Query an AI-powered assistant for financial advice based on their data.

This project was developed as part of **Module 7 (Dashboard UI, Sprint 4)**, focusing on building a functional, visually appealing, and user-centric financial tool.

**What We Have Done**

Throughout the development of FinAgent, several key milestones were achieved:

- **Dashboard Design**: Created a two-column layout with a green-themed UI, ensuring a professional and intuitive user experience.
- **Data Integration**: Loaded and processed financial data (e.g., transactions, budgets, savings) from JSON files for real-time analysis.
- **Interactive Features**: Implemented dropdowns for month selection, forms for savings plans, and buttons for user interactions.
- **Charts and Visualizations**: Used Plotly to generate pie charts for budget distribution and bar charts for spending analysis.
- **AI Integration**: Added an LLM query section to provide users with personalized financial advice.
- **Testing**: Wrote unit tests for transaction cleaning and dashboard functionality, ensuring code reliability.
- **CI/CD Pipelin**e: Set up GitHub Actions for automated testing, code formatting checks, and Docker image builds.
- **Dockerization**: Containerized the app using Docker for easy deployment and scalability.


**What We Have Learned**

This project provided valuable hands-on experience in several areas:

- **Python & Streamlit**: Gained proficiency in building interactive web apps with Streamlit, leveraging its simplicity for rapid development.
- **Data Handling**: Learned to manage and process financial data using pandas, ensuring clean and structured inputs for analysis.
- **UI/UX Design**: Developed skills in creating user-friendly interfaces with custom CSS, focusing on layout, color schemes, and accessibility.
- **Testing & Automation**: Mastered writing unit tests with unittest and automating workflows with GitHub Actions for continuous integration.
- **Docker**: Understood containerization basics, creating Dockerfiles, and managing images for consistent environments.
- **Version Control**: Enhanced Git skills through branching, committing, and resolving merge conflicts in a collaborative setting.
- **Problem-Solving**: Tackled challenges like deployment issues, learning to adapt and find alternative solutions.


**How This Project Helps**

FinAgent offers several benefits:

**For Users**:

Provides a clear overview of financial health through visual data.
Helps in setting and achieving savings goals with a dedicated planner.
Offers actionable insights through AI-driven financial advice.


**For Developers**:

Serves as a practical example of building a full-stack app with Python.
Demonstrates best practices in code structure, testing, and automation.
Provides a template for integrating data visualization and AI features.


**Getting Started**

- Clone the repository: git clone [https://github.com/yourusername/Finagent](https://github.com/SFA16SCM21C/Finagent) {Clones the project to your local machine}
- Set up a virtual environment: python -m venv venv && source venv/bin/activate {Creates and activates a virtual environment}
- Install dependencies: pip install -r requirements.txt {Installs required Python packages}
- Run the main script: python src/main.py {Initializes the project, skip if not applicable}
- Launch the Streamlit app: streamlit run src/dashboard.py {Starts the dashboard at http://localhost:8501}
- Explore the dashboard: Open browser to http://localhost:8501 {Interact with the app's features}


**Future Improvements**

While FinAgent is functional, there are opportunities for enhancement:

**Dynamic Hosting**: Deploy the app on platforms like Streamlit Sharing or Heroku for full interactivity.
**User Authentication**: Add login functionality to support multiple users.
**Data Sources**: Integrate with real-time financial APIs for live data updates.
**Mobile Optimization**: Ensure the UI is responsive for mobile devices.


**Screenshots**

To get a sense of how the FinAgent dashboard looks and feels, please refer to the screenshots folder within the project repository, which contains captured screenshots showcasing the layout, charts, and interactive elements of the app.

**Apologies for Not Hosting This Project**

Due to technical challenges with deployment, we were unable to host a live version of the FinAgent dashboard. We apologize for this limitation but encourage you to explore the screenshots for a visual representation of the project.
