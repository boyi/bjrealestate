from lxml import html
from urlparse import urljoin
import magic
import mimetypes
import requests

def test_for_meta_redirections(r):
    mime = magic.from_buffer(r.content, mime=True)
    extension = mimetypes.guess_extension(mime)
    if extension == '.html':
        html_tree = html.fromstring(r.text)
        attr = html_tree.xpath("//meta[translate(@http-equiv, 'REFSH', 'refsh') = 'refresh']/@content")
        if attr and len(attr) > 0:
            attr = attr[0]
            wait, text = attr.split(";")
            if text.lower().startswith("url="):
                url = text[4:]
                if not url.startswith('http'):
                    # Relative URL, adapt
                    url = urljoin(r.url, url)
                return True, url
    return False, None


def follow_redirections(r, s):
    """
    Recursive function that follows meta refresh redirections if they exist.
    """
    redirected, url = test_for_meta_redirections(r)
    if redirected:
        r = s.get(url)
    return r

def crawl(url):
    s = requests.session()
    r = s.get(url)
    # test for and follow meta redirects
    r = follow_redirections(r, s)
    
    return r

def crawl_and_save(url, outfile):
    r = crawl(url)
    f = open(outfile, 'wb')
    f.write(r.content)
    f.close()
    
    
    
if __name__ == "__main__":
    crawl_and_save('http://baidu.com', 'out.tmp')
    