import dotenv 
import langchain
from langchain_openai import ChatOpenAI
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re



dotenv.load_dotenv()
#llm = ChatOpenAI(model="gpt-4-0125-preview", temperature = 0.5) 
llm = ChatOpenAI(temperature = 0.5) 
output_parser = StrOutputParser()


def task_expanding_title(task: str):
    prompt = ChatPromptTemplate.from_messages({
    ("system",
     """.
     Write a title for the following task description. Keep it less than 5 words. 
     Do not prepend it with the word "title" or "task". Do not put it in quotes."""),
     ("user", "{task}")
    })
    chain = prompt | llm | output_parser
    title = chain.invoke({"task": task})
    return title

def task_expanding_description(task: str):
    prompt = ChatPromptTemplate.from_messages({
    ("system",
     """You are helping some come up with a description for a task.
     A task blurb will be input and you are to give it an imperative description, 
     briefly describing this task with 1 or 2 sentences but not any advice on how 
     to complete the task. Do not prepend your response with the word "task".
     The task is as follows:"""),
     ("user", "{task}")
    })
    chain = prompt | llm | output_parser
    description = chain.invoke({"task": task})
    return description


def task_expanding(task: str):
    title = task_expanding_title(task)
    description = task_expanding_description(task)
    output = {"title": title, "description": description}
    return output


def task_breakdown(task: str):
    prompt = ChatPromptTemplate.from_messages({
        ("system", 
        """You are an expert at breaking down tasks.
        A task will be given to you and you are to break it down into granular, one-line Sub-Tasks.
        Use as few steps as possible. Enumerate each line."""),
        ("user", "{input}")
    })
    chain = prompt | llm | output_parser
    output = chain.invoke({"input": task})
    output = format_breakdown(output)
    return output

def format_breakdown(text):
    prompt = ChatPromptTemplate.from_messages({
        ('system',
         """
        Given the following list of tasks, format it such that it is a newline separated list
                          """),
        ("user", "{text}")
    })
    chain = prompt | llm | output_parser
    output = chain.invoke({"text": text}).split('\n')
    output = parse_garbage(output)
    output_status = [False] * len(output)
    return {"points": output,
            "points_completed": output_status}


def parse_garbage(tasks:list):
    regex = "^\\d*\\s*[\\-\\.)]?\\s+"
    for i in range(len(tasks)):
        if tasks[i].strip() == "":
            tasks.pop(i)
        if re.match(regex, tasks[i]) or task.strip() == "":
            tasks[i] = re.split(regex, tasks[i])[1]
        
    return tasks


def task_recreate_breakdown(task_name: str, user_message: str):
    """
    Asks the AI to regenerate a list of subtasks, given user feedback.
    task_name is the 'content' field in the header.

    :param task_name
    :param user_message: User-submitted prompt detailing what about sub-tasks needs to be changed
    """
    prompt = ChatPromptTemplate.from_messages({
        ("system", 
        """You are an expert at breaking down tasks.
        A Task title will be given to you and a piece of user-feedback.
        The user would like you to create the Sub-Tasks for the given Task in JSON
        giving the existing Task name and a prompt.
        Make sure it is in JSON with the headers 'content' and 'points' 
        e.g. {{
        points: [*subtask 1*, *subtask 2*, *subtask 3* ....]
        }}
        where content is the Task name, and points is the Sub-Tasks.
        Sub-Tasks cannot have their own Sub-Tasks."""),
        ("user", "{task_title}"),
        ("user", "{feedback}")
    })
    chain = prompt | llm | output_parser

    output = chain.invoke({"task_title": task_name,
                           "feedback": user_message})
    output = format_breakdown(output)
    return output


def task_recreate_breakdown_with_context(task: dict, user_message: str):
    """
    Asks the AI to regenerate a list of subtasks, given its previously generated list of subtasks, anduser feedback.
    task_name is the 'content' field in the header.

    :param task_name
    :param user_message: User-submitted prompt detailing what about sub-tasks needs to be changed
    """

    prompt = ChatPromptTemplate.from_messages({
        ("system", 
        """Recreate the following list of subtasks (might also be called points or tasks):
        """),
        ("user", "{subtask_list}"),
        ("system",
        """
        Using the following context provided:
        """),
        ("user", "{feedback_context}"),
        ("system",
        """
        MAKING SURE that the new subtasks match this description
        """),
        ("user", "{task_description}"),
        ("system",
        """
        Where the theme of the task is:
        """),
        ("user", "{task_title}"),
        ("system", 
        """
        If the context provided is closely related to the current list of subtasks,
        then just recreate the subtasks using the context provided.
        Otherwise, if the context provided is NOT closely related to the current list of subtasks,
        then entirely recreate the subtasks using the context.
        DO NOT regurgitate any of the instructions given to you.
        EMPHASISE the context provided.
        """)
    })
    chain = prompt | llm | output_parser

    # output = chain.invoke({"task_title": task["content"],
    #                        "feedback": user_message})
    output = chain.invoke({"subtask_list": task["points"],
                           "feedback_context": user_message,
                           "task_description": task["description"],
                           "task_title": task["content"]})
    output = format_breakdown(output)
    return output

if __name__ == '__main__':
    output = task_breakdown("I want learn how to create a RESTful API.")
    print(output)
    output2 = task_recreate_breakdown(output, "Please do it with Express.js")
    print(output2)