# NewsMind - 用 AI 來生成英文新聞的閱讀測驗

## 簡介

NewsMind 利用 AI 將最新英文新聞轉換成互動式的閱讀測驗，幫助你一邊掌握國際新聞，一邊提升英文閱讀力。

### 功能特色

  ✅ 新聞來源：每天最新的CNN文章

  ✅ 主題分類選擇：國際、科技、商業、娛樂、運動

  ✅ AI 自動生成閱讀理解試題

  ✅ 每題提供 正確答案與詳解

  ✅ 練習直接在網頁上進行，無需安裝

<img width="1796" height="968" alt="image" src="https://github.com/user-attachments/assets/301e7e8f-3f45-4b01-9183-0f10d8e0e7e2" />
<img width="1796" height="968" alt="image" src="https://github.com/user-attachments/assets/e5468f87-f678-4b50-9a44-8cdf93fb47f2" />
<img width="1796" height="968" alt="image" src="https://github.com/user-attachments/assets/f3195e2c-88a6-430d-9f1b-674f40b27763" />
<img width="1796" height="968" alt="image" src="https://github.com/user-attachments/assets/a40a88a4-2622-4786-924e-95c5230ec350" />

## 如何在 Windows 上啟動 news-quiz-ai
```bash
$ git clone https://github.com/csun3366/news-quiz-ai.git
$ cd news-quiz-ai
$ python3 -m venv venv
$ .\venv\Scripts\activate
$ pip install -r requirements.txt
$ cd backend/
$ python manage.py runserver
```


## 雲端部屬流程（On Ubuntu 25.04 Minimal, Google Cloud VM）

### 建立基本環境
```bash
# 更新系統與安裝工具
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install git python3 pip vim python3.13-venv
```

### 設定nginx
```bash
$ sudo apt-get install nginx
$ sudo apt-get install gunicorn
$ sudo vim /etc/nginx/sites-available/your_project

將以下內容貼上
server {
    listen 80;
    server_name newsmind-ai.ix.tc;  # 或寫 IP，例如 123.123.123.123

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 180s; #這個跟據處理時間更改
    }
}

$ sudo ln -s /etc/nginx/sites-available/your_project /etc/nginx/sites-enabled/
$ sudo nginx -t
$ sudo systemctl restart nginx
$ sudo systemctl daemon-reload
```

### 複製專案並建立虛擬環境
```bash
$ git clone https://github.com/csun3366/news-quiz-ai.git
$ cd news-quiz-ai
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install gunicorn
```
### 啟動 news-quiz-ai
```bash
$ cd backend/
$ python manage.py collectstatic
$ vim backend/settings.py
ALLOWED_HOSTS加入以下內容
ALLOWED_HOSTS = ['輸入機器對外IP', 'newsmind-ai.ix.tc']

$ nohup ../venv/bin/gunicorn backend.wsgi --bind 127.0.0.1:8000 --access-logfile - --error-logfile gunicorn-error.log --timeout 180 > gunicorn.out 2>&1 &
```

到這一步，就可以用 http://newsmind-ai.ix.tc 瀏覽網站

### 設定https
```bash
$ sudo apt install certbot python3-certbot-nginx
$ sudo certbot --nginx
```

可以用 https://newsmind-ai.ix.tc 瀏覽網站
