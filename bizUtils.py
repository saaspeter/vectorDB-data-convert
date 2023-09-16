from bs4 import BeautifulSoup

RESOURCE_TYPE_MEDICINE = 1
RESOURCE_TYPE_DISEASE = 2

LANGUAGE_CHINESE = 'zh'
LANGUAGE_ENGLISH = 'en'

# extract the pure text from html content
def extractTextFromHtml(html_content: str) -> str:
    if not html_content:
        return html_content
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.text
    # text = soup.get_text() // also can use this method, need review the finial result effect.
    return text


def formatVectorDBId(resource_type, article_id):
    return str(resource_type)+'_'+str(article_id)


def getArticleTupleFromVectorDBId(vectorDB_id: str):
    if vectorDB_id:
        arr = vectorDB_id.split('_')
        if len(arr) == 2:
            return arr[0], arr[1]
    raise ValueError('the value of vectorDB_id is wrong', vectorDB_id)

