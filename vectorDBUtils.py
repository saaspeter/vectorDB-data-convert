import chromadb
from langchain.vectorstores import Chroma
from chromadb.utils import embedding_functions
import mysqlDBUtils
import llmUtil
from ObjectDef import ArticleHealth
import time

DISEASEMEDICINE_COLLECTION = 'Disease_Medicine_Collection'


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


# def getEmbeddingFunction():
#     return SentenceTransformerEf().sentence_transformer_ef

def getEmbeddingFunction():
    # this is default embedding function, all-MiniLM-L6-v2 of Sentence Transformers
    # default_ef = embedding_functions.DefaultEmbeddingFunction()
    # all-mpnet-base-v2 will have the best quality (https://www.sbert.net/docs/pretrained_models.html)
    # embedding_functions already has cache
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
    return sentence_transformer_ef


@singleton
class ChromaClientEf:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="/Users/peterfan/vectorDB_data/chroma")
        # client.heartbeat()


def getChromaDBClient():
    return ChromaClientEf().client

def getCollectionDefault():
    return getCollection(DISEASEMEDICINE_COLLECTION)

def getCollection(collection_name):
    client = getChromaDBClient()
    # get embedding function
    embed_fun = getEmbeddingFunction()
    collection = client.get_collection(name=collection_name, embedding_function=embed_fun)
    return collection


# if record_size=-1, which means load all mysql db data to vector db
def addDataToCollectionFromMysql(collection, resourceType, record_size):
    batch_size = 20

    loop = True
    # if record_size==-1 or record_size>20:
    # finished_number = 0
    # offset is the finished number
    offset = 0

    start_time = time.time()
    batch_start_time = start_time
    print("---- begin to insert data to chroma, total number: {}".format(record_size))
    while loop:
        fetch_number = batch_size if (record_size - offset > batch_size) or record_size == -1 else record_size - offset
        # get data from DB
        healthObj_list = mysqlDBUtils.getArticleHealthListFromDB(resourceType, offset, fetch_number)
        if healthObj_list and len(healthObj_list) > 0:
            # add to chroma db collection
            addDataToCollection(collection, healthObj_list)

            offset += len(healthObj_list)
            if len(healthObj_list) < batch_size or (record_size != -1 and offset >= record_size):
                loop = False

            if offset % 100 == 0 and offset != 0:
                print('---- processing the data to chroma, offset: {}, this batch time cose: {}'
                      .format(offset, time.time() - batch_start_time))
                batch_start_time = time.time()
        else:
            loop = False

    print("---- finished all data to chroma, target data number: {}, finished number: {}, time cose: {}"
          .format(record_size, offset, time.time() - start_time))


def addDataToCollection(collection, obj_list: list[ArticleHealth]):
    if not obj_list or len(obj_list) < 1:
        return
    embed_fun = getEmbeddingFunction()
    embeddings_index = embed_fun([obj.getDocument() for obj in obj_list])
    collection.add(
        documents=[obj.getDocument() for obj in obj_list],
        embeddings=embeddings_index,
        metadatas=[obj.getMetaData() for obj in obj_list],
        ids=[obj.getVectorId() for obj in obj_list]
    )


def testQueryByText(collection):
    """
    query some data according the question content, we can filter the result by distance,
    if the distance is less than 0.7, keep the record, otherwise discard it due to the accuracy

    :param collection:
    :return:
    """
    # question1 is the text from sepsis, but the result is not good
    question1 = 'Fast and shallow breathing,Sweating for no clear reason,Feeling lightheaded,Shivering,Strong sleepiness or hard time staying awake'
    question2 = 'I felt dizzy, shaky, unable to stand and sweating for no reason and Shivering sometimes'
    # still give the result, but all the distances larger than 0.8
    question3 = 'bad man'
    # metadata={"hnsw:space": "cosine"}  # l2 is the default
    question4 = 'flatfeet'
    question1_medicine = "what usage of Down syndrome?"

    question = question1_medicine
    start_time = time.time()
    result = collection.query(
        query_texts=[question],
        n_results=5,
        # where={"resource_type": bizUtils.RESOURCE_TYPE_DISEASE}
        # ,where_document={"$contains": "search_string"}
    )
    end_time = time.time()
    print("---- query time cose: {}".format(end_time - start_time))

    print(result['ids'])
    print(result['distances'])
    print([item["name"] for item in result['metadatas'][0]])

    # filter out high distance, only show result with distance less than 0.7
    distances_arr = result['distances'][0]
    final_result = []
    for index, distance in enumerate(distances_arr):
        if distance < 0.7:
            tuple_temp = (result['ids'][0][index], result['metadatas'][0][index]["name"], distance)
            final_result.append(tuple_temp)
    # print final result
    print("-------- final query result --------")
    if final_result:
        for item in final_result:
            print("%s , %s , %s" % (item[0], item[1], item[2]))
    else:
        print('no related answer, please try to ask by another way!')


def queryByChromaNative(question, score: float, k: int):
    collection = getCollectionDefault()
    start_time = time.time()
    result = collection.query(
        query_texts=[question],
        n_results=5,
        # where={"resource_type": bizUtils.RESOURCE_TYPE_DISEASE}
        # ,where_document={"$contains": "search_string"}
    )
    end_time = time.time()
    print("---- query time cose: {}".format(end_time - start_time))

    print(result['ids'])
    print(result['distances'])
    print([item["name"] for item in result['metadatas'][0]])

    # filter out high distance, only show result with distance less than 0.7
    distances_arr = result['distances'][0]
    final_result = []
    for index, distance in enumerate(distances_arr):
        if distance < 0.7:
            tuple_temp = (result['ids'][0][index], result['metadatas'][0][index]["name"], distance)
            final_result.append(tuple_temp)


# use langchain chroma search with score filtering, see:
# https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore
def queryByLangChainChroma(question, score: float, k: int):
    chroma_client = getChromaDBClient()
    embeddings = llmUtil.getSentenceTransformerEmbeddings()
    chroma_vectorstore = Chroma(collection_name=DISEASEMEDICINE_COLLECTION,
                                client=chroma_client, embedding_function=embeddings)
    retriever = chroma_vectorstore.as_retriever(search_type="similarity_score_threshold",
                                                search_kwargs={"score_threshold": score, "k": k})

    docs = retriever.get_relevant_documents(question)
    return docs

