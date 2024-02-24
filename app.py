from flask import Flask, jsonify, request, Response
import langchain
import ai_part
import json


tasks_db = {}
last_task_id = 0


app = Flask(__name__)


# flask isn't broken strangely
@app.route("/helloworld", methods=['GET'])
def helloworld():
    if (request.method == 'GET'):
        data = {"data": "Greetings mother"}
        return jsonify(data)


@app.get("/api/tasks")
def get_tasks():
    return list(tasks_db.values())

@app.post("/api/tasks")
def add_task():
    global last_task_id

    task = request.get_json()
    
    # Where task["content"] is the initial task the user types in
    task_expanded = ai_part.task_expanding(task["content"])
    task_expanded = json.loads(task_expanded)
    
    task.update(task_expanded)

    id = last_task_id
    last_task_id += 1

    task["id"] = id
    tasks_db[id] = task

    return task


@app.delete("/api/tasks/<int:id>")
def delete_task(id):
    if id in tasks_db:
        del tasks_db[id]
        return Response(status=200)
    
    return Response(status=204)
    


@app.get("/api/tasks/<int:id>")
def get_task(id):
    return tasks_db[id]

@app.patch("/api/tasks/<int:id>")
def patch_task(id):
    task = tasks_db[id]
    patch = request.get_json()

    task.update(patch)

    return task


@app.get("/api/tasks/clarify/<int:id>")
def clarify_task(id):
    task = tasks_db[id]
    return ai_part.task_expanding(task)


@app.get("/api/tasks/breakdown/<int:id>")
def breakdown_task(id):
	task = tasks_db[id]
	return ai_part.task_breakdown(task)


if __name__ == '__main__':
    app.run(debug=True)