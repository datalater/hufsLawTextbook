import requests
from bs4 import BeautifulSoup

import re


# 법학도서관 지정도서 작업을 위해 "법전원 2017-1학기 수업별 교재목록"을 parsing하는 프로젝트


head={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
timetable_url = "http://webs.hufs.ac.kr:8989/src08/jsp/lecture/LECTURE2020L.jsp"
timetable_url_law = "http://webs.hufs.ac.kr:8989/src08/jsp/lecture/syllabus.jsp?mode=print&ledg_year=2017&ledg_sessn=1&org_sect=L&lssn_cd="

class parsing_class():

    # 클래스가 생성되자마자 시작되는 __init__ 함수 정의
    def __init__(self):

        # 브라우저를 켜는 함수를 바인딩하는 변수를 만든다.
        self.current_session = requests.session()

        # 2017년 1학기 법전원 옵션을 선택한다.
        params = {
            'tab_lang':'K',
            'type':'',
            'ag_ledg_year': '2017',
            'ag_ledg_sessn':'1',
            'ag_org_sect':'L',
            'gubun':'1',
            'ag_crs_strct_cd':'LAAA1_H1'
            }

        # 브라우저를 켜고 POST로 접속한다.
        self.current_session.post(timetable_url,data=params,headers=head)

        # POST로 접속하는 개체를 변수로 바인딩한다.
        self.timetable = self.current_session.post(timetable_url,data=params,headers=head)
        
        # 크롤링을 시작한다.
        html = BeautifulSoup(self.timetable.text, "html.parser")
        tr_courses = html.find_all("tr", attrs={"height":"55"})

        # 학수번호, 교과목명, 교수명을 담는다.
        for tr_course in tr_courses:
            self.course_number = tr_course.find_all("td")[3].string # 학수번호

            self.course_name = tr_course.find_all("td")[4].get_text() # 교과목명
            self.course_name = self.course_name.replace("\n","")
            cut_count = self.course_name.count("(")
            for i in range(cut_count):
                cut = self.course_name.rfind("(")
                self.course_name = self.course_name[:cut]

            self.course_professor = tr_course.find_all("td")[10].get_text() # 담당교수
            self.course_professor = self.course_professor.replace("\r","").replace("\t","").replace("\n","")
            cut = self.course_professor.rfind("(")
            if cut!=-1:
                self.course_professor = self.course_professor[:cut]

            # 학수번호가 포함된 강의계획서 url을 만든다.
            syllabus_url = timetable_url_law+self.course_number

            # 현재 브라우저에서 GET으로 강의계획서에 접속한다.
            self.current_session.get(syllabus_url,headers=head)

            # GET으로 접속하는 개체를 변수로 바인딩한다.
            self.syllabus = self.current_session.get(syllabus_url,headers=head)

            # 크롤링을 시작한다.
            html2 = BeautifulSoup(self.syllabus.text, "html.parser")
            textbook_tag = html2.find(text=re.compile("Textbooks")).parent.parent.parent.next_sibling.next_sibling

            # 디버깅-start-
            print("**********DEBUGGING: "+self.course_name+"("+self.course_number+")")
            reference_tag = html2.find(text=re.compile("Reference")).parent.parent
            print(reference_tag)
            # 디버깅-end-
            
            reference_tag = html2.find(text=re.compile("Reference")).parent.parent.parent.next_sibling.next_sibling
            
            textbook_tag = textbook_tag.text
            textbook_tag = repr(textbook_tag)
            textbook_tag = textbook_tag.replace("\\r","\n").replace("  ","")
            
            reference_tag = reference_tag.text
            reference_tag = repr(reference_tag)
            reference_tag = reference_tag.replace("\\r","\n").replace("  ","")

            print(self.course_name+"("+self.course_number+")"+"\n"+self.course_professor+"\n"+"<교재> "+textbook_tag+"\n"+"<참고문헌>"+reference_tag)
            print("===================================")
            print("===================================")

if __name__ == '__main__':
    p = parsing_class()
