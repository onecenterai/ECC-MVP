from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents.types import AgentType
from langchain.schema import HumanMessage, AIMessage

from helpers.model_tools import GetEndpointParams, ApiQuery

def get_task_list(id):
    tasks = Endpoint.get_all(id)
    task_list = ''
    for task in tasks:
        task_list += f' - {task.name} \n'
    return task_list

def qa_chain(question, history=[]):
    #embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    llm = ChatOpenAI()
    
    system_message = f'''
            "You are an Emergency Support Agent"
            "Your job is to respond to callers, by either giving best course of action to take in an emergency, \
            or to forward their call to a human agent"
            
            "Based on the nature on the emergency, you might need to do one of the following"
            
            "- Give best course of action to take in the particular emergency"
            "- Notify the necessary Government agency to handle the emergency"
            "- Forward the caller's call to a human agent"

            
            "You can ask follow-up questions to help you understand the current emergency, and to know the best course of action to take."
            "If you are unsure of how to help, you can forward the call to a human agent"
            "Try to sound as human as possible"
            "Remember callers would most likely be in a distressed state"
            "Make your responses as concise as possible"
            
        '''
    
    tools = [
        GetEndpointParams(),
        ApiQuery()

    ]
    executor = initialize_agent(
        agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,
        # memory=conversational_memory,
        handle_parsing_errors="Check your output and make sure it conforms!",
        agent_kwargs={"system_message": system_message},
        verbose=True,
    )

    q = {"question": question} #+f"\n\nIf the request requires you to query an api here are some available endpoints:`{get_endpoints()}`"}

    chat_history = []
    for h in history:
        chat_history.append(HumanMessage(content=h.question))
        chat_history.append(AIMessage(content=h.answer))

    return executor.run(input=q, chat_history=chat_history)
