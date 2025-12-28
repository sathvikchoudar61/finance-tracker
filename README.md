# Finance Tracker

A robust desktop application built with Python and PyQt5 for tracking personal finances. This application allows users to manage their income and expenses with an intuitive graphical user interface.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)

## ✨ Features
- **Dashboard Overview**: View your current balance at a glance with color-coded indicators.
- **Transaction Management**:
  - **Send Money**: Record expenses with details like name, amount, description, and date.
  - **Receive Money**: Record income with key financial details.
  - **Edit/Remove**: Modify or delete existing transactions easily.
- **Search & Filter**: Quickly find transactions by name, description, amount, or date.
- **Data Persistence**: All data is automatically saved to a local JSON file (`transactions.json`), ensuring your records are never lost.
- **Responsive UI**: A clean, responsive interface powered by PyQt5.

## 🛠 Tech Stack
- **Language**: Python 3.x
- **GUI Framework**: PyQt5
- **Data Storage**: JSON (Local file system)

## 📝 Prerequisites
Before running this application, ensure you have the following installed:
- [Python 3.x](https://www.python.org/downloads/)

## 🚀 Installation

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Dependencies**
    This project requires `PyQt5`. You can install it using pip:
    ```bash
    pip install PyQt5
    ```

## 💡 Usage

1.  **Run the Application**
    Execute the main script to start the application:
    ```bash
    python main.py
    ```

2.  **Using the App**:
    - **Add Transaction**: Click "Receive Money" or "Send Money" on the sidebar. Fill in the specific details and submit.
    - **Edit Transaction**: Click the "Edit" button on any transaction item in the list.
    - **Delete Transaction**: Click the "Remove" button to delete a record.
    - **Search**: Use the search bar at the top to filter through your transaction history.

## 📂 Project Structure
```
finance-tracker/
├── main.py              # Main application entry point and logic
├── transactions.json    # Data storage file (auto-generated)
└── README.md            # Project documentation
```

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
