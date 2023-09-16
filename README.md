# vectorDB-data-convert

load data from mysqlDB then add the data into Chroma vector db, then do some query verification

the program's entrance is in: main.py, method: main_entrance(), for detail, see the method comments.

the mysql db schema is for my personal project about health, so you need change the data schema for your project.
the file is in: mysqlDBUtils.py, the mysql connection is in config.yaml file.

so the steps are:

1. create a chroma db collection. run createCollection.py
2. load data from mysql to chroma. run main.py
