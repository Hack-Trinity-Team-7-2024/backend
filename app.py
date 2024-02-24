from flask import Flask, jsonify, request
import langchain


app = Flask(__name__)


# flask isn't broken strangely
@app.route("/helloworld", methods=['GET'])
def helloworld():
    if (request.method == 'GET'):
        data = {"data": "Greetings mother"}
        return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)