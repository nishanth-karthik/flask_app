# --- File to be deployed on Render ---
# render_app.py

import os
import base64
from flask import Flask, request, jsonify
from supabase import create_client, Client

# --- Supabase Configuration ---
# Use environment variables for security
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Ensure the environment variables are set before creating the client
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase environment variables are not set. Please check your Render dashboard.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route('/upload-data', methods=['POST'])
def upload_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        detected_counts = data.get("detected", {})
        missing_objects = data.get("missing", [])
        image_data_b64 = data.get("image_data", "")
        timestamp = data.get("timestamp", "")

        # Decode the Base64 image data
        image_bytes = base64.b64decode(image_data_b64)

        detected_str = ", ".join([f"{k}:{v}" for k, v in detected_counts.items()])
        missing_str = ", ".join(missing_objects)

        supabase_data = {
            "timestamp": timestamp,
            "detected_objects": detected_str,
            "missing_objects": missing_str,
            "annotated_image_b64": image_data_b64 
        }
        
        # Insert data into Supabase table
        response = supabase.table("render_data_log").insert(supabase_data).execute()
        
        print(f"[Render] Data received and inserted into Supabase. Response: {response}")
        return jsonify({"message": "Data received and saved successfully"}), 200

    except Exception as e:
        print(f"[Render Error] An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
