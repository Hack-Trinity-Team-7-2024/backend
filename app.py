from flask import Flask, jsonify, request
import langchain


tasks_db = {}
last_task_id = 0


app = Flask(__name__)


# flask isn't broken strangely
@app.route("/helloworld", methods=['GET'])
def helloworld():
    if (request.method == 'GET'):
        data = {"data": "Greetings mother"}
        return jsonify(data)


@app.get("/tasks")
def get_tasks():
    return list(tasks_db.values())

@app.post("/tasks")
def add_task():
    global last_task_id

    task = request.get_json()

    id = last_task_id
    last_task_id += 1

    task["id"] = id
    tasks_db[id] = task

    return {"id": last_task_id}

@app.get("/tasks/<int:id>")
def get_task(id):
    return tasks_db[id]

@app.patch("/tasks/<int:id>")
def patch_task(id):
    task = tasks_db[id]
    patch = request.get_json()

    task.update(patch)

    return task


if __name__ == '__main__':
    app.run(debug=True)