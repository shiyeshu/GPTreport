import base64
from flask import Flask, render_template, request
import requests
#import openai
import json
import time

app = Flask(__name__, template_folder='templates', static_folder='static')

# 设置 OpenAI API 密钥
api_key = "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"

# 设定 GPT-3 模型名称
#model_engine = "gpt-3.5-turbo"
model_engine = "gpt-3.5-turbo"

# 设置代理
global proxy
proxy = "http://127.0.0.1:7890"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        vuln_name = request.form.get('vuln_name', default="SQL注入")
        vuln_point = request.form.get('vuln_point', default="www.google.com")
        beizhu = request.form.get('beizhu', default="")
        language = request.form.get('language')
        start = time.time()
        report = generate_report(vuln_name, vuln_point, beizhu, language)
        end = time.time()
        times = end - start

        return render_template('index.html', report=report, times=times)
    else:
        return render_template('index.html')


def generate_report(vuln_name, vuln_point, beihzu="", language=""):
    # 构造 GPT-3 输入
    prompt = f"漏洞名称：{vuln_name}\n漏洞点：{vuln_point}\n生成一个不少于300字向SRC提交的{language}漏洞报告，要求返回makedown源码格式。{beihzu}"

    #api_base = {"socks5":proxy}
    api_base = {"http": proxy, "https": proxy}

    # 调用 OpenAI API 生成漏洞报告
    headers = {
        # Already added when you pass json= but not when you pass data=
        'Content-Type': 'application/json',
        'Authorization': "Bearer "+api_key,
    }

    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    }
    # 设置代理
    # 计算时间

    response = requests.post('https://api.openai.com/v1/chat/completions',
                             headers=headers, json=json_data, proxies=api_base)

    # 处理 OpenAI API 的响应
    if response.status_code == 200:
        text = response.text
        text = json.loads(text)
        text = text['choices'][0]['message']['content']
        report = f"{text}"

    else:
        report = "生成漏洞报告失败，请检查输入并重试。状态码："+str(response.status_code)

    return report

@app.route('/outfile',methods=['POST'])
def outfile():
    #获取post过来的base64编码的date
    date=request.form.get('reportText')
    
    #将date进行base64解码
    date=base64.b64decode(date,).decode('utf-8')
    #将date写入md文件，文件名为当前时间
    fname=time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    with open(fname+'.md','w') as f:
        f.write(date)
    return "ok"
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
