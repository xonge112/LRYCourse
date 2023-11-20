import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random
import json
import os
import re
from configparser import ConfigParser


class Cloud:
    def __init__(self, WebUrl, f_path):
        """
        对象初始化
        :param WebUrl: 网站地址
        :param f_path: Cookies文件保存路径
        """
        self.WebUrl = WebUrl
        # 加载edge浏览器驱动
        edge_path = r"MicrosoftWebDriver.exe"
        self.driver = webdriver.Edge(executable_path=edge_path)
        self.f_path = f_path

    # 第一次登录或cookie过期

    def login(self):
        # 获取网页
        self.driver.get(self.WebUrl)
        # 读取ini文件的账号和密码
        conf = ConfigParser()  # 需要实例化一个ConfigParser对象
        conf.read('login.ini')  # 需要添加上config.ini的路径，不需要open打开，直接给文件路径就读取，也可以指定encoding='utf-8'
        username = conf['user']['account']
        password = conf['user']['password']
        # 先点击页面空白处再进行元素定位
        self.driver.find_element_by_xpath('/html/body').click()
        # 调用selenium库中的find_element_by_xpath()方法定位搜索框，
        # 同时使用send_keys()方法在其中输入信息
        self.driver.find_element_by_xpath('//*[@id="account"]').send_keys(username)
        time.sleep(6 * random.random())  # 在两次请求之间间隔0~6秒的随机时间，避免反扒机制
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
        time.sleep(6 * random.random())
        self.driver.find_element_by_xpath('//*[@id="loginform"]/div[4]/button').submit()
        time.sleep(6 * random.random())
        self.driver.find_element_by_xpath('//*[@id="new_app_list"]/li[9]/a').click()
        # 跳转到新的页面
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(6 * random.random())
        self.driver.find_element_by_xpath('//*[@id="coursesearchbox"]').send_keys('刘成贤')
        time.sleep(6 * random.random())
        self.driver.find_element_by_xpath('//*[@id="search"]/button').submit()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(6 * random.random())
        self.driver.find_element_by_xpath('//*[@id="region-main"]/div/div[2]/div/div[2]/div[3]/p/a').click()
        time.sleep(6 * random.random())
        # driver.find_element_by_xpath('//*[@id="page-navbar"]/nav/div/form/div/div/button').click()
        # time.sleep(6 * random.random())
        self.save_cookies(self.driver.get_cookies())
        # 关闭driver
        # driver.close()

    # 自动登录
    def cloud_automatic_login(self):
        self.driver.get(self.WebUrl)
        cookies = self.load_cookies()
        print(self.load_cookies())
        if cookies:
            self.__cookies_login(cookies)
        else:
            self.login()
        login.cycle_answer()

    # 保存cookie到文件里面
    def save_cookies(self, data, encoding="utf-8"):
        # :param data: 所保存数据
        # :param encoding: 文件编码,默认utf-8
        with open("云Cookies.json", "w", encoding=encoding) as f_w:
            json.dump(data, f_w)

    # 把cookie从文件中加载出来
    def load_cookies(self, encoding="utf-8"):
        """
        :param encoding: 文件编码,默认utf-8
        """
        if os.path.isfile("云Cookies.json"):
            with open("云Cookies.json", "r", encoding=encoding) as f_r:
                user_status = json.load(f_r)
            return user_status

    # 添加登录所需要的cookies
    def __cookies_login(self, cookies: list):
        """
        :param cookies: 网页所需要添加的Cookie
        """
        self.driver.get("https://moodle.scnu.edu.cn/")
        flag = True
        self.driver.delete_all_cookies()
        for c in cookies:
            if cookies.index(c) == len(cookies) - 1:
                print(c)
                self.driver.add_cookie(c)
        self.driver.refresh()
        try:
            self.driver.find_element_by_class_name('usertext')
        except Exception:
            flag = False
        if flag:
            self.driver.get("https://moodle.scnu.edu.cn/course/view.php?id=15241")
            # self.driver.refresh()
        else:
            self.driver.delete_all_cookies()
            self.login()

    # 爬网页返回结果
    def get_web_result(self, year, section):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'MoodleSession={}'.format(self.driver.get_cookie('MoodleSession')['value'])}
        historyUrl = 'https://moodle.scnu.edu.cn/course/view.php?id=15241&section=' + str(section)
        res = requests.get(historyUrl, headers=header)
        print(res)
        html_doc = res.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        data = soup.find_all('div', attrs={'class': 'activityinstance'})
        # print(data)
        dic = {}
        for index in range(2, len(data), 2):
            examUrl = data[index].find('a')['href']
            examName = data[index].find('span', attrs={'class': 'instancename'}).text
            dic[examName] = examUrl
        name = ''
        for key in dic:
            if str(year) in key:
                name = key
            print(key + ' ---> ' + dic.get(key), end='\n')
        loginInfo = soup.find('div', attrs={'class': 'logininfo'})
        key = loginInfo.find_all('a')
        skey = key[1]['href'].split('=')[1]
        # print(skey)
        self.get_CloudQuestion(dic.get(name).split('=')[1], skey)

    # 返回lry题目
    def get_CloudQuestion(self, cmId, key):
        print(cmId)
        print(key)
        QUrl = 'https://moodle.scnu.edu.cn/mod/quiz/startattempt.php'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'MoodleSession={}'.format(self.driver.get_cookie('MoodleSession')['value'])
        }
        data = {
            'cmid': cmId,
            'sesskey': key,
            '_qf__mod_quiz_preflight_check_form': '1',
            'submitbutton': '开始答题'
        }
        res = requests.post(QUrl, headers=header, data=data, allow_redirects=False)
        link = ''
        try:
            link = res.headers['location'].split('=')
        except KeyError:
            print('该章节的答题次数已达上限')
            return -1
        no = link[1].split('&')
        print(no)
        locUrl = res.headers['location']
        res = requests.get(locUrl, headers=header)
        print(res)
        html_doc = res.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        questions_and_answers = soup.find_all('div', attrs={'class': 'formulation'})
        nextPage = soup.find('input', attrs={'class': 'mod_quiz-next-nav'})['value']
        if nextPage == '下一页':
            nextRes = requests.get(locUrl + "&page=1", headers=header)
            nextSoup = BeautifulSoup(nextRes.text, 'html.parser')
            nextQAA = nextSoup.find_all('div', attrs={'class': 'formulation'})
            for qaa in nextQAA:
                questions_and_answers.append(qaa)
        que_arr = []
        ans_arr = []
        code_arr = []
        for qa in questions_and_answers:
            question = qa.find('div', attrs={'class': 'qtext'})
            p = question.find('p', attrs={'dir': 'ltr'})
            if p is not None:
                question = p
            answer = qa.find_all('div', attrs={'class': 'ml-1'})
            que_arr.append("".join(question.text.split()))
            temp = []
            for index, a in enumerate(answer):
                if index == 0:
                    element = a.find_parent()['id']
                    code = element.split('_')
                    code_arr.append(code[0])
                temp.append("".join(a.text.split()))
            ans_arr.append(temp)
        print(que_arr)
        print(ans_arr)
        op = []
        for index in range(len(que_arr)):
            op.append(self.search_answer(que_arr[index], ans_arr[index]))
        print(op)
        self.auto_answers(op, code_arr, key, int(no[0]))

    def auto_answers(self, op, code_arr, key, shuZi):
        QUrl = 'https://moodle.scnu.edu.cn/mod/quiz/autosave.ajax.php'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'MoodleSession={}'.format(self.driver.get_cookie('MoodleSession')['value'])
        }
        data = {}
        que_no = []
        for i, code in enumerate(code_arr):
            temp = code + '_:flagged'
            data[temp] = 0
            temp1 = code + '_:sequencecheck'
            data[temp1] = 1
            temp2 = code + '_answer'
            nb = int(code.split(':')[1])
            que_no.append(nb)
            data[temp2] = op[i]
        data['attempt'] = shuZi
        data['thispage'] = 0
        data['nextpage'] = -1
        data['timeup'] = 0
        data['sesskey'] = key
        data['scrollpos'] = ''
        target = ''
        for index, i in enumerate(que_no):
            if index < len(que_no) - 1:
                target = target + str(i) + ','
            else:
                target = target + str(i)
        data['slots'] = target
        print(data)
        res = requests.post(QUrl, headers=header, data=data)
        print(res)
        print(res.json())

    def statement_normalization(self, sm):
        sm = sm.replace(' ', '')
        return re.sub(r'[^\w\s]', '', sm)

    def search_answer(self, question, answer: list):
        f = open('questionBank', 'r', encoding='utf-8')
        lines = f.readlines()
        keyIndex = 0
        ar = []
        question = self.statement_normalization(question)
        # print(question)
        for index, line in enumerate(lines):
            line = self.statement_normalization(line)
            if question in line or line in question:
                # print(line)
                keyIndex = index
                ar.append(line)
            if index > keyIndex & keyIndex != 0:
                ar.append(line)
            # print(line)
            if len(ar) == 10:
                break
        f.close()
        for targetAnswer in ar:
            for i, a in enumerate(answer):
                a = self.statement_normalization(a)
                if a in targetAnswer:
                    return i
        return -1

    def cycle_answer(self):
        while True:
            try:
                msg = int(input('请输入您要答的题目对应的年份（1921-2021）或退出（0）: '))
                if msg == 0:
                    print('祝您使用愉快！')
                    break
                elif msg < 1921 or msg > 2021:
                    print('请重新输入！')
                else:
                    section = -1
                    result = msg - 1921
                    if result < 10:
                        section = 2
                    elif msg == 2021:
                        section = 11
                    else:
                        section = int(result / 10) + 2
                    self.get_web_result(msg, section)

            except ValueError:
                print("请输入年份！")


url, cookie_fname = "https://sso.scnu.edu.cn/AccountService/user/login.html", "云Cookies.json"
login = Cloud(url, cookie_fname)
login.cloud_automatic_login()
