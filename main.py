import bizUtils
import vectorDBUtils


def testQuery(collection):
    """
    query some data according the attributes to verify the adding data process is successful
    :param collection:
    :return:
    """
    print("db items number:{}".format(collection.count()))
    #items = collection.get(ids=['1_62', '1_102', '1_10001', '1_20179'])
    items = collection.get(ids=['2_1', '2_1790'], include=["embeddings","metadatas","documents"])
    print(items["ids"])
    print(items['metadatas'])
    print(items['embeddings'])
    print(items['documents'])


def main_entrance():
    """
    this is the program entrance, first add data to vectorDB collection
    then search the data in vectorDB to verify the process,
    either with method: testQuery or vectorDBUtils.testQueryByText
    :return:
    """
    collection_name = vectorDBUtils.DISEASEMEDICINE_COLLECTION
    collection = vectorDBUtils.getCollection(collection_name)
    print('========collection.name:'+collection.name)
    # add operation
    print('========> begin to processing disease data:')
    vectorDBUtils.addDataToCollectionFromMysql(collection, bizUtils.RESOURCE_TYPE_DISEASE, -1)

    # query1: query by attribute value, e.g: attribute id
    testQuery(collection)

    # test2: query by the question content, control the accuracy by the distance value
    #vectorDBUtils.testQueryByText(collection)


main_entrance()
