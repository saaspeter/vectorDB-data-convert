from langchain.chat_models import ChatOpenAI
from langchain.embeddings import SentenceTransformerEmbeddings
from chromadb.utils import embedding_functions
from annotationUtil import singleton
from langchain.chains import LLMChain

def getChatModel():
    # max_tokens in response
    return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=500)


# SentenceTransformerEmbedding in chromadb definition, model: all-mpnet-base-v2
def getEmbeddingFunction_chroma():
    # this is default embedding function, all-MiniLM-L6-v2 of Sentence Transformers
    # default_ef = embedding_functions.DefaultEmbeddingFunction()
    # all-mpnet-base-v2 will have the best quality (https://www.sbert.net/docs/pretrained_models.html)
    # embedding_functions already has cache
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    return sentence_transformer_ef


@singleton
class SentenceTransformerEmbeddings_Factory:
    def __init__(self):
        self.client = SentenceTransformerEmbeddings()


# SentenceTransformerEmbeddings in langchain definition, model: all-mpnet-base-v2
def getSentenceTransformerEmbeddings():
    return SentenceTransformerEmbeddings_Factory().client



def answerByAI_model(chat_model, chat_prompt, question_user):
    chain = LLMChain(
        llm=chat_model,
        prompt=chat_prompt
        # , output_parser=CommaSeparatedListOutputParser()
    )
    answer = chain.run(question_user)
    return answer
