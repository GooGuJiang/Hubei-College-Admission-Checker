import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import ddddocr
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
import os

# 配置 loguru 日志
logger.add("logfile.log", rotation="1 MB")

# 发送邮件函数
def send_email(subject, body, to_email):
    sender_email = "" # 邮箱地址
    sender_password = "" # SMTP密码
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.163.com', 465) as server: # 设置SMTP服务器
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        logger.info(f"邮件发送成功: {to_email}")
    except Exception as e:
        logger.error(f"邮件发送失败: {e}")

# 读取配置文件
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        return None

# 初始化OCR
ocr = ddddocr.DdddOcr(show_ad=False)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def check_status(session, ksh, sfzh):
    try:
        captcha_url = "https://cx.e21.cn/global/gd_check.php"
        response = session.get(captcha_url, headers=headers)

        if 'image' in response.headers['Content-Type']:
            try:
                image = Image.open(BytesIO(response.content))
            except Exception as e:
                logger.error(f"无法打开图片: {e}")
                return None
        else:
            logger.error("获取的内容不是图片。")
            logger.debug(response.content.decode('utf-8', errors='ignore'))
            return None

        result = ocr.classification(image)
        captcha_code = result

        form_data = {
            'ksh': ksh,
            'sfzh': sfzh,
            'randCode': captcha_code,
            'do': 'search'
        }

        post_url = "https://cx.e21.cn/statusSearch.php"
        response = session.post(post_url, headers=headers, data=form_data)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            tbody = soup.find('table', width="315")
            
            if tbody:
                status_info = {}
                rows = tbody.find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) == 2:
                        key = columns[0].text.strip()
                        value = columns[1].text.strip()
                        status_info[key] = value
                
                return status_info
            else:
                logger.error("tbody not found in the response.")
                return None
        else:
            logger.error(f"表单提交失败。状态码: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"查询状态失败: {e}")
        return None

def save_status_cache(status_cache):
    try:
        with open('status_cache.json', 'w') as file:
            json.dump(status_cache, file, ensure_ascii=False, indent=4)
        #logger.info("状态缓存保存成功。")
    except Exception as e:
        logger.error(f"保存状态缓存失败: {e}")

def load_status_cache():
    if os.path.exists('status_cache.json'):
        try:
            with open('status_cache.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"加载状态缓存失败: {e}")
            return {}
    return {}

def main():
    config = load_config()
    if not config:
        logger.error("配置文件加载失败，程序退出。")
        return
    
    previous_status = load_status_cache()

    while True:
        for account in config['accounts']:
            session = requests.Session()
            status_info = check_status(session, account['ksh'], account['sfzh'])

            if status_info:
                status_str = json.dumps(status_info, ensure_ascii=False, indent=4)
                previous_status_str = previous_status.get(account['email'], '')
                logger.info(f"{status_info['姓名']}:{status_info['考生状态']}")

                if status_str != previous_status_str:
                    logger.info(f"状态更新: {account['email']}")
                    email_body = "录取状态更新:\n\n"
                    for key, value in status_info.items():
                        email_body += f"{key}: {value}\n"
                    send_email("录取状态更新", email_body, account['email'])
                    previous_status[account['email']] = status_str
                    logger.info(f"状态更新发送邮件: {account['email']}")
            time.sleep(10)
            

        save_status_cache(previous_status)
        time.sleep(600)  # 每10分钟检测一次

if __name__ == "__main__":
    main()
