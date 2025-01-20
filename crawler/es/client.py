import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv(verbose=True)


class ElasticSearch:
    def __init__(self):
        self.client = Elasticsearch(
            hosts=['http://localhost:9200'],
            api_key=os.getenv('ELASTICSEARCH_API_KEY'),
        )

    def create_index(self, index_name):
        self.client.indices.create(index=index_name, ignore=400)

    def delete_index(self, index_name):
        self.client.indices.delete(index=index_name, ignore=[400, 404])

    def insert_data(self, index_name, data):
        response = self.client.index(index=index_name, document=data)
        return response

    def search(self, index_name, query):
        response = self.client.search(index=index_name, body=query)
        return response


es_client = ElasticSearch()
