from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
app= FastAPI()

@app.get('/')
def Home():
    return "@@@@@@@@@@@"
@app.get('/get-marks')
def Abouts(styId : int , password: int,semester:int):


    base_url = 'http://mygate.aiu.edu.sy:8080/'
    login_url = '/faces/ui/login.xhtml'
    url = urljoin(base_url, login_url)
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    form = soup.find('form', {'id': 'lognForm'})

    action_url = urljoin(base_url, form['action'])

    view_state = soup.find('input', {'name': 'javax.faces.ViewState'})['value']
    
    form_data = {
        'lognForm': 'lognForm',
        'lognForm:j_idt19': f'{styId}',
        'lognForm:j_idt24': f'{password}',
        'lognForm:j_idt28': '1',
        'lognForm:j_idt33': 'دخول',
        'javax.faces.ViewState': view_state
    }

    response = session.post(action_url, data=form_data)

    if 'صحيحة' in response.text:
        return "NOTTRUE";
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
        #print(session_id)

        soup = BeautifulSoup(response.text, 'html.parser')

        a = soup.find('a', {'class': 'ripplelink beenhere'})

        Marks_Link = a.get('href')

        print("@@@@")
        url = urljoin(base_url, Marks_Link)



        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')  # Get Html content of login Page
        view_state = soup.find('input', {'name': 'javax.faces.ViewState'})['value']
        form_data = {
            "javax.faces.partial.ajax": 'true',
            "javax.faces.source": "contents:j_idt109",
            "javax.faces.partial.execute": "contents:j_idt109",
            "javax.faces.partial.render": "contents",
            "javax.faces.behavior.event": "change",
            "javax.faces.partial.event": "change",
            "contents": "contents",
            "contents:j_idt109_focus": "",
            "contents:j_idt109_input": f"{semester}",
            "javax.faces.ViewState": view_state
        }

        response = session.get(url)

        response = session.post(url, data=form_data)

        soup = BeautifulSoup(response.content, 'html.parser')

        result_table = soup.find('update')

        result_table = result_table.contents[0].strip()

        result_table = BeautifulSoup(result_table, 'html.parser')
        result_table = result_table.find('tbody', {'id': 'contents:j_idt113_data'})

        pattern = re.compile('^contents:j_idt113:.*:j_idt118$')
        subjectNames = result_table.find_all('label', {'id': pattern})
        pattern = re.compile('^contents:j_idt113:.*:(j_idt124|j_idt125)$')
        marksByNumb = result_table.find_all('label', {'id': pattern})

        # In[268]:

        pattern = re.compile('^contents:j_idt113:.*:j_idt127$')
        marksByLetter = result_table.find_all('label', {'id': pattern})
        #print(marksByLetter)

        # In[269]:
        print("@@@@@@@@@@@@@@@@@@@@@@")
        session_id = session.cookies.get('session_id')

        pattern = re.compile('^ui-widget-content ui-datatable-(even|odd)$')
        get_all_subs = result_table.find_all('tr', {'class': pattern})
        num_subs = len(get_all_subs)

        print("@@@@@@@@@@@@@@@@@@@@@@")

        # In[282]:
        data = {}
        for i in range(num_subs):
            form_data = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": f"contents:j_idt113:{i}:j_idt132",
                "javax.faces.partial.execute": "@all",
                "javax.faces.partial.render": "contents:courseDtlPnl",
                f"contents:j_idt113:{i}:j_idt132": f"contents:j_idt113:{i}:j_idt132",
                "contents": "contents",
                "contents:j_idt109_focus": "",
                "contents:j_idt109_input": f"{semester}",
                "javax.faces.ViewState": view_state
            }
            url = urljoin(base_url, "/faces/ui/pages/student/courseResult/index.xhtml")
            # print(url)
            print()
            response = session.post(url, data=form_data)
            soup = BeautifulSoup(response.content, 'html.parser')
            result_table = soup.find('update')
            result_table = result_table.contents[0].strip()
            result_table = BeautifulSoup(result_table, 'html.parser')
            pattern = re.compile(r'contents:j_idt136:(.*):j_idt142')
            details_table = result_table.find_all('label', {'id': pattern})
            total=0
            for mark in details_table:
                details_text = mark.text.strip()
                total += float(details_text)
            subj = {"subjectName": subjectNames[i].text, 'markByLetter': marksByLetter[i].text,
                    'markByNumber': marksByNumb[i].text, 'totalMarks': total}

            data[i]=subj
        return data;






