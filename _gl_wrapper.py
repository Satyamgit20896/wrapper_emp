from flask import Flask, request, jsonify
import requests
import urllib3

# Flask app start
app = Flask(__name__)

# SSL warning disable (verify=False ke liye)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@app.route("/test-follow-up", methods=["POST"])
def post_follow_up():
    data = request.get_json()

    url = "https://lmsssl.landmarkbic.com/api/follow-up"
    headers = {
        "Content-Type": "application/json"
        # "Authorization": "Bearer YOUR_TOKEN"  # Uncomment if needed
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        return jsonify({
            "status_code": response.status_code,
            "response": response.json()
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
