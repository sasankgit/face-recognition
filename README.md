# Face Recognition System

A complete face recognition application built with Python Flask backend and React + Vite + Tailwind CSS frontend.

## Features

- **Face Registration**: Register new faces with names using webcam
- **Face Recognition**: Recognize registered faces and display names
- **Real-time Camera**: Live webcam feed with image capture
- **User Management**: View and delete registered faces
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS

## Project Structure

```
finalfacerecognition/
├── backend/
│   └── app.py                 # Flask backend server
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # React entry point
│   │   ├── App.css           # Custom styles
│   │   └── index.css         # Tailwind CSS imports
│   ├── package.json          # Frontend dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── postcss.config.js     # PostCSS configuration
├── requirements.txt           # Python backend dependencies
└── README.md                 # This file
```

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Webcam access for face capture

## Installation

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Start the Flask server:**
   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will run on `http://localhost:3001`

## Usage

### 1. Register a New Face

1. Open the application in your browser
2. Allow webcam access when prompted
3. Position your face in the camera view
4. Click "Capture Image" to take a photo
5. Enter the person's name in the "Register New Face" section
6. Click "Register Face" to save the face

### 2. Recognize a Face

1. Position the person's face in the camera view
2. Click "Capture Image" to take a photo
3. Click "Recognize Face" to identify the person
4. If recognized, the system will display:
   - Person's name
   - Recognition confidence percentage
   - Success message

### 3. Manage Registered Faces

- View all registered faces in the right panel
- Delete faces using the "Delete" button next to each name
- The system automatically updates the list after changes

## API Endpoints

### Backend API (Flask)

- `POST /register_face` - Register a new face with name
- `POST /recognize_face` - Recognize a face from image
- `GET /get_registered_faces` - Get list of registered faces
- `DELETE /delete_face/<name>` - Delete a registered face

## Technical Details

### Backend Technologies

- **Flask**: Python web framework
- **face_recognition**: Face detection and encoding library
- **OpenCV**: Image processing
- **PIL/Pillow**: Image manipulation
- **NumPy**: Numerical operations

### Frontend Technologies

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **react-webcam**: Webcam integration
- **Axios**: HTTP client for API calls

### Face Recognition Process

1. **Registration**:
   - Capture image from webcam
   - Detect face location in image
   - Generate 128-dimensional face encoding
   - Store encoding with name

2. **Recognition**:
   - Capture new image
   - Generate face encoding
   - Compare with all registered encodings
   - Find best match using distance threshold
   - Return name and confidence if recognized

## Troubleshooting

### Common Issues

1. **Webcam not working**:
   - Ensure browser has camera permissions
   - Check if another application is using the camera

2. **Face not detected**:
   - Ensure good lighting
   - Face should be clearly visible and centered
   - Avoid multiple faces in frame

3. **Installation errors**:
   - Use Python 3.8+ for compatibility
   - Ensure pip is up to date
   - Try installing packages individually if needed

4. **Performance issues**:
   - Face recognition can be CPU-intensive
   - Close other applications for better performance
   - Use smaller images for faster processing

### Dependencies Issues

If you encounter issues with `face_recognition` or `opencv-python`:

1. **Windows users**: These packages come pre-compiled and should work without build tools
2. **Alternative**: If issues persist, try using `pip install --only-binary=all opencv-python`

## Security Notes

- This is a development/demo application
- Face data is stored locally
- No encryption of face encodings
- Consider security implications for production use

## License

This project is for educational and demonstration purposes.

## Contributing

Feel free to submit issues and enhancement requests!
