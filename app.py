from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS

import src.polyline_obj as OBJSim

app = Flask(__name__)
CORS(app)

# @app.route('/')
# def hello_geek():
#     return '<h1>Hello from Flask & Docker</h2>'


# @app.route('/',methods=['GET'])
# def api():
#     data_set = {'PAGE': 'Home', "MESSAGE": "Successful", "Timestep": time.time()}
#     json_dump = json.dumps(data_set)

#     return json_dump



@app.route('/polyline_obj', methods=['POST'])
def blend():   

    body = request.get_json()

    output = {}

    output["inp"] = OBJSim.main(body["content"], body["result_name"])

    json_dump = json.dumps(output)

    return json_dump


if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 80)