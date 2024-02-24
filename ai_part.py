import dotenv 
import langchain
from langchain_openai import ChatOpenAI
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser



dotenv.load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0) 
output_parser = StrOutputParser()

def task_expanding(task: str):
    prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are helping someone clarify a task.
     A task will be input and you are to give it a title and short description as if it were a task card.
     Format your output in the form of JSON.
     You are to keep the description brief and broad."""),
    ("user", "{input}")
    ])
    chain = prompt | llm | output_parser
    output = chain.invoke({"input": task})
    return output


def task_breakdown(task: str):
    prompt = ChatPromptTemplate.from_messages({
        ("system", 
        """You are an expert at breaking down tasks.
        A task will be given to you and you are to break it down into granular sub-tasks
        Format your output in the form of JSON containing the Task, and the list of Sub-Tasks.
        You are to keep the sub-tasks in brief bulletpoints format.
        Sub-tasks cannot have their own sub-tasks."""),
        ("user", "{input}")
    })
    chain = prompt | llm | output_parser
    output = chain.invoke({"input": task})
    return output


def task_recreate_breakdown(task: dict, user_message: str):
    """
    Asks the AI to regenerate a list of subtasks, given a list of subtasks and 
    an explanation as to why they are unsuitable.

    :param task: dict containing the Task name and list of unsuitable sub-tasks
    :param user_message: User-submitted prompt detailing what about sub-tasks needs to be changed
    """

    prompt = ChatPromptTemplate.from_messages({
        ("system", 
        """You are an expert at breaking down tasks.
        A Task will be given to you in a JSON format with accompanying Sub-Tasks.
        The user would like you to re-create the Sub-Tasks for the given Task in JSON
        giving the existing Task name and the re-created Sub-Tasks
        and has given feedback.
        Make sure the JSON formatting is the exact same"""),
        ("user", "{task_title}"),
        ("user",  "{subtasks}"),
        ("user", "{feedback}")
    })
    chain = prompt | llm | output_parser
    output = chain.invoke({"task_title": task["Task"],
                           "subtasks": [subtask for subtask in task["Sub-Tasks"]],
                           "feedback": user_message})
    return output

if __name__ == '__main__':
    output = task_breakdown("I want learn how to create a RESTful API.")
    print(output)
    output2 = task_recreate_breakdown(json.loads(output), "Please do it with Express.js")
    print(output2)