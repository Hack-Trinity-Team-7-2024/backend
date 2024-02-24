from flask import Flask, jsonify, request, Response
import langchain
import ai_part
import json
import time


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
    task["completed"] = False
    task["time"] = time.time_ns()
    
    task_expanded = ai_part.task_expanding(task["content"])
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



@app.get("/api/tasks/completed")
def get_completed_tasks():
    return [task for (_,task) in tasks_db.items() if task["completed"]]


@app.get("/api/tasks/not-completed")
def get_not_completed_tasks():
    return [task for (_,task) in tasks_db.items() if not task["completed"]]


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

@app.post("/api/tasks/recreate/<int:id>")
def recreate_task(id):
    # Given a task id and message, recreates the sub-tasks for that task id in accordance 
    # with the message
    if id not in tasks_db:
        return Response(status=404)
    
    input = request.get_json()
    task = tasks_db[id]['content']
    recreated_task = ai_part.task_recreate_breakdown(task_name=task, user_message=input["message"])
    print(recreated_task)
    print(type(recreated_task))
    print(json.loads(recreated_task))
    return recreated_task

if __name__ == '__main__':
    app.run(debug=True)