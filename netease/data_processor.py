import re
import html

def process_articles(articles):
    """处理文章数据，清理HTML内容"""
    processed = []
    
    for article in articles:
        processed_article = article.copy()
        
        # 处理HTML文本，保留<br>标签
        processed_article['text'] = process_html_text(article['text'])
        
        processed.append(processed_article)
    
    return processed

def process_html_text(html_content):
    """处理HTML文本内容，仅保留安全标签"""
    if not html_content:
        return ''
    
    # 保留<br>标签，移除其他HTML标签
    processed_text = re.sub(r'<a[^>]*data-action="activity"[^>]*>(.*?)</a>', r'\1', html_content)
    
    # 保留<br>标签但去除其他标签
    processed_text = re.sub(r'<(?!br\s*/?>)[^>]+>', '', processed_text)
    
    return processed_text

def plain_text_from_html(html_content):
    """从HTML中提取纯文本"""
    if not html_content:
        return ''
    
    text = re.sub(r'<br\s*/?>', '\n', html_content)
    
    text = re.sub(r'<[^>]+>', '', text)
    
    text = html.unescape(text)
    
    return text