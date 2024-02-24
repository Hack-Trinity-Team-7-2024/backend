import dotenv 
import langchain
from langchain_openai import ChatOpenAI
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser



dotenv.load_dotenv()
#llm = ChatOpenAI(model="gpt-4-0125-preview", temperature = 0.5) 
llm = ChatOpenAI(temperature = 0) 
output_parser = StrOutputParser()


def task_expanding_title(task: str):
    prompt = ChatPromptTemplate.from_messages({
    ("system",
     """You are helping someone clarify a task.
     A task will be input and you are to give it a title, briefly describing it."""),
     ("user", "{task}")
    })
    chain = prompt | llm | output_parser
    title = chain.invoke({"task": task})
    return title

def task_expanding_description(task: str):
    prompt = ChatPromptTemplate.from_messages({
    ("system",
     """You are helping someone clarify a task.
     A task blurb will be input and you are to give it an imperative description, briefly describing this task with 1 or 2 sentences."""),
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
        You will generate no more than 6 sub-tasks"""),
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
    output_status = [False] * len(output)
    return {"points": output,
            "points_completed": output_status}

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
        content: *insert content name here*,
        points: [*subtask 1*, *subtask 2*, *subtask 3* ....]
        }}
        where content is the Task name, and points is the Sub-Tasks.
        Sub-Tasks cannot have their own Sub-Tasks."""),
        ("user", "{task_title}"),
        ("user", "{feedback}")
    })
    chain = prompt | llm | output_parser

    output = json.loads(chain.invoke({"task_title": task_name,
                           "feedback": user_message}))
    for i, subtask in enumerate(output['points']):
        output['points'][i] = f"{i+1}. {output['points'][i]}"
    output_status = [False] * len(output['points'])
    output['points_completed'] = output_status
    return output

if __name__ == '__main__':
    output = task_breakdown("I want learn how to create a RESTful API.")
    print(output)
    output2 = task_recreate_breakdown(output, "Please do it with Express.js")
    print(output2)