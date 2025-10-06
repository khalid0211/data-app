# Streamlit Firebase Library System

This project is a simple library management system built using Streamlit and Firebase. It allows users to manage a collection of books by adding, editing, and deleting entries. Each book contains the following fields: Title, Author(s), Publisher, Edition, and Publish Date.

## Project Structure

```
streamlit-firebase-library
├── app.py               # Main entry point of the Streamlit application
├── firebase_utils.py    # Utility functions for Firebase interactions
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Prerequisites

- Python 3.8+
- A Google Firebase project

## Setup Instructions

### 1. Clone the Repository

Clone or download this project to your local machine:
```bash
git clone <repository-url>
cd data-app
```

### 2. Set up Firebase

1. Go to your [Firebase Console](https://console.firebase.google.com/).
2. Create a new project (or use an existing one).
3. In your project, go to **Project Settings** (the gear icon).
4. Navigate to the **Service accounts** tab.
5. Click on **"Generate new private key"**. A JSON file will be downloaded.
6. **Important:** Rename this file if you wish, and place it in a secure location within your project directory. For this project, you can place it in the root folder.
7. Go to the `utils/firebase_utils.py` file and update the `key_path` variable to the path of your downloaded JSON key file:
   ```python
   # In utils/firebase_utils.py
   key_path = "path/to/your/firebase/serviceAccountKey.json"  # Change this line
   ```
8. In the Firebase Console, go to **Firestore Database** from the left-hand menu.
9. Click **"Create database"**. Start in **test mode** for easy setup (you can change security rules later). Choose a location and click **Enable**.

### 3. Install Dependencies

Open your terminal or command prompt, navigate to the project directory, and install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Application

Once the dependencies are installed, you can run the Streamlit app with the following command:
```bash
streamlit run app.py
```

Your web browser should open with the application running.


## Features

- **Add Books:** Users can input details for new books to be added to the library.
- **Edit Books:** Existing book entries can be modified.
- **Delete Books:** Users can remove books from the library.
- **View Books:** A list of all books in the library is displayed, showing their details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.