# Pairwise Voting Web Application

A lightweight, anonymous, multi-user web application built with Streamlit and MongoDB for pairwise voting on Q&A pairs, featuring a dedicated analysis dashboard.

## Features
- **Anonymous Voting:** Multi-user anonymous pairwise voting.
- **Flexible Rating:** Rate RAG or LLM-generated answers (Up/Down).
- **Persistent Storage:** Uses MongoDB Atlas for reliable data persistence.
- **Analysis Dashboard:** A dedicated interface to view questions, answers, gold references, and automated evaluation feedback/scores.
- **Data Export:** Tools to export voting data for analysis.

## Setup

### 1. Prerequisites
- Python 3.x
- `pip`

### 2. Installation
```bash
# Clone the repository
git clone <repository_url>
cd voting_app_abinit_forum

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.streamlit/secrets.toml` file in the project root to manage your MongoDB connection:

```toml
# .streamlit/secrets.toml
MONGO_URI = "mongodb+srv://<username>:<password>@<cluster_url>/?appName=MyCluster"
```

### 4. Running the Applications

**Voting Application:**
```bash
streamlit run app.py
```

**Analysis Dashboard:**
```bash
streamlit run analysis_app.py
```

## Utilities
- **Data Export:** Export voting data to CSV.
  ```bash
  python3 export_votes.py
  ```
- **Vote Analysis:** Generate a bar plot visualizing vote performance.
  ```bash
  python3 analyze_votes.py
  ```
- **Reset Votes:** Clear all recorded votes (keeps questions and answers).
  ```bash
  python3 reset_votes.py
  ```
