// ==UserScript==
// @name           网易云音乐笔记(动态)备份插件
// @namespace      https://github.com/sansan0/netease-note-backup
// @version        1.4
// @description    提取网易云音乐页面的文字内容，歌曲信息和图片
// @author         sansan
// @match          https://music.163.com/*
// @grant          GM_setClipboard
// @grant          GM_xmlhttpRequest
// @connect        music.163.com
// @connect        p1.music.126.net
// @connect        p2.music.126.net
// @connect        p3.music.126.net
// @license        GPL-3.0 License
// @icon           data:image/png;base64,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
// @noframes       true
// ==/UserScript==

(function() {
    'use strict';

    if (window !== window.top) return;

    const UI_CONTAINER_ID = 'netease-comment-extractor-ui';
    const defaultSettings = {
        imageSize: 100,
        useBase64Images: true
    };

    let userSettings = {...defaultSettings};
    let uiElements = null;
    let hasInitialized = false;
    let articleArray = [];
    let processedIds = new Set();
    let observer = null;
    let hasScrolledToTop = false;
    let isScrollThrottled = false;

    // 创建UI界面
    function createUI() {
        const existingUI = document.getElementById(UI_CONTAINER_ID);
        if (existingUI) existingUI.remove();

        const uiContainer = document.createElement('div');
        uiContainer.id = UI_CONTAINER_ID;
        uiContainer.style.position = 'fixed';
        uiContainer.style.top = '10px';
        uiContainer.style.left = '10px';
        uiContainer.style.zIndex = '9999';
        uiContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        uiContainer.style.padding = '10px';
        uiContainer.style.borderRadius = '5px';
        uiContainer.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.2)';
        uiContainer.style.fontFamily = 'Arial, sans-serif';
        uiContainer.style.fontSize = '14px';

        const countDisplay = document.createElement('div');
        countDisplay.id = 'article-count';
        countDisplay.style.marginBottom = '10px';
        countDisplay.innerText = '已检测到 0 篇文章';

        const rangeContainer = document.createElement('div');
        rangeContainer.style.display = 'flex';
        rangeContainer.style.alignItems = 'center';
        rangeContainer.style.marginBottom = '10px';

        const startRangeInput = document.createElement('input');
        startRangeInput.type = 'number';
        startRangeInput.min = '1';
        startRangeInput.value = '1';
        startRangeInput.style.width = '50px';
        startRangeInput.style.marginRight = '5px';
        startRangeInput.style.padding = '5px';

        const rangeSeparator = document.createElement('span');
        rangeSeparator.innerText = '到';
        rangeSeparator.style.margin = '0 5px';

        const endRangeInput = document.createElement('input');
        endRangeInput.type = 'number';
        endRangeInput.min = '1';
        endRangeInput.value = '1';
        endRangeInput.style.width = '50px';
        endRangeInput.style.marginRight = '10px';
        endRangeInput.style.padding = '5px';

        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'flex';
        buttonContainer.style.alignItems = 'center';
        buttonContainer.style.marginBottom = '10px';

        const copyButton = document.createElement('button');
        copyButton.innerText = '复制';
        copyButton.style.padding = '5px 10px';
        copyButton.style.cursor = 'pointer';
        copyButton.style.marginRight = '10px';

        const maxButton = document.createElement('button');
        maxButton.innerText = '最大';
        maxButton.style.padding = '5px 10px';
        maxButton.style.cursor = 'pointer';

        const settingsContainer = document.createElement('div');
        settingsContainer.style.marginBottom = '10px';
        settingsContainer.style.borderTop = '1px solid #ddd';
        settingsContainer.style.paddingTop = '10px';

        const sizeContainer = document.createElement('div');
        sizeContainer.style.display = 'flex';
        sizeContainer.style.alignItems = 'center';
        sizeContainer.style.marginBottom = '5px';

        const sizeLabel = document.createElement('label');
        sizeLabel.innerText = '图片大小(px): ';
        sizeLabel.style.marginRight = '5px';

        const sizeInput = document.createElement('input');
        sizeInput.type = 'number';
        sizeInput.min = '50';
        sizeInput.max = '500';
        sizeInput.value = userSettings.imageSize;
        sizeInput.style.width = '60px';
        sizeInput.style.padding = '3px';

        const base64Container = document.createElement('div');
        base64Container.style.display = 'flex';
        base64Container.style.alignItems = 'center';

        const base64Checkbox = document.createElement('input');
        base64Checkbox.type = 'checkbox';
        base64Checkbox.checked = userSettings.useBase64Images;
        base64Checkbox.style.marginRight = '5px';

        const base64Label = document.createElement('label');
        base64Label.innerText = '将图片转为base64格式(推荐)';

        const exportContainer = document.createElement('div');
        exportContainer.style.display = 'flex';
        exportContainer.style.alignItems = 'center';

        const exportButton = document.createElement('button');
        exportButton.innerText = '导出HTML';
        exportButton.style.padding = '5px 10px';
        exportButton.style.cursor = 'pointer';

        const statusDisplay = document.createElement('div');
        statusDisplay.style.fontSize = '12px';
        statusDisplay.style.color = '#666';
        statusDisplay.style.marginTop = '5px';
        statusDisplay.innerText = '等待加载...';

        // 组装UI元素
        sizeContainer.appendChild(sizeLabel);
        sizeContainer.appendChild(sizeInput);

        base64Container.appendChild(base64Checkbox);
        base64Container.appendChild(base64Label);

        settingsContainer.appendChild(sizeContainer);
        settingsContainer.appendChild(base64Container);

        rangeContainer.appendChild(startRangeInput);
        rangeContainer.appendChild(rangeSeparator);
        rangeContainer.appendChild(endRangeInput);

        buttonContainer.appendChild(copyButton);
        buttonContainer.appendChild(maxButton);

        exportContainer.appendChild(exportButton);

        uiContainer.appendChild(countDisplay);
        uiContainer.appendChild(rangeContainer);
        uiContainer.appendChild(buttonContainer);
        uiContainer.appendChild(settingsContainer);
        uiContainer.appendChild(exportContainer);
        uiContainer.appendChild(statusDisplay);

        setupInputEvents(sizeInput, base64Checkbox, startRangeInput, endRangeInput, statusDisplay);

        return {
            uiContainer,
            countDisplay,
            startRangeInput,
            endRangeInput,
            copyButton,
            maxButton,
            exportButton,
            statusDisplay,
            sizeInput,
            base64Checkbox
        };
    }

    function setupInputEvents(sizeInput, base64Checkbox, startRangeInput, endRangeInput, statusDisplay) {
        sizeInput.addEventListener('change', function() {
            userSettings.imageSize = parseInt(this.value) || defaultSettings.imageSize;
            statusDisplay.innerText = `已设置图片尺寸为 ${userSettings.imageSize}px`;
        });

        base64Checkbox.addEventListener('change', function() {
            userSettings.useBase64Images = this.checked;
            statusDisplay.innerText = `已${this.checked ? '启用' : '禁用'}图片base64转换`;
        });

        startRangeInput.addEventListener('change', function() {
            const start = parseInt(this.value) || 1;
            const end = parseInt(endRangeInput.value) || 1;
            const total = articleArray.length;

            if (start < 1) {
                this.value = 1;
            } else if (start > total) {
                this.value = total;
            }

            if (start > end) {
                endRangeInput.value = this.value;
            }

            statusDisplay.innerText = `已设置范围: ${this.value} 到 ${endRangeInput.value}`;
        });

        endRangeInput.addEventListener('change', function() {
            const start = parseInt(startRangeInput.value) || 1;
            const end = parseInt(this.value) || 1;
            const total = articleArray.length;

            if (end < 1) {
                this.value = 1;
            } else if (end > total) {
                this.value = total;
            }

            if (end < start) {
                startRangeInput.value = this.value;
            }

            statusDisplay.innerText = `已设置范围: ${startRangeInput.value} 到 ${this.value}`;
        });
    }

    // 等待主文档准备就绪，添加UI
    function addUIToDocument() {
        if (document.body) {
            if (!uiElements) {
                uiElements = createUI();
                document.body.appendChild(uiElements.uiContainer);
                setupUIEvents();
            }
        } else {
            setTimeout(addUIToDocument, 100);
        }
    }

    // 清理图片URL，移除参数
    function cleanImageUrl(url) {
        if (!url) return '';
        return url.split('?')[0].replace(/^http:/, 'https:');
    }

    // 将图片转换为base64格式
    function convertImageToBase64(url) {
        return new Promise((resolve, reject) => {
            if (!url) {
                resolve('');
                return;
            }

            const secureUrl = url.replace(/^http:/, 'https:');

            GM_xmlhttpRequest({
                method: 'GET',
                url: secureUrl,
                responseType: 'blob',
                onload: function(response) {
                    if (response.status === 200) {
                        const reader = new FileReader();
                        reader.onloadend = function() {
                            resolve(reader.result);
                        };
                        reader.onerror = function() {
                            console.error('无法读取图片数据:', secureUrl);
                            resolve('');
                        };
                        reader.readAsDataURL(response.response);
                    } else {
                        console.error('获取图片失败:', response.status, secureUrl);
                        resolve('');
                    }
                },
                onerror: function(error) {
                    console.error('请求图片出错:', error, secureUrl);
                    resolve('');
                }
            });
        });
    }

    // 生成HTML导出内容，处理图片为base64格式
    async function generateHtmlContent(articles) {
        let html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>网易云音乐动态导出</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .article { border-bottom: 1px solid #eee; padding: 20px 0; }
        .time { color: #888; margin-bottom: 10px; }
        .text { white-space: pre-wrap; line-height: 1.6; }
        .song { background-color: #f7f7f7; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .song a { color: #0c73c2; text-decoration: none; }
        .song a:hover { text-decoration: underline; }
        .images { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .images img { width: ${userSettings.imageSize}px; height: ${userSettings.imageSize}px; object-fit: cover; border-radius: 3px; cursor: pointer; }
        .lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; }
        .lightbox img { max-width: 90%; max-height: 90%; object-fit: contain; }
        .close-lightbox { position: absolute; top: 20px; right: 20px; color: white; font-size: 30px; cursor: pointer; }
    </style>
    <script>
        function openLightbox(imgSrc) {
            const lightbox = document.getElementById("lightbox");
            const lightboxImg = document.getElementById("lightbox-img");
            lightboxImg.src = imgSrc;
            lightbox.style.display = "flex";
        }
        function closeLightbox() {
            document.getElementById("lightbox").style.display = "none";
        }
    </script>
</head>
<body>
    <div id="lightbox" class="lightbox" onclick="closeLightbox()">
        <span class="close-lightbox">&times;</span>
        <img id="lightbox-img" src="" alt="大图">
    </div>`;

        for (const article of articles) {
            html += `
    <div class="article">
        <div class="time">${article.time}</div>
        <div class="text">${article.text}</div>`;

            if (article.song) {
                html += `
        <div class="song">
            <div><a href="${article.song.url}" target="_blank">${article.song.title}</a></div>
            <div>歌手: <a href="${article.song.artistUrl}" target="_blank">${article.song.artist}</a></div>
        </div>`;
            }

            if (article.images && article.images.length > 0) {
                html += `
        <div class="images">`;
                for (const image of article.images) {
                    const cleanedUrl = cleanImageUrl(image);
                    if (cleanedUrl) {
                        if (userSettings.useBase64Images) {
                            const base64Image = await convertImageToBase64(cleanedUrl);
                            if (base64Image) {
                                html += `
            <img src="${base64Image}" alt="图片" loading="lazy" onclick="openLightbox('${base64Image}')" />`;
                            }
                        } else {
                            html += `
            <img src="${cleanedUrl}" alt="图片" loading="lazy" onclick="openLightbox('${cleanedUrl}')" onerror="this.style.display='none';" />`;
                        }
                    }
                }
                html += `
        </div>`;
            }

            html += `
    </div>`;
        }

        html += `
</body>
</html>`;
        return html;
    }

    // 获取名称用于导出文件名
    function getExportFileName() {
        const url = window.location.href;
        let userId = '';
        const idMatch = url.match(/[\?&]id=(\d+)/);
        if (idMatch && idMatch[1]) {
            userId = idMatch[1];
        }

        let userName = '';
        try {
            const iframe = document.getElementById('g_iframe');
            if (iframe && iframe.contentDocument) {
                const nameElement = iframe.contentDocument.querySelector('#j-name-wrap');
                if (nameElement) {
                    userName = nameElement.textContent.trim();
                }
            }
        } catch (e) {
            console.error('获取用户名失败:', e);
        }

        if (!userName) {
            userName = '网易云音乐用户';
        }

        return (userId ? userId + '_' : '') + userName.replace(/[\\/:*?"<>|]/g, '_') + '.html';
    }

    // 完全重写下载函数，使用数据URL而不是Blob URL
    function safeDownloadFile(content, filename) {
        try {
            const base64Content = btoa(unescape(encodeURIComponent(content)));
            const dataUrl = `data:text/html;charset=utf-8;base64,${base64Content}`;

            const popupWindow = window.open('', '_blank', 'width=800,height=600');
            if (!popupWindow) {
                alert('下载失败：请允许弹出窗口');
                return false;
            }

            popupWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>下载 - ${filename}</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                        h3 { margin-bottom: 20px; }
                        .button {
                            display: inline-block;
                            padding: 10px 20px;
                            background: #2196F3;
                            color: white;
                            border-radius: 4px;
                            text-decoration: none;
                            margin: 10px;
                            cursor: pointer;
                        }
                    </style>
                </head>
                <body>
                    <h3>文件已准备好下载</h3>
                    <p>文件名: ${filename}</p>
                    <a id="download-link" class="button" href="${dataUrl}" download="${filename}">点击下载</a>
                    <button onclick="window.close()" class="button">关闭窗口</button>
                    <script>
                        setTimeout(function() {
                            document.getElementById('download-link').click();
                        }, 500);
                    </script>
                </body>
                </html>
            `);

            return true;
        } catch (e) {
            console.error('下载文件失败:', e);
            alert('下载失败: ' + e.message);
            return false;
        }
    }

    // 获取选定范围的文章
    function getSelectedArticles() {
        if (!uiElements) return [];

        const start = Math.max(1, parseInt(uiElements.startRangeInput.value) || 1);
        const end = Math.min(articleArray.length, parseInt(uiElements.endRangeInput.value) || 1);

        if (start > end || start > articleArray.length) {
            return [];
        }

        return articleArray.slice(start - 1, end);
    }

    // 处理HTML文本内容，保留<br>等安全标签
    function processHTMLText(htmlContent) {
        if (!htmlContent) return '';

        let processedText = htmlContent;
        processedText = processedText.replace(/<a[^>]*data-action="activity"[^>]*>(.*?)<\/a>/gi, '$1');

        return processedText;
    }

    // 设置UI事件
    function setupUIEvents() {
        if (!uiElements) return;

        uiElements.maxButton.addEventListener('click', function() {
            const articles = updateArticleCount();
            if (articles.length > 0) {
                uiElements.startRangeInput.value = '1';
                uiElements.endRangeInput.value = articles.length;
                uiElements.statusDisplay.innerText = `已设置范围: 1 到 ${articles.length}`;
            }
        });

        uiElements.copyButton.addEventListener('click', function() {
            updateArticleCount();
            const selectedArticles = getSelectedArticles();

            if (selectedArticles.length === 0) {
                alert('请输入有效的范围');
                return;
            }

            const copyText = selectedArticles.map(article => {
                const processedText = article.text.replace(/<br\s*\/?>/gi, '\n');
                const plainText = processedText.replace(/<[^>]+>/g, '');
                return `${article.time}\n${plainText}`;
            }).join('\n\n');

            try {
                GM_setClipboard(copyText);

                const originalText = uiElements.copyButton.innerText;
                uiElements.copyButton.innerText = '已复制!';
                uiElements.statusDisplay.innerText = `已复制 ${selectedArticles.length} 篇文章`;
                setTimeout(() => {
                    uiElements.copyButton.innerText = originalText;
                }, 1500);
            } catch (error) {
                console.error('复制失败:', error);
                alert('复制失败，请检查脚本权限');
                uiElements.statusDisplay.innerText = '复制失败';
            }
        });

        uiElements.exportButton.addEventListener('click', async function() {
            updateArticleCount();
            const selectedArticles = getSelectedArticles();

            if (selectedArticles.length === 0) {
                alert('请输入有效的范围');
                return;
            }

            const originalText = uiElements.exportButton.innerText;
            uiElements.exportButton.innerText = '处理中...';
            uiElements.statusDisplay.innerText = `正在处理 ${selectedArticles.length} 篇文章...`;

            try {
                if (userSettings.useBase64Images) {
                    uiElements.statusDisplay.innerText = `正在处理和转换图片...这可能需要一些时间`;
                }

                const htmlContent = await generateHtmlContent(selectedArticles);
                const fileName = getExportFileName();

                if (safeDownloadFile(htmlContent, fileName)) {
                    uiElements.statusDisplay.innerText = `已导出 ${selectedArticles.length} 篇文章到 ${fileName}`;
                } else {
                    uiElements.statusDisplay.innerText = '导出失败，请检查浏览器设置';
                }
            } catch (error) {
                console.error('导出处理失败:', error);
                uiElements.statusDisplay.innerText = '导出失败: ' + error.message;
                alert('导出失败: ' + error.message);
            } finally {
                setTimeout(() => {
                    uiElements.exportButton.innerText = originalText;
                }, 1500);
            }
        });
    }

    // 获取iframe文档
    function getIframeDocument() {
        const iframe = document.getElementById('g_iframe');
        if (!iframe) return null;

        try {
            return iframe.contentDocument || iframe.contentWindow.document;
        } catch (e) {
            console.error('无法访问iframe内容:', e);
            return null;
        }
    }

    // 滚动到顶部以确保捕获所有内容
    function scrollToTop() {
        const iframeDoc = getIframeDocument();
        if (!iframeDoc) return false;

        try {
            const originalScrollPosition = iframeDoc.documentElement.scrollTop || iframeDoc.body.scrollTop;

            iframeDoc.documentElement.scrollTop = 0;
            iframeDoc.body.scrollTop = 0;

            hasScrolledToTop = true;

            if (uiElements) {
                uiElements.statusDisplay.innerText = '已滚动到顶部，正在扫描...';
            }

            setTimeout(() => {
                iframeDoc.documentElement.scrollTop = originalScrollPosition;
                iframeDoc.body.scrollTop = originalScrollPosition;
                if (uiElements) {
                    uiElements.statusDisplay.innerText = '扫描完成，已恢复滚动位置';
                }
            }, 1000);

            return true;
        } catch (e) {
            console.error('滚动到顶部失败:', e);
            return false;
        }
    }

    // 提取歌曲信息
    function extractSongInfo(elem) {
        try {
            const srcElement = elem.querySelector('.src');
            if (!srcElement) return null;

            const scntElement = srcElement.querySelector('.scnt');
            if (!scntElement) return null;

            const titleElement = scntElement.querySelector('.tit a');
            if (!titleElement) return null;

            const title = titleElement.textContent.trim();
            const songHref = titleElement.getAttribute('href');
            const songUrl = songHref ? `https://music.163.com${songHref}` : '';

            const artistElement = scntElement.querySelector('.from a');
            if (!artistElement) return null;

            const artist = artistElement.textContent.trim();
            const artistHref = artistElement.getAttribute('href');
            const artistUrl = artistHref ? `https://music.163.com${artistHref}` : '';

            return {
                title,
                url: songUrl,
                artist,
                artistUrl
            };
        } catch (e) {
            console.error('提取歌曲信息失败:', e);
            return null;
        }
    }

    // 提取图片URL
    function extractImageUrls(elem) {
        try {
            const imageUrls = [];
            const imageElements = elem.querySelectorAll('.pics .pic img');

            if (imageElements && imageElements.length > 0) {
                imageElements.forEach(img => {
                    const src = img.getAttribute('src');
                    if (src) {
                        const cleanSrc = src.split('?')[0].replace(/^http:/, 'https:');
                        if (cleanSrc) {
                            imageUrls.push(cleanSrc);
                        }
                    }
                });
            } else {
                const coverImg = elem.querySelector('.cover .lnk img');
                if (coverImg && coverImg.src) {
                    const cleanSrc = coverImg.src.split('?')[0].replace(/^http:/, 'https:');
                    if (cleanSrc) {
                        imageUrls.push(cleanSrc);
                    }
                }
            }

            return imageUrls;
        } catch (e) {
            console.error('提取图片URL失败:', e);
            return [];
        }
    }

    // 为元素生成唯一ID
    function generateElementId(elem, time, text) {
        return `${time}-${text.substring(0, 30).replace(/\s+/g, '')}`;
    }

    // 收集所有文章
    function scanForArticles() {
        const iframeDoc = getIframeDocument();
        if (!iframeDoc) {
            return { articles: articleArray, newFound: false };
        }

        const dcntcElements = iframeDoc.querySelectorAll('.dcntc');
        let newArticlesFound = false;

        dcntcElements.forEach(elem => {
            const timeElem = elem.querySelector('.time');
            const textElem = elem.querySelector('.text');

            if (timeElem && textElem) {
                let time = '';
                const timeLink = timeElem.querySelector('a');
                if (timeLink) {
                    time = timeLink.textContent.trim();
                } else {
                    time = timeElem.textContent.trim();
                }

                const text = textElem.innerHTML.trim();

                if (time && text) {
                    const articleId = generateElementId(elem, time, text);

                    if (!processedIds.has(articleId)) {
                        const song = extractSongInfo(elem);
                        const images = extractImageUrls(elem);
                        const domIndex = articleArray.length;

                        articleArray.push({
                            id: articleId,
                            time: time,
                            text: text,
                            song: song,
                            images: images,
                            elem: elem,
                            domIndex: domIndex
                        });

                        processedIds.add(articleId);
                        newArticlesFound = true;
                    }
                }
            }
        });

        return {
            articles: articleArray,
            newFound: newArticlesFound
        };
    }

    // 更新文章计数显示和范围输入
    function updateArticleCount() {
        if (!uiElements) return articleArray;

        const result = scanForArticles();
        const articles = result.articles;
        const total = articles.length;

        uiElements.countDisplay.innerText = `已检测到 ${total} 篇文章`;

        const currentEndValue = parseInt(uiElements.endRangeInput.value) || 1;
        if (result.newFound || currentEndValue > total) {
            if (currentEndValue > total) {
                uiElements.endRangeInput.value = total > 0 ? total : 1;
            }
        }

        uiElements.statusDisplay.innerText = result.newFound ?
            `发现新内容，共 ${total} 篇` :
            `内容稳定，共 ${total} 篇`;

        return articles;
    }

    // 重置所有状态
    function resetAllState() {
        articleArray.length = 0;
        processedIds.clear();
        hasScrolledToTop = false;
    }

    // 设置iframe滚动监听
    function setupIframeScrollListener() {
        const iframe = document.getElementById('g_iframe');
        if (!iframe || !iframe.contentWindow) return;

        iframe.contentWindow.addEventListener('scroll', function() {
            if (!isScrollThrottled) {
                isScrollThrottled = true;
                setTimeout(() => {
                    updateArticleCount();
                    isScrollThrottled = false;
                }, 300);
            }
        });
    }

    // 设置 MutationObserver 监听iframe DOM变化
    function setupMutationObserver() {
        if (observer) {
            observer.disconnect();
        }

        const iframeDoc = getIframeDocument();
        if (!iframeDoc) return;

        observer = new MutationObserver((mutations) => {
            let shouldUpdate = false;

            for (const mutation of mutations) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    shouldUpdate = true;
                    break;
                }
            }

            if (shouldUpdate) {
                updateArticleCount();
            }
        });

        observer.observe(iframeDoc.body, { childList: true, subtree: true });
    }

    // 初始化函数
    function initialize() {
        if (hasInitialized) {
            if (uiElements) {
                uiElements.statusDisplay.innerText = '重新扫描中...';
            }
            updateArticleCount();
            return;
        }

        const iframe = document.getElementById('g_iframe');
        if (!iframe) {
            if (uiElements) {
                uiElements.statusDisplay.innerText = '等待iframe加载...';
            }
            setTimeout(initialize, 1000);
            return;
        }

        if (!iframe.contentDocument || !iframe.contentWindow ||
            !iframe.contentDocument.body || iframe.contentDocument.readyState !== 'complete') {
            if (uiElements) {
                uiElements.statusDisplay.innerText = '等待iframe内容加载完成...';
            }
            setTimeout(initialize, 1000);
            return;
        }

        if (uiElements) {
            uiElements.statusDisplay.innerText = '正在初始化...';
        }

        hasInitialized = true;

        if (!hasScrolledToTop) {
            if (scrollToTop()) {
                setTimeout(() => {
                    setupIframeScrollListener();
                    setupMutationObserver();
                    updateArticleCount();
                }, 1500);
            } else {
                setupIframeScrollListener();
                setupMutationObserver();
                updateArticleCount();
            }
        } else {
            setupIframeScrollListener();
            setupMutationObserver();
            updateArticleCount();
        }
    }

    // 监听iframe变化
    function monitorIframeChanges() {
        const iframeObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'src') {
                    if (uiElements) {
                        uiElements.statusDisplay.innerText = 'iframe更新，重新初始化...';
                    }

                    if (observer) {
                        observer.disconnect();
                    }

                    resetAllState();
                    hasInitialized = false;
                    setTimeout(initialize, 1000);
                }
            });
        });

        const iframe = document.getElementById('g_iframe');
        if (iframe) {
            iframeObserver.observe(iframe, { attributes: true });
        }
    }

    // 监听页面变化，以便在导航到新页面时重新初始化
    window.addEventListener('hashchange', function() {
        if (uiElements) {
            uiElements.statusDisplay.innerText = 'URL变化，重新初始化...';
        }

        resetAllState();
        hasInitialized = false;
        setTimeout(initialize, 1000);
    });

    // 主函数：添加UI并开始初始化
    function main() {
        addUIToDocument();

        const checkIframeInterval = setInterval(() => {
            const iframe = document.getElementById('g_iframe');
            if (iframe && iframe.contentDocument && iframe.contentDocument.body) {
                clearInterval(checkIframeInterval);
                initialize();
                monitorIframeChanges();
            }
        }, 1000);

        setTimeout(() => {
            initialize();
            monitorIframeChanges();
        }, 2000);

        setInterval(() => {
            updateArticleCount();
        }, 5000);
    }

    if (window === window.top && !window.netEaseCommentExtractorInitialized) {
        window.netEaseCommentExtractorInitialized = true;
        main();
    }
})();