import aiohttp
import base64
from .data_processor import plain_text_from_html

async def export_to_html(articles, file_path, settings, ui):
    """将文章导出为HTML文件，显示详细进度"""
    ui.add_update('status', message="开始准备导出HTML...")
    html_content = await generate_html_content(articles, settings, ui)
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    ui.add_update('status', message=f"已成功导出到 {file_path}")
    return file_path

def copy_to_clipboard(articles):
    """将文章作为纯文本复制到剪贴板"""
    copy_text = []
    
    for article in articles:
        # 处理时间
        time_text = article['time']
        
        # 将HTML文本转换为纯文本
        plain_text = plain_text_from_html(article['text'])
        
        # 组合文本
        article_text = f"{time_text}\n{plain_text}"
        copy_text.append(article_text)
    
    result = "\n\n".join(copy_text)
    return result

async def convert_image_to_base64(url, session):
    """将图片URL转换为base64格式"""
    if not url:
        return ""
    
    try:
        # 确保URL使用https协议
        secure_url = url.replace("http:", "https:")
        
        async with session.get(secure_url) as response:
            if response.status == 200:
                image_data = await response.read()
                # 转换为base64
                base64_data = base64.b64encode(image_data).decode('utf-8')
                # 获取MIME类型
                content_type = response.headers.get('Content-Type', 'image/jpeg')
                return f"data:{content_type};base64,{base64_data}"
            else:
                print(f"获取图片失败: {response.status} {secure_url}")
                return ""
    except Exception as e:
        print(f"转换图片为base64时出错: {e}, URL: {url}")
        return ""

async def generate_html_content(articles, settings, ui):
    """生成HTML内容，处理图片为base64格式，显示详细进度"""
    html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
    html += '<meta charset="UTF-8">\n'
    html += '<title>网易云音乐动态导出</title>\n'
    html += '<style>\n'
    html += 'body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }\n'
    html += '.article { border-bottom: 1px solid #eee; padding: 20px 0; }\n'
    html += '.time { color: #888; margin-bottom: 10px; }\n'
    html += '.text { white-space: pre-wrap; line-height: 1.6; }\n'
    html += '.song { background-color: #f7f7f7; padding: 10px; margin: 10px 0; border-radius: 5px; }\n'
    html += '.song a { color: #0c73c2; text-decoration: none; }\n'
    html += '.song a:hover { text-decoration: underline; }\n'
    html += '.images { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }\n'
    html += f'.images img {{ width: {settings["imageSize"]}px; height: {settings["imageSize"]}px; object-fit: cover; border-radius: 3px; cursor: pointer; }}\n'
    html += '.lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; }\n'
    html += '.lightbox img { max-width: 90%; max-height: 90%; object-fit: contain; }\n'
    html += '.close-lightbox { position: absolute; top: 20px; right: 20px; color: white; font-size: 30px; cursor: pointer; }\n'
    html += '</style>\n'
    html += '<script>\n'
    html += 'function openLightbox(imgSrc) {\n'
    html += '  const lightbox = document.getElementById("lightbox");\n'
    html += '  const lightboxImg = document.getElementById("lightbox-img");\n'
    html += '  lightboxImg.src = imgSrc;\n'
    html += '  lightbox.style.display = "flex";\n'
    html += '}\n'
    html += 'function closeLightbox() {\n'
    html += '  document.getElementById("lightbox").style.display = "none";\n'
    html += '}\n'
    html += '</script>\n'
    html += '</head>\n<body>\n'

    # 添加灯箱元素
    html += '<div id="lightbox" class="lightbox" onclick="closeLightbox()">\n'
    html += '  <span class="close-lightbox">&times;</span>\n'
    html += '  <img id="lightbox-img" src="" alt="大图">\n'
    html += '</div>\n'

    # 计算总图片数量
    total_images = 0
    for article in articles:
        if article.get('images'):
            total_images += len(article['images'])
    
    ui.add_update('status', message=f"共有 {total_images} 张图片需要处理")
    
    # 创建HTTP会话
    async with aiohttp.ClientSession() as session:
        # 当前处理的图片计数
        current_image = 0
        
        # 处理每篇文章
        for article_idx, article in enumerate(articles):
            html += '<div class="article">\n'

            # 时间
            html += f'<div class="time">{article["time"]}</div>\n'

            # 文本内容 - 直接使用HTML内容，保留<br>标签
            html += f'<div class="text">{article["text"]}</div>\n'

            # 歌曲信息（如果有）
            if article.get('song'):
                song = article['song']
                html += '<div class="song">\n'
                html += f'<div><a href="{song["url"]}" target="_blank">{song["title"]}</a></div>\n'
                html += f'<div>歌手: <a href="{song["artistUrl"]}" target="_blank">{song["artist"]}</a></div>\n'
                html += '</div>\n'

            # 图片（如果有）
            if article.get('images') and len(article['images']) > 0:
                html += '<div class="images">\n'
                for img_idx, image_url in enumerate(article['images']):
                    current_image += 1
                    
                    # 更新UI状态
                    ui.add_update('status', message=f"正在处理图片 ({current_image}/{total_images}): 文章 {article_idx+1}, 图片 {img_idx+1}")
                    
                    # 清理URL
                    clean_url = image_url.split('?')[0].replace('http:', 'https:')
                    
                    if clean_url:
                        if settings['useBase64Images']:
                            # 转换为base64格式
                            try:
                                base64_image = await convert_image_to_base64(clean_url, session)
                                if base64_image:
                                    html += f'<img src="{base64_image}" alt="图片" loading="lazy" onclick="openLightbox(\'{base64_image}\')" />\n'
                                    ui.add_update('status', message=f"图片 {current_image}/{total_images} 下载成功")
                                else:
                                    ui.add_update('status', message=f"图片 {current_image}/{total_images} 下载失败")
                            except Exception as e:
                                ui.add_update('status', message=f"图片 {current_image}/{total_images} 处理出错: {str(e)}")
                        else:
                            # 使用原始URL
                            html += f'<img src="{clean_url}" alt="图片" loading="lazy" onclick="openLightbox(\'{clean_url}\')" onerror="this.style.display=\'none\';" />\n'
                            ui.add_update('status', message=f"图片 {current_image}/{total_images} 添加完成")
                
                html += '</div>\n'

            html += '</div>\n'

    html += '</body>\n</html>'
    return html