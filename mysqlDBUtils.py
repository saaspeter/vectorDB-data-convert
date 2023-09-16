import bizUtils
from ObjectDef import ArticleHealth
import mysql.connector
import yaml


def getDBConnectionFromConfig():
    with open("config.yaml", "r") as f:
        config_data = yaml.load(f, Loader=yaml.FullLoader)
    host = config_data['mysql']['host']
    database = config_data['mysql']['database']
    user = config_data['mysql']['user']
    password = config_data['mysql']['password']
    port = config_data['mysql']['port']
    if not host or not database or not user or not password or not port:
        raise ValueError('db connection dict missing in getSourceListForDetailJob')

    connection = mysql.connector.connect(host=host, database=database,
                                         user=user, password=password, port=port)
    return connection


# fetch article from DB, because these article is very large, so fetch_size cannot be a large number
def getArticleHealthListFromDB(resource_type, offset, fetch_size=10):
    if fetch_size > 20:
        raise ValueError('fetch_size cannot larger than 20, because each article is so large')
    connection = getDBConnectionFromConfig()
    cursor = connection.cursor()
    table_name = 'kh_disease_article' if resource_type==bizUtils.RESOURCE_TYPE_DISEASE else 'kh_medicine_article'
    query = 'SELECT article_id,name,source_url,language FROM ' + table_name \
            + ' limit '+str(offset)+', '+str(fetch_size)
    cursor.execute(query)
    queryResultList = cursor.fetchall()
    items = []
    for result in queryResultList:
        article_id = result[0]
        name = result[1]
        source_url = result[2]
        language = result[3]
        # get full article in new sql query, because the article is very large
        full_article = getArticleContent(cursor, article_id, resource_type)
        article_obj = ArticleHealth(article_id, name, full_article, resource_type, language, source_url)
        items.append(article_obj)

    return items


def getArticleContent(cursor, article_id, resource_type):
    query_detail_disease = 'SELECT full_article FROM kh_disease_article_detail_text where article_id=%s'
    query_detail_medicine = 'SELECT full_article FROM kh_medicine_article_detail_text where article_id=%s'
    query = query_detail_disease if resource_type == bizUtils.RESOURCE_TYPE_DISEASE else query_detail_medicine
    params = (article_id,)
    cursor.execute(query, params)
    (full_article,) = cursor.fetchone()
    return full_article

