import asyncio
import os
import sys

import langchain
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

# from langchain.chat_models import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import LLMResult
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
    def __init__(self):
        self.content: str = ""
        self.final_answer: bool = False
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()

    async def on_llm_new_token(self, token: str, **kwargs: any) -> None:
        self.content += token
        # if we passed the final answer, we put tokens in queue
        if self.final_answer:
            if '"action_input": "' in self.content:
                if token not in ['"', "}"]:
                    self.queue.put_nowait(token)
        elif "Final Answer" in self.content:
            self.final_answer = True
            self.content = ""

    async def on_llm_end(self, response: LLMResult, **kwargs: any) -> None:
        if self.final_answer:
            self.content = ""
            self.final_answer = False
            self.done.set()
        else:
            self.content = ""


llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0.0,
    model="gpt-3.5-turbo",
    # max_tokens=100,
    streaming=True,
    callbacks=[],
)

# initialize conversational memory
memory = ConversationBufferWindowMemory(
    memory_key="chat_history", k=5, return_messages=True, output_key="output"
)


# initialize the agent
agent = initialize_agent(
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    tools=[],
    llm=llm,
    memory=memory,
    verbose=True,
    max_iterations=3,
    early_stopping_method="generate",
    return_intermediate_steps=False,
)


async def run_call(query: str, stream_it: AsyncCallbackHandler):
    agent.agent.llm_chain.llm.callbacks = [stream_it]
    response = await agent.acall(inputs={"input": query})
    return response


async def create_gen(query: str, stream_it: AsyncCallbackHandler):
    task = asyncio.create_task(run_call(query, stream_it))
    async for token in stream_it.aiter():
        yield token
    await task
