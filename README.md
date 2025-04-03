# Student Registration System

A web application for managing student registrations using Flask and Firebase.

## Contact Information
- Email: nraoswasthik2004@gmail.com
- LinkedIn: [www.linkedin.com/in/swasthik-n-rao](https://www.linkedin.com/in/swasthik-n-rao)

## Setup Instructions

1. Install Python requirements:
```bash
pip install -r requirements.txt
```

2. Set up Firebase:
   - Go to the Firebase Console (https://console.firebase.google.com/)
   - Create a new project
   - Go to Project Settings > Service Accounts
   - Generate a new private key
   - Save the JSON file as `serviceAccountKey.json` in the root directory of this project

3. Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Features

- Student registration form with all necessary fields
- Data storage in Firebase Firestore
- Responsive design using Bootstrap
- Form validation
- Success/error messages
- Secure data handling
- Real-time database updates

## File Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   └── student_form.html  # Student registration form
├── static/              # Static files (CSS, JS, images)
├── .env                 # Environment variables
├── firestore.rules      # Firebase security rules
├── firestore.indexes.json # Firebase indexes
└── .gitignore          # Git ignore rules
```

## Security Notes

- Keep your `serviceAccountKey.json` secure and never commit it to version control
- Use environment variables for sensitive information
- Implement proper authentication before deploying to production
- Follow Firebase security rules for data protection

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 