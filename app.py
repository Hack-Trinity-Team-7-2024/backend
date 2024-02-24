from flask import Flask, jsonify, request
import langchain


tasks = []


app = Flask(__name__)


# flask isn't broken strangely
@app.route("/helloworld", methods=['GET'])
def helloworld():
    if (request.method == 'GET'):
        data = {"data": "Greetings mother"}
        return jsonify(data)


@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def add_task():
    task = request.get_json()
    tasks.append(task)
    return task


if __name__ == '__main__':
    app.run(debug=True)