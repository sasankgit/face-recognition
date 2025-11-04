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
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Directory to store registered faces
FACES_DIR = "registered_faces"
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)

# File to store face encodings and names
FACES_DATA_FILE = "faces_data.json"
DEEPFACE_DATA_FILE = "deepface_data.json"

def print_separator():
    """Print a separator line for better readability"""
    print("=" * 80)

def print_header(text):
    """Print a header with timestamp"""
    print_separator()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}")
    print_separator()

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
        print("📥 Converting base64 string to image...")
        # Remove data:image/jpeg;base64, prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        print(f"✅ Image converted successfully - Size: {image.size}, Mode: {image.mode}")
        return image
    except Exception as e:
        print(f"❌ Error converting base64 to image: {e}")
        return None

def image_to_face_encoding(image):
    """Convert PIL Image to face encoding (face_recognition model)"""
    try:
        print("🔍 Processing image with face_recognition library...")
        # Convert PIL Image to numpy array
        image_array = np.array(image)
        print(f"   Image array shape: {image_array.shape}")
        
        # Convert RGB to BGR if needed (OpenCV uses BGR)
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            print("   ✓ Converted RGB to BGR")
        
        # Find face locations
        print("   🔎 Detecting face locations...")
        face_locations = face_recognition.face_locations(image_array)
        
        if not face_locations:
            print("   ❌ No face detected in the image")
            return None, "No face detected in the image"
        
        print(f"   ✓ Found {len(face_locations)} face(s)")
        
        if len(face_locations) > 1:
            print("   ⚠️  Multiple faces detected!")
            return None, "Multiple faces detected. Please use an image with only one face."
        
        # Get face encoding
        print("   🧬 Generating face encoding...")
        face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
        print(f"   ✅ Face encoding generated - Encoding length: {len(face_encoding)}")
        return face_encoding, None
        
    except Exception as e:
        print(f"   ❌ Error processing image: {str(e)}")
        return None, f"Error processing image: {str(e)}"

def save_image_for_deepface(image, name):
    """Save image for DeepFace processing"""
    try:
        print(f"💾 Saving image for DeepFace - Name: {name}")
        deepface_dir = os.path.join(FACES_DIR, "deepface")
        if not os.path.exists(deepface_dir):
            os.makedirs(deepface_dir)
            print(f"   📁 Created directory: {deepface_dir}")
        
        image_path = os.path.join(deepface_dir, f"{name}.jpg")
        image.save(image_path, "JPEG")
        print(f"   ✅ Image saved to: {image_path}")
        return image_path
    except Exception as e:
        print(f"   ❌ Error saving image for DeepFace: {e}")
        return None

def verify_face_deepface(image, name):
    """Verify face using DeepFace"""
    try:
        print(f"   🔍 Verifying against: {name}")
        # Save temporary image
        temp_path = os.path.join(FACES_DIR, "temp_verify.jpg")
        image.save(temp_path, "JPEG")
        print(f"   💾 Temporary image saved")
        
        # Get registered image path
        registered_path = os.path.join(FACES_DIR, "deepface", f"{name}.jpg")
        
        if not os.path.exists(registered_path):
            print(f"   ⚠️  Registered image not found for {name}")
            return None, "Registered image not found"
        
        # Verify using DeepFace
        print(f"   🧠 Running DeepFace verification with VGG-Face model...")
        result = DeepFace.verify(
            img1_path=temp_path,
            img2_path=registered_path,
            model_name='VGG-Face',
            enforce_detection=True
        )
        
        print(f"   📊 Verification result for {name}:")
        print(f"      - Verified: {result.get('verified', False)}")
        print(f"      - Distance: {result.get('distance', 'N/A'):.4f}")
        print(f"      - Threshold: {result.get('threshold', 'N/A')}")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"   🗑️  Temporary file cleaned up")
        
        return result, None
        
    except Exception as e:
        print(f"   ❌ Error in DeepFace verification for {name}: {str(e)}")
        # Clean up temp file
        temp_path = os.path.join(FACES_DIR, "temp_verify.jpg")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return None, f"Error in DeepFace verification: {str(e)}"

