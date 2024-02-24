import dotenv 
import langchain
from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser



#dotenv.load_dotenv()
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
        Format your output in the form of JSON.
        You are to keep the sub-tasks in brief bulletpoints format."""),
        ("user", "{input}")
    })
    chain = prompt | llm | output_parser
    output = chain.invoke({"input": task})
    return output


output = task_breakdown("I need to build a localhost web proxy for an assignment")
print(output)