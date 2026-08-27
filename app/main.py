import requests
from flask import Flask, request, jsonify
from app.parser import parse_eml_bytes, EmailParserError

app = Flask(__name__)

@app.route('/parse', methods=['POST'])
def parse_endpoint():
    """
    Endpoint to parse an EML file uploaded via multipart/form-data.
    Expects a single file field named 'file'.
    """
    # Check if the request content type is multipart/form-data
    if not request.is_multipart():
        return jsonify({"error": "Unsupported media type. Must be multipart/form-data."}), 415

    # Retrieve the file from form data
    files = request.files.getlist('file')
    if not files or (len(files) == 1 and not files[0].filename):
        return jsonify({"error": "Missing 'file' parameter in multipart/form-data."}), 400

    # Use the first file found, assuming only one is expected
    uploaded_file = files[0]
    eml_bytes = uploaded_file.read()
    
    try:
        # Use the robust parser function
        parsed_data = parse_eml_bytes(eml_bytes)

        # Prepare response structure, ensuring compatibility with existing JSON contract
        response = {
            "success": True,
            "metadata": parsed_data["metadata"],
            "body": parsed_data["body"],
            "attachments": [
                {
                    "filename": att.get("filename"),
                    "content_type": att.get("content_type"),
                    "size": att.get("size"),
                    # Note: Content is returned as a string representation of the decoded data
                    "content": att.get("content") 
                } for att in parsed_data["attachments"]
            ]
        }

        return jsonify(response), 200

    except EmailParserError as e:
        print(f"Parsing Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({"success": False, "error": f"An unexpected error occurred during parsing: {str(e)}"}), 500

if __name__ == '__main__':
    # Running the app for local testing (not used by the API call)
    app.run(debug=True)