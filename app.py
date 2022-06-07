# Inspired by https://code.visualstudio.com/docs/python/tutorial-flask

# Can be tested from the VScode or command line without having to deply the code to GCP.
# To run from command line:
#   $ python -m flask run --port 5000

from flask import Flask
import main

app = Flask(__name__)


@app.route("/")
def home(request):
    return main.stream(request)

if __name__ == '__main__':
    import os
    
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