@app.route('/register_face', methods=['POST'])
def register_face():
    """Register a new face with a name"""
    print_header("📝 NEW FACE REGISTRATION REQUEST")
    
    try:
        data = request.get_json()
        name = data.get('name')
        image_base64 = data.get('image')
        model = data.get('model', 'face_recognition')
        
        print(f"👤 Name: {name}")
        print(f"🤖 Model: {model}")
        print(f"📷 Image data received: {len(image_base64) if image_base64 else 0} characters")
        
        if not name or not image_base64:
            print("❌ Missing name or image data")
            return jsonify({'success': False, 'message': 'Name and image are required'}), 400
        
        # Convert base64 to image
        image = base64_to_image(image_base64)
        if image is None:
            print("❌ Failed to convert image")
            return jsonify({'success': False, 'message': 'Invalid image format'}), 400
        
        if model == 'deepface':
            print("\n🧠 Using DeepFace model for registration...")
            # DeepFace registration
            deepface_data = load_deepface_data()
            print(f"📚 Currently registered faces in DeepFace: {len(deepface_data)}")
            
            if name in deepface_data:
                print(f"⚠️  Name '{name}' already exists in DeepFace database")
                return jsonify({'success': False, 'message': 'Name already registered'}), 400
            
            # Save image for DeepFace
            image_path = save_image_for_deepface(image, name)
            if not image_path:
                print("❌ Failed to save image for DeepFace")
                return jsonify({'success': False, 'message': 'Error saving image'}), 400
            
            # Store metadata
            deepface_data[name] = {
                'image_path': image_path,
                'timestamp': str(np.datetime64('now'))
            }
            save_deepface_data(deepface_data)
            print(f"✅ Face registered successfully in DeepFace database")
            print(f"📊 Total registered faces in DeepFace: {len(deepface_data)}")
            print_separator()
            
            return jsonify({
                'success': True, 
                'message': f'Face registered successfully for {name} using DeepFace'
            })
        
        else:
            print("\n🔍 Using face_recognition model for registration...")
            # Original face_recognition registration
            face_encoding, error = image_to_face_encoding(image)
            if error:
                print(f"❌ Face encoding failed: {error}")
                return jsonify({'success': False, 'message': error}), 400
            
            faces_data = load_faces_data()
            print(f"📚 Currently registered faces in face_recognition: {len(faces_data)}")
            
            if name in faces_data:
                print(f"⚠️  Name '{name}' already exists in face_recognition database")
                return jsonify({'success': False, 'message': 'Name already registered'}), 400
            
            faces_data[name] = {
                'encoding': face_encoding.tolist(),
                'timestamp': str(np.datetime64('now'))
            }
            save_faces_data(faces_data)
            
            # Save image for reference
            image_path = os.path.join(FACES_DIR, f"{name}.jpg")
            image.save(image_path, "JPEG")
            print(f"💾 Reference image saved to: {image_path}")
            print(f"✅ Face registered successfully in face_recognition database")
            print(f"📊 Total registered faces in face_recognition: {len(faces_data)}")
            print_separator()
            
            return jsonify({
                'success': True, 
                'message': f'Face registered successfully for {name}'
            })
        
    except Exception as e:
        print(f"❌ REGISTRATION FAILED: {str(e)}")
        print_separator()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    """Recognize a face from the uploaded image"""
    print_header("🔎 FACE RECOGNITION REQUEST")
    
    try:
        data = request.get_json()
        image_base64 = data.get('image')
        model = data.get('model', 'face_recognition')
        
        print(f"🤖 Model: {model}")
        print(f"📷 Image data received: {len(image_base64) if image_base64 else 0} characters")
        
        if not image_base64:
            print("❌ No image data provided")
            return jsonify({'success': False, 'message': 'Image is required'}), 400
        
        # Convert base64 to image
        image = base64_to_image(image_base64)
        if image is None:
            print("❌ Failed to convert image")
            return jsonify({'success': False, 'message': 'Invalid image format'}), 400
        
        if model == 'deepface':
            print("\n🧠 Using DeepFace model for recognition...")
            # DeepFace recognition
            deepface_data = load_deepface_data()
            print(f"📚 Checking against {len(deepface_data)} registered face(s)")
            
            if not deepface_data:
                print("⚠️  No registered faces found in DeepFace database")
                return jsonify({
                    'success': False, 
                    'message': 'No registered faces found',
                    'recognized': False
                }), 404
            
            best_match = None
            best_distance = float('inf')
            
            print("\n🔄 Starting face comparison process...")
            for idx, name in enumerate(deepface_data.keys(), 1):
                print(f"\n   [{idx}/{len(deepface_data)}] Comparing with: {name}")
                result, error = verify_face_deepface(image, name)
                
                if error:
                    print(f"   ⚠️  Skipping {name} due to error")
                    continue
                
                if result and result['distance'] < best_distance:
                    best_distance = result['distance']
                    best_match = name
                    print(f"   ⭐ New best match! Distance: {best_distance:.4f}")
            
            # Threshold for DeepFace (lower is better)
            recognition_threshold = 0.4
            print(f"\n📊 Recognition Results:")
            print(f"   Best match: {best_match if best_match else 'None'}")
            print(f"   Best distance: {best_distance:.4f}")
            print(f"   Threshold: {recognition_threshold}")
            
            if best_match and best_distance <= recognition_threshold:
                confidence = 1 - (best_distance / 1.0)  # Normalize to 0-1
                confidence = max(0, min(1, confidence))
                print(f"   ✅ FACE RECOGNIZED!")
                print(f"   👤 Identified as: {best_match}")
                print(f"   📈 Confidence: {confidence * 100:.2f}%")
                print_separator()
                
                return jsonify({
                    'success': True,
                    'recognized': True,
                    'name': best_match,
                    'confidence': confidence,
                    'message': f'Face recognized as {best_match}'
                })
            else:
                print(f"   ❌ FACE NOT RECOGNIZED")
                print(f"   Distance {best_distance:.4f} exceeds threshold {recognition_threshold}")
                print_separator()
                
                return jsonify({
                    'success': True,
                    'recognized': False,
                    'message': 'Face not recognized'
                })
        
        else:
            print("\n🔍 Using face_recognition model for recognition...")
            # Original face_recognition model
            face_encoding, error = image_to_face_encoding(image)
            if error:
                print(f"❌ Face encoding failed: {error}")
                return jsonify({'success': False, 'message': error}), 400
            
            faces_data = load_faces_data()
            print(f"📚 Checking against {len(faces_data)} registered face(s)")
            
            if not faces_data:
                print("⚠️  No registered faces found in face_recognition database")
                return jsonify({
                    'success': False, 
                    'message': 'No registered faces found',
                    'recognized': False
                }), 404
            
            best_match = None
            best_distance = float('inf')
            
            print("\n🔄 Starting face comparison process...")
            for idx, (name, face_data) in enumerate(faces_data.items(), 1):
                print(f"   [{idx}/{len(faces_data)}] Comparing with: {name}")
                registered_encoding = np.array(face_data['encoding'])
                distance = face_recognition.face_distance([registered_encoding], face_encoding)[0]
                print(f"      Distance: {distance:.4f}")
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = name
                    print(f"      ⭐ New best match!")
            
            recognition_threshold = 0.6
            print(f"\n📊 Recognition Results:")
            print(f"   Best match: {best_match if best_match else 'None'}")
            print(f"   Best distance: {best_distance:.4f}")
            print(f"   Threshold: {recognition_threshold}")
            
            if best_distance <= recognition_threshold:
                confidence = 1 - best_distance
                print(f"   ✅ FACE RECOGNIZED!")
                print(f"   👤 Identified as: {best_match}")
                print(f"   📈 Confidence: {confidence * 100:.2f}%")
                print(f"   📏 Match quality: {'Excellent' if confidence > 0.8 else 'Good' if confidence > 0.6 else 'Fair'}")
                print_separator()
                
                return jsonify({
                    'success': True,
                    'recognized': True,
                    'name': best_match,
                    'confidence': confidence,
                    'message': f'Face recognized as {best_match}'
                })
            else:
                print(f"   ❌ FACE NOT RECOGNIZED")
                print(f"   Distance {best_distance:.4f} exceeds threshold {recognition_threshold}")
                print_separator()
                
                return jsonify({
                    'success': True,
                    'recognized': False,
                    'message': 'Face not recognized'
                })
        
    except Exception as e:
        print(f"❌ RECOGNITION FAILED: {str(e)}")
        print_separator()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/get_registered_faces', methods=['GET'])
