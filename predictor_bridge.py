import sys
import tensorflow as tf
import joblib
import numpy as np

# Load model and scaler
model = tf.keras.models.load_model('bug_predictor_model.keras')
scaler = joblib.load('bug_scaler.save')

# Get command-line arguments and validate
if len(sys.argv) != 4:
    print("Error: You must provide three numerical arguments.")
    sys.exit(1)

try:
    headline_length = float(sys.argv[1])
    load_time_ms = float(sys.argv[2])
    missing_elements = float(sys.argv[3])
except ValueError:
    print("Error: Invalid number format.")
    sys.exit(1)

# Construct input
input_data = np.array([[headline_length, load_time_ms, missing_elements]])

# Scale input
scaled_data = scaler.transform(input_data)

# Predict
prediction = model.predict(scaled_data)
bug_likelihood = float(prediction[0][0])

# Final output
print(f"{bug_likelihood:.4f}")