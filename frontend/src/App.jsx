import React, { useState, useEffect } from 'react'
import Webcam from 'react-webcam'
import axios from 'axios'
import './App.css'

function App() {
  const [webcamRef, setWebcamRef] = useState(null)
  const [capturedImage, setCapturedImage] = useState(null)
  const [isRegistering, setIsRegistering] = useState(false)
  const [isRecognizing, setIsRecognizing] = useState(false)
  const [registerName, setRegisterName] = useState('')
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')
  const [registeredFaces, setRegisteredFaces] = useState([])
  const [recognitionResult, setRecognitionResult] = useState(null)

  // API base URL
  const API_BASE = '/api'

  useEffect(() => {
    loadRegisteredFaces()
  }, [])

  const loadRegisteredFaces = async () => {
    try {
      const response = await axios.get(`${API_BASE}/get_registered_faces`)
      if (response.data.success) {
        setRegisteredFaces(response.data.faces)
      }
    } catch (error) {
      console.error('Error loading registered faces:', error)
    }
  }

  const captureImage = () => {
    if (webcamRef) {
      const imageSrc = webcamRef.getScreenshot()
      setCapturedImage(imageSrc)
      setMessage('')
      setRecognitionResult(null)
    }
  }

  const clearImage = () => {
    setCapturedImage(null)
    setMessage('')
    setRecognitionResult(null)
    setRegisterName('')
  }

  const registerFace = async () => {
    if (!capturedImage || !registerName.trim()) {
      setMessage('Please capture an image and enter a name')
      setMessageType('error')
      return
    }

    setIsRegistering(true)
    setMessage('')

    try {
      const response = await axios.post(`${API_BASE}/register_face`, {
        name: registerName.trim(),
        image: capturedImage
      })

      if (response.data.success) {
        setMessage(response.data.message)
        setMessageType('success')
        setRegisterName('')
        setCapturedImage(null)
        loadRegisteredFaces()
      } else {
        setMessage(response.data.message)
        setMessageType('error')
      }
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error registering face')
      setMessageType('error')
    } finally {
      setIsRegistering(false)
    }
  }

  const recognizeFace = async () => {
    if (!capturedImage) {
      setMessage('Please capture an image first')
      setMessageType('error')
      return
    }

    setIsRecognizing(true)
    setMessage('')

    try {
      const response = await axios.post(`${API_BASE}/recognize_face`, {
        image: capturedImage
      })

      if (response.data.success) {
        if (response.data.recognized) {
          setRecognitionResult({
            name: response.data.name,
            confidence: response.data.confidence,
            message: response.data.message
          })
          setMessage('')
        } else {
          setRecognitionResult(null)
          setMessage(response.data.message)
          setMessageType('info')
        }
      } else {
        setMessage(response.data.message)
        setMessageType('error')
      }
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error recognizing face')
      setMessageType('error')
    } finally {
      setIsRecognizing(false)
    }
  }

  const deleteFace = async (name) => {
    try {
      const response = await axios.delete(`${API_BASE}/delete_face/${name}`)
      if (response.data.success) {
        setMessage(response.data.message)
        setMessageType('success')
        loadRegisteredFaces()
      } else {
        setMessage(response.data.message)
        setMessageType('error')
      }
    } catch (error) {
      setMessage(error.response?.data?.message || 'Error deleting face')
      setMessageType('error')
    }
  }

  const getMessageColor = () => {
    switch (messageType) {
      case 'success': return 'text-green-600 bg-green-100'
      case 'error': return 'text-red-600 bg-red-100'
      case 'info': return 'text-blue-600 bg-blue-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
          Face Recognition System
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Camera and Controls */}
          <div className="space-y-6">
            {/* Webcam */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">Camera</h2>
              <div className="relative">
                <Webcam
                  ref={setWebcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-64 object-cover rounded-lg"
                />
                {capturedImage && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <img
                      src={capturedImage}
                      alt="Captured"
                      className="max-w-full max-h-full object-contain rounded-lg"
                    />
                  </div>
                )}
              </div>
              
              <div className="flex gap-3 mt-4">
                <button
                  onClick={captureImage}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Capture Image
                </button>
                <button
                  onClick={clearImage}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>

            {/* Face Recognition */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">Face Recognition</h2>
              <button
                onClick={recognizeFace}
                disabled={!capturedImage || isRecognizing}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                {isRecognizing ? 'Recognizing...' : 'Recognize Face'}
              </button>
              
              {recognitionResult && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h3 className="font-semibold text-green-800">Recognition Successful!</h3>
                  <p className="text-green-700">Name: {recognitionResult.name}</p>
                  <p className="text-green-700">Accuracy: {(recognitionResult.confidence * 100).toFixed(1)}%</p>
                </div>
              )}
            </div>

            {/* Face Registration */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">Register New Face</h2>
              <input
                type="text"
                placeholder="Enter person's name"
                value={registerName}
                onChange={(e) => setRegisterName(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg mb-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={registerFace}
                disabled={!capturedImage || !registerName.trim() || isRegistering}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                {isRegistering ? 'Registering...' : 'Register Face'}
              </button>
            </div>
          </div>

          {/* Right Column - Registered Faces and Messages */}
          <div className="space-y-6">
            {/* Messages */}
            {message && (
              <div className={`p-4 rounded-lg border ${getMessageColor()}`}>
                {message}
              </div>
            )}

            {/* Registered Faces */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">Registered Faces</h2>
              {registeredFaces.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No faces registered yet</p>
              ) : (
                <div className="space-y-3">
                  {registeredFaces.map((name, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="font-medium text-gray-800">{name}</span>
                      <button
                        onClick={() => deleteFace(name)}
                        className="text-red-600 hover:text-red-800 font-medium text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-3">How to Use</h3>
              <ol className="list-decimal list-inside space-y-2 text-blue-700">
                <li>Capture an image using the camera</li>
                <li>To register: Enter a name and click "Register Face"</li>
                <li>To recognize: Click "Recognize Face" to identify the person</li>
                <li>View all registered faces in the right panel</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
