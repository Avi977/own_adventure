#LLMs like CHAT GPT are very bad at recalling stuff
#We want to INJECT the data into the model and let the answers be based on those previous prompts
#Retrieval Agumented Generation (RAG) RLLM
#requires a super fast DB so we used a free vector Database by DATASTAX ie; ASTRA CASSANDRA DB instead of a tabular DB

#AstraCS:MFiNBQgWUapeCBlEDEfYotas:0593a1c71f7e0e6cdcc7ab0b177fbbba12e21dc36855054a68fd835af592bb0d

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain_openai import OpenAI
from  langchain.chains import LLMChain
from  langchain.prompts import PromptTemplate
import json

cloud_config= {
    'secure_connect_bundle': 'secure-connect-own-adventure.zip'
}
with open("own_adventure.json") as f:
    secrets = json.load(f)
CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE="default_keyspace"
OPENAI_API_KEY="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"
# OPENAI_API_KEY="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"

auth_provider = PlainTextAuthProvider (CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history =CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600#timetolive
)
message_history.clear()#for a new set of memory for every game

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

template = """
I am making a game for the user to choose their adventure. I will take in user inputs as paths that the player takes.
You are a guide to a game where the player(traveller)  has just been reincarnated to a mythical world with mysterious creatures and powers.
This world also contains magic and demons. Your job is to help the traveller find a path that leads to the demon lord and defeat him.
Help the traveller find mysterious items,weapons and help them grow to be strong enough for tough battles. 
Here are the rules of the game:
1. Start by describing the dire situation of the world and asking the players their weapon of choice.
2. Give the traveler 3 options they can pick from to continue their path everytime
3. If the traveler chooses to leave or end the game, or if they make a fatal descision, make sure to give a reply containing "The End." 

I will be looking for this text to end the program
Here is the chat history, use this to understand what to say next but don't print the same conversation: 
chat history: {chat_history}
player response: {human_input}
"""


prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

#initialize a connection
llm=OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain=LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)
choice="start"

while True:
    response = llm_chain.predict( human_input=choice)
    print(response.strip())   
    if "The End." in response or 'altf4' in choice:
        break
    choice=input("Your Reply :")
