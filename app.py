from flask import Flask, request, jsonify
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

app = Flask(__name__)

@app.route('/')

def home():
    return "@@@@@@@@@@@"

@app.route('/get-marks', methods=['GET'])
def get_marks():

    styId = request.args.get('styId')
    password = request.args.get('password')
    semester = request.args.get('semester')

    base_url = 'http://mygate.aiu.edu.sy:8080/'
    login_url = '/faces/ui/login.xhtml'
    url = urljoin(base_url, login_url)
    session = requests.Session()
    
    response = session.get(url)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    form = soup.find('form', {'id': 'lognForm'})
    new_url=f"/faces/ui/login.xhtml;jsessionid={session.cookies.get('JSESSIONID')}"
    action_url = urljoin(base_url, form['action'])
    new_url=urljoin(base_url, new_url)
    view_state = soup.find('input', {'name': 'javax.faces.ViewState'})['value']
    
    form_data = {
        'lognForm': 'lognForm',
        'lognForm:j_idt27': f'{styId}',
        'lognForm:j_idt33': f'{password}',
        'lognForm:j_idt38': '1',
        'lognForm:j_idt43': '',
        'javax.faces.ViewState': view_state
    }
    session_id=session.cookies.get('JSESSIONID')
    
    response = session.post(new_url, data=form_data)
    
    

    
    
    if 'صحيحة' in response.text:
        return jsonify({'message': 'NOTTRUE'})
    else:

        if 'الفترة الحالية تقع ضمن فترة التسجيل' in response.text:

            form_data = {
                "javax.faces.partial.ajax": True,
                "javax.faces.source": "contents:j_idt112",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "contents:j_idt112",
                "contents:j_idt112": "contents:j_idt112",
                "javax.faces.ViewState": view_state
            }
            url1 = urljoin(base_url, "faces/ui/pages/student/index.xhtml")
            response = session.post(url1, data=form_data)
            response = session.get(url1)

            soup = BeautifulSoup(response.text, 'html.parser')
            name = soup.find('div', {'class': 'user-card-name'})  # Get name of Student
            name = name.text.strip()
        
        session_id = soup.find("input", {"name": "javax.faces.ViewState"})["value"]
        
        soup = BeautifulSoup(response.text, 'html.parser')

        a = soup.find('a', {'class': 'ripplelink beenhere'})

        marks_link = a.get('href')

        url = urljoin(base_url, marks_link)

        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')  # Get Html content of login Page
        view_state = soup.find('input', {'name': 'javax.faces.ViewState'})['value']
        ####################
        form_data_id='j_idt110'
        
        ############
        form_data = {
            "javax.faces.partial.ajax": 'true',
            "javax.faces.source": f"contents:{form_data_id}", 
            "javax.faces.partial.execute": f"contents:{form_data_id}",
            "javax.faces.partial.render": "contents",
            "javax.faces.behavior.event": "change",
            "javax.faces.partial.event": "change",
            "contents": "contents",
            f"contents:{form_data_id}_focus": "",
            f"contents:{form_data_id}_input": f"{semester}",
            "javax.faces.ViewState": view_state 
            }
        
        
        response = session.get(url)
        
        response = session.post(url, data=form_data)

        soup = BeautifulSoup(response.content, 'html.parser')

        result_table = soup.find('update')
        
        result_table = result_table.contents[0].strip()
        
        result_table = BeautifulSoup(result_table, 'html.parser')
        result_table = result_table.find('tbody', {'id': 'contents:j_idt114_data'})
        
        ########### change every semester
        sem_id='j_idt114'
        subname_id='j_idt119'
        marks_by_numb_id='j_idt126'
        marks_by_letter_id='j_idt128'
        details_id='j_idt133'
        result_detail_table_id1='j_idt137'
        result_detail_table_id2='j_idt143'
        ##############################
        pattern = re.compile(f'^contents:{sem_id}:.*:{subname_id}$')
        subject_names = result_table.find_all('label', {'id': pattern})
        pattern = re.compile(f'^contents:{sem_id}:.*:({marks_by_numb_id})$')
        marks_by_numb = result_table.find_all('label', {'id': pattern})
        
        pattern = re.compile(f'^contents:{sem_id}:.*:{marks_by_letter_id}$')
        marks_by_letter = result_table.find_all('label', {'id': pattern})



        session_id = session.cookies.get('session_id')

        pattern = re.compile('^ui-widget-content ui-datatable-(even|odd)$')
        get_all_subs = result_table.find_all('tr', {'class': pattern})
        num_subs = len(get_all_subs)

        data = {}
        
        
        for i in range(num_subs):
            form_data = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": f"contents:{sem_id}:{i}:{details_id}",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "contents:courseDtlPnl",
                f"contents:{sem_id}:{i}:{details_id}": f"contents:j_idt113:{i}:{details_id}",
                "contents": "contents",
                f"contents:{form_data_id}_focus": "",
                f"contents:{form_data_id}_input": f"{semester}",
                "javax.faces.ViewState": view_state
            }
            url = urljoin(base_url, "/faces/ui/pages/student/courseResult/index.xhtml")

            response = session.post(url, data=form_data)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            result_table = soup.find('update')
            result_table = result_table.contents[0].strip()
            result_table = BeautifulSoup(result_table, 'html.parser')
            print(result_table)
            pattern = re.compile(f'contents:{result_detail_table_id1}:(.*):{result_detail_table_id2}')
            details_table = result_table.find_all('label', {'id': pattern})
            total=0
            for mark in details_table:
                details_text = mark.text.strip()
                total += float(details_text)
            
            json_string = json.dumps({"": subject_names[i].text}, ensure_ascii=False)
            
            subj = {"subjectName": json.loads(json_string), 'markByLetter': marks_by_letter[i].text,
                    'markByNumber': marks_by_numb[i].text, 'totalMarks': total}
            #print(subject_names[i].text)
            
            data[i]=subj
        print(data)
        return jsonify(data)

if __name__=="__main__":
    app.run(debug=True)