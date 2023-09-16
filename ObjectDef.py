import bizUtils

class ArticleHealth:
    def __init__(self, article_id, name, content, resource_type, language, source_url):
        if not article_id or not content or not resource_type or not source_url:
            raise ValueError('article_id and resource_type and source_url must not be empty')
        self.article_id = article_id
        self.name = name
        self.content = content
        self.resource_type = resource_type
        self.language = language if language else ''
        self.source_url = source_url


    def getName(self):
        return self.name

    def getDocument(self):
        return self.content if self.content else ''

    def getArticleId(self):
        return self.article_id

    def getResourceType(self):
        return self.resource_type

    def getVectorId(self):
        return bizUtils.formatVectorDBId(self.resource_type, self.article_id)

    def getMetaData(self):
        meta_data = {
            'name': self.name,
            'resource_type': self.resource_type,
            'language': self.language,
            'source_url': self.source_url
        }
        return meta_data