def get_registered_faces():
    """Get list of all registered faces from both models"""
    print_header("📋 GET REGISTERED FACES REQUEST")
    
    try:
        faces_data = load_faces_data()
        deepface_data = load_deepface_data()
        
        print(f"📊 Database Status:")
        print(f"   face_recognition: {len(faces_data)} face(s)")
        print(f"   DeepFace: {len(deepface_data)} face(s)")
        
        # Combine names from both models (remove duplicates)
        all_names = list(set(list(faces_data.keys()) + list(deepface_data.keys())))
        
        print(f"   Total unique faces: {len(all_names)}")
        if all_names:
            print(f"   Names: {', '.join(sorted(all_names))}")
        
        print_separator()
        
        return jsonify({
            'success': True,
            'faces': sorted(all_names),
            'count': len(all_names)
        })
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print_separator()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/delete_face/<name>', methods=['DELETE'])
def delete_face(name):
    """Delete a registered face from both models"""
    print_header(f"🗑️  DELETE FACE REQUEST: {name}")
    
    try:
        faces_data = load_faces_data()
        deepface_data = load_deepface_data()
        
        deleted = False
        deleted_from = []
        
        # Remove from face_recognition data
        if name in faces_data:
            print(f"🔍 Found '{name}' in face_recognition database")
            del faces_data[name]
            save_faces_data(faces_data)
            deleted = True
            deleted_from.append('face_recognition')
            print(f"   ✅ Removed from face_recognition")
            
            # Remove image file
            image_path = os.path.join(FACES_DIR, f"{name}.jpg")
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"   🗑️  Deleted image file: {image_path}")
        
        # Remove from DeepFace data
        if name in deepface_data:
            print(f"🔍 Found '{name}' in DeepFace database")
            del deepface_data[name]
            save_deepface_data(deepface_data)
            deleted = True
            deleted_from.append('DeepFace')
            print(f"   ✅ Removed from DeepFace")
            
            # Remove DeepFace image file
            deepface_image_path = os.path.join(FACES_DIR, "deepface", f"{name}.jpg")
            if os.path.exists(deepface_image_path):
                os.remove(deepface_image_path)
                print(f"   🗑️  Deleted image file: {deepface_image_path}")
        
        if not deleted:
            print(f"⚠️  Face '{name}' not found in any database")
            print_separator()
            return jsonify({'success': False, 'message': 'Face not found'}), 404
        
        print(f"✅ Successfully deleted '{name}' from: {', '.join(deleted_from)}")
        print(f"📊 Remaining faces:")
        print(f"   face_recognition: {len(faces_data)}")
        print(f"   DeepFace: {len(deepface_data)}")
        print_separator()
        
        return jsonify({
            'success': True,
            'message': f'Face {name} deleted successfully'
        })
        
    except Exception as e:
        print(f"❌ DELETE FAILED: {str(e)}")
        print_separator()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print_header("🚀 FACE RECOGNITION SERVER STARTING")
    print("Server running on: http://0.0.0.0:5000")
    print("Press CTRL+C to quit")
    print_separator()
    app.run(debug=True, host='0.0.0.0', port=5000)