from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BASE_URL = "https://script.google.com/macros/s/AKfycbwtb-odKPCjZlLm5iU4PreWQfXTZ2XmRdk9UjxgprCExnKvKVwlYYkSBPhXDhKYLOInvg/exec"

@app.route("/get-user-info", methods=["GET"])
def get_user_info():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "Missing 'id' parameter"}), 400

    try:
        response = requests.get(BASE_URL, params={"id": user_id})
        data = response.json()

        if not data:
            return jsonify({"error": "No data found for given ID"}), 404

        user = data[0]  # Since it's a list with one dict
        return jsonify({
            "name": user.get("name"),
            "department": user.get("department")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
