import chromadb
import vectorDBUtils


client = chromadb.PersistentClient(path="/Users/peterfan/vectorDB_data/chroma")
client.heartbeat()

collection_name = vectorDBUtils.DISEASEMEDICINE_COLLECTION
# this is default embedding function
embed_fun = vectorDBUtils.getEmbeddingFunction()

collection = client.create_collection(name=collection_name, metadata={"hnsw:space": "cosine"},
                                      embedding_function=embed_fun)

# check whether this collection had been created, if cannot get it, will throw an error
client.get_collection(name=collection_name, embedding_function=embed_fun)

print('collection:'+collection_name+' had been created successfully!')
