from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import cv2
import numpy as np
import os
import json
from PIL import Image
import base64
import io
from deepface import DeepFace

app = Flask(__name__)
CORS(app)

# Directory to store registered faces
FACES_DIR = "registered_faces"
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)

# File to store face encodings and names
FACES_DATA_FILE = "faces_data.json"
DEEPFACE_DATA_FILE = "deepface_data.json"

def load_faces_data():
    """Load registered faces data from JSON file"""
    if os.path.exists(FACES_DATA_FILE):
        with open(FACES_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_faces_data(faces_data):
    """Save registered faces data to JSON file"""
    with open(FACES_DATA_FILE, 'w') as f:
        json.dump(faces_data, f)

def load_deepface_data():
    """Load DeepFace registered faces data"""
    if os.path.exists(DEEPFACE_DATA_FILE):
        with open(DEEPFACE_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_deepface_data(deepface_data):
    """Save DeepFace registered faces data"""
    with open(DEEPFACE_DATA_FILE, 'w') as f:
        json.dump(deepface_data, f)

def base64_to_image(base64_string):
    """Convert base64 string to PIL Image"""
    try:
        # Remove data:image/jpeg;base64, prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        return None

def image_to_face_encoding(image):
    """Convert PIL Image to face encoding (face_recognition model)"""
    try:
        # Convert PIL Image to numpy array
        image_array = np.array(image)
        
        # Convert RGB to BGR if needed (OpenCV uses BGR)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Find face locations
        face_locations = face_recognition.face_locations(image_array)
        
        if not face_locations:
            return None, "No face detected in the image"
        
        if len(face_locations) > 1:
            return None, "Multiple faces detected. Please use an image with only one face."
        
        # Get face encoding
        face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
        return face_encoding, None
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

def save_image_for_deepface(image, name):
    """Save image for DeepFace processing"""
    try:
        deepface_dir = os.path.join(FACES_DIR, "deepface")
        if not os.path.exists(deepface_dir):
            os.makedirs(deepface_dir)
        
        image_path = os.path.join(deepface_dir, f"{name}.jpg")
        image.save(image_path, "JPEG")
        return image_path
    except Exception as e:
        print(f"Error saving image for DeepFace: {e}")
        return None

def verify_face_deepface(image, name):
    """Verify face using DeepFace"""
    try:
        # Save temporary image
        temp_path = os.path.join(FACES_DIR, "temp_verify.jpg")
        image.save(temp_path, "JPEG")
        
        # Get registered image path
        registered_path = os.path.join(FACES_DIR, "deepface", f"{name}.jpg")
        
        if not os.path.exists(registered_path):
            return None, "Registered image not found"
        
        # Verify using DeepFace
        result = DeepFace.verify(
            img1_path=temp_path,
            img2_path=registered_path,
            model_name='VGG-Face',
            enforce_detection=True
        )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return result, None
        
    except Exception as e:
        # Clean up temp file
        temp_path = os.path.join(FACES_DIR, "temp_verify.jpg")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None, f"Error in DeepFace verification: {str(e)}"

@app.route('/register_face', methods=['POST'])
def register_face():
    """Register a new face with a name"""
    try:
        data = request.get_json()
        name = data.get('name')
        image_base64 = data.get('image')
        model = data.get('model', 'face_recognition')
        
        if not name or not image_base64:
            return jsonify({'success': False, 'message': 'Name and image are required'}), 400
        
        # Convert base64 to image
        image = base64_to_image(image_base64)
        if image is None:
            return jsonify({'success': False, 'message': 'Invalid image format'}), 400
        
        if model == 'deepface':
            # DeepFace registration
            deepface_data = load_deepface_data()
            
            if name in deepface_data:
                return jsonify({'success': False, 'message': 'Name already registered'}), 400
            
            # Save image for DeepFace
            image_path = save_image_for_deepface(image, name)
            if not image_path:
                return jsonify({'success': False, 'message': 'Error saving image'}), 400
            
            # Store metadata
            deepface_data[name] = {
                'image_path': image_path,
                'timestamp': str(np.datetime64('now'))
            }
            save_deepface_data(deepface_data)
            
            return jsonify({
                'success': True, 
                'message': f'Face registered successfully for {name} using DeepFace'
            })
        
        else:
            # Original face_recognition registration
            face_encoding, error = image_to_face_encoding(image)
            if error:
                return jsonify({'success': False, 'message': error}), 400
            
            faces_data = load_faces_data()
            
            if name in faces_data:
                return jsonify({'success': False, 'message': 'Name already registered'}), 400
            
            faces_data[name] = {
                'encoding': face_encoding.tolist(),
                'timestamp': str(np.datetime64('now'))
            }
            save_faces_data(faces_data)
            
            # Save image for reference
            image_path = os.path.join(FACES_DIR, f"{name}.jpg")
            image.save(image_path, "JPEG")
            
            return jsonify({
                'success': True, 
                'message': f'Face registered successfully for {name}'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    """Recognize a face from the uploaded image"""
    try:
        data = request.get_json()
        image_base64 = data.get('image')
        model = data.get('model', 'face_recognition')
        
        if not image_base64:
            return jsonify({'success': False, 'message': 'Image is required'}), 400
        
        # Convert base64 to image
        image = base64_to_image(image_base64)
        if image is None:
            return jsonify({'success': False, 'message': 'Invalid image format'}), 400
        
        if model == 'deepface':
            # DeepFace recognition
            deepface_data = load_deepface_data()
            
            if not deepface_data:
                return jsonify({
                    'success': False, 
                    'message': 'No registered faces found',
                    'recognized': False
                }), 404
            
            best_match = None
            best_distance = float('inf')
            
            for name in deepface_data.keys():
                result, error = verify_face_deepface(image, name)
                
                if error:
                    continue
                
                if result and result['distance'] < best_distance:
                    best_distance = result['distance']
                    best_match = name
            
            # Threshold for DeepFace (lower is better)
            recognition_threshold = 0.4
            
            if best_match and best_distance <= recognition_threshold:
                confidence = 1 - (best_distance / 1.0)  # Normalize to 0-1
                return jsonify({
                    'success': True,
                    'recognized': True,
                    'name': best_match,
                    'confidence': max(0, min(1, confidence)),
                    'message': f'Face recognized as {best_match}'
                })
            else:
                return jsonify({
                    'success': True,
                    'recognized': False,
                    'message': 'Face not recognized'
                })
        
        else:
            # Original face_recognition model
            face_encoding, error = image_to_face_encoding(image)
            if error:
                return jsonify({'success': False, 'message': error}), 400
            
            faces_data = load_faces_data()
            
            if not faces_data:
                return jsonify({
                    'success': False, 
                    'message': 'No registered faces found',
                    'recognized': False
                }), 404
            
            best_match = None
            best_distance = float('inf')
            
            for name, face_data in faces_data.items():
                registered_encoding = np.array(face_data['encoding'])
                distance = face_recognition.face_distance([registered_encoding], face_encoding)[0]
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = name
            
            recognition_threshold = 0.6
            
            if best_distance <= recognition_threshold:
                return jsonify({
                    'success': True,
                    'recognized': True,
                    'name': best_match,
                    'confidence': 1 - best_distance,
                    'message': f'Face recognized as {best_match}'
                })
            else:
                return jsonify({
                    'success': True,
                    'recognized': False,
                    'message': 'Face not recognized'
                })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/get_registered_faces', methods=['GET'])
def get_registered_faces():
    """Get list of all registered faces from both models"""
    try:
        faces_data = load_faces_data()
        deepface_data = load_deepface_data()
        
        # Combine names from both models (remove duplicates)
        all_names = list(set(list(faces_data.keys()) + list(deepface_data.keys())))
        
        return jsonify({
            'success': True,
            'faces': sorted(all_names),
            'count': len(all_names)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/delete_face/<name>', methods=['DELETE'])
def delete_face(name):
    """Delete a registered face from both models"""
    try:
        faces_data = load_faces_data()
        deepface_data = load_deepface_data()
        
        deleted = False
        
        # Remove from face_recognition data
        if name in faces_data:
            del faces_data[name]
            save_faces_data(faces_data)
            deleted = True
            
            # Remove image file
            image_path = os.path.join(FACES_DIR, f"{name}.jpg")
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Remove from DeepFace data
        if name in deepface_data:
            del deepface_data[name]
            save_deepface_data(deepface_data)
            deleted = True
            
            # Remove DeepFace image file
            deepface_image_path = os.path.join(FACES_DIR, "deepface", f"{name}.jpg")
            if os.path.exists(deepface_image_path):
                os.remove(deepface_image_path)
        
        if not deleted:
            return jsonify({'success': False, 'message': 'Face not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Face {name} deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)