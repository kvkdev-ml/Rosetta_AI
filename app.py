from flask.app import Flask
from flask import request,jsonify
from flask.templating import render_template
from ollama import Client,generate
import os as os
app=Flask(__name__)
client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
)
def check_code(code_snippet:str | None=None,model:str='gpt-oss:120b-cloud'):
    response = client.enerate(model=f'{model}',prompt=f"""
    Detect whether the give snippet is a programming language or not.
    Return ONLY true if yes otherwise no and if nothing is given then return None.
    Do not explain anything.
    Code:{code_snippet}
    """)
    return response.response
def generate_code(target_lang:str,initial_code:str,additionnal_prompt:str | None='No additional info'):
    if additionnal_prompt=='' or additionnal_prompt is None:
        additionnal_prompt='No Additional Info'
    resp=generate(model='gpt-oss:120b-cloud',prompt=f'''
You a Smart Code Transformer
Convert the following code:
{initial_code}
into the target language :{target_lang}
without breaking the structure and without changing any logic
Instructions:
    ->Dont explain anything.
    ->Return the code with proper Indentation.
    ->Only return the code while preserving the original Logic.
(Optional)Additional Information:{additionnal_prompt}
''')
    return resp.response
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/CodeMorpher')
def morpher_page():
    return render_template('input.html')
@app.route('/api/morph_code',methods=['POST'])
def code_morpher():
    if request.method=='POST':
        data=request.json
        code=data.get('code_snippet')
        if code:
            if check_code(code_snippet=code)=='no':
                return jsonify({'response':1,'valid_code':'invalid'})
            target_language=data.get('target_language')
            additional_ip=data.get('additional_ip')
            return jsonify({"response":1,'valid_code':'valid','output_code':generate_code(target_lang=target_language,initial_code=code,additionnal_prompt=additional_ip)})
    return jsonify({"response":0})
if __name__=='__main__':
    app.run()
