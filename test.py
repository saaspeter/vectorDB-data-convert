import yaml
import mysql.connector


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


connection = getDBConnectionFromConfig()
cursor = connection.cursor()
query = 'SELECT article_id,name,source_url,language FROM kh_disease_article limit 1'
cursor.execute(query)
queryResultList = cursor.fetchall()
for result in queryResultList:
    name = result[1]
    print(name)
