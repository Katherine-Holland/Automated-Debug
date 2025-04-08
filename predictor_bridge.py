import sys
import tensorflow as tf
import joblib
import numpy as np

# Load model and scaler
model = tf.keras.models.load_model('bug_predictor_model.keras')
scaler = joblib.load('bug_scaler.save')

# Get input features from command-line arguments
# Usage: python predictor_bridge.py headline_length load_time missing_elements
try:
    headline_length = float(sys.argv[1])
    load_time_ms = float(sys.argv[2])
    missing_elements = float(sys.argv[3])
except (IndexError, ValueError):
    print("Error: You must provide three numerical arguments.")
    sys.exit(1)

# Prepare and scale input
input_data = np.array([[headline_length, load_time_ms, missing_elements]])
scaled_data = scaler.transform(input_data)

# Predict
prediction = model.predict(scaled_data)
bug_likelihood = prediction[0][0]

# Print just the numeric prediction so Node.js can read it
print(bug_likelihood)