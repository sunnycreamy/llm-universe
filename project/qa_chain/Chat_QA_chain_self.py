from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

from model_to_llm import model_to_llm
from get_vectordb import get_vectordb


class Chat_QA_chain_self:
    """"
    带历史记录的问答链  
    - model：调用的模型名称
    - temperature：温度系数，控制生成的随机性
    - top_k：返回检索的前k个相似文档
    - chat_history：历史记录，输入一个列表，默认是一个空列表
    - history_len：控制保留的最近 history_len 次对话
    - file_path：建库文件所在路径
    - persist_path：向量数据库持久化路径
    - appid：星火
    - api_key：所有模型都需要
    - api_secret：星火、百度文心
    - embeddings：使用的embedding模型  
    """
    def __init__(self,model:str, temperature:float=0.0, top_k:int=4, chat_history:list=[], history_len:int=0, file_path:str=None, persist_path:str=None, appid:str=None, api_key:str=None, api_secret:str=None, embedding = "openai"):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.chat_history = chat_history
        self.history_len = history_len
        self.file_path = file_path
        self.persist_path = persist_path
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.embedding = embedding


        self.vectordb = get_vectordb(self.file_path, self.persist_path, self.api_key, self.embedding)
        self.llm = model_to_llm(self.model, self.temperature, self.appid, self.api_key, self.api_secret)

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.retriever = self.vectordb.as_retriever(search_type="similarity",   
                                        search_kwargs={'k': self.top_k})  #默认similarity，k=4

        self.qa = ConversationalRetrievalChain.from_llm(
            llm = self.llm,
            retriever = self.retriever,
            memory = self.memory
        )
    
    def clear_history(self):
        "清空历史记录"
        return self.chat_history.clear()

    
    def change_history_length(self,):
        """
        保存指定对话轮次的历史记录
        输入参数：
        - history_len ：控制保留的最近 history_len 次对话
        - chat_history：当前的历史对话记录
        输出：返回最近 history_len 次对话
        """
        n = len(self.chat_history)
        return self.chat_history[n-self.history_len:n]

 
    def answer(self, question:str=None):
        """"
        核心方法，调用问答链
        arguments: 
        - question：用户提问
        """
        if len(question) == 0:
            return "", self.chat_history

        #print(self.llm)
        result = self.qa({"question": question})     
        self.chat_history.append((question,result['answer'])) #更新历史记录

        return result['answer'],self.chat_history  #返回本次回答和更新后的历史记录



    
        
        
















