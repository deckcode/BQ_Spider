import os
from sys import exception
from time import sleep

import goto
from numpy.f2py.auxfuncs import throw_error
# from goto import with_goto

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
import logging

from webdriver_manager.core import driver

import threading


class LogMonitor(threading.Thread):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self._running = True

    def run(self):
        while self._running:
            for log_type in ["browser", "driver", "performance"]:
                for entry in self.driver.get_log(log_type):
                    self.process_log(entry)

    def process_log(self, entry):
        if entry["level"] == "SEVERE":
            logging.error(f"CRITICAL ERROR: {entry['message']}")

    def stop(self):
        self._running = False


class FenbiSpider:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 无头模式，取消注释即可启用
        chrome_options.add_argument('--start-maximized')

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # driver = webdriver.Chrome(options=chrome_options)
        # 添加反检测参数（仅适用于简单场景） or 使用更隐蔽的自动化工具（如 Puppeteer 或 Playwright）。
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                    """
        })
        self.wait = WebDriverWait(self.driver, 10)
        self.action = ActionChains(self.driver)

        # 使用示例
        # self.monitor = LogMonitor(self.driver)
        # self.monitor.start()

        # 执行测试操作...
        
    def login(self):
        """登录粉笔网"""
        self.driver.get('https://www.fenbi.com/')
        # 等待用户手动登录
        input("请完成登录后按回车继续...")
        print("login success")
        
    def navigate_to_exam(self):
        """导航到目标试题"""
        sleep(1)
        # 点击题库
        # /html/body/app-root/div/div[1]/fb-header/div/div[1]/div[2]/a[3]
        # /html/body/app-root/div/div[1]/fb-header/div/div[1]/div[2]/a[3]/div[1]
        tiku = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div[1]/fb-header/div/div[1]/div[2]/a[3]")))
        # self.wait.until(EC.element_to_be_)
        tiku.click()

        curr_win_handle = self.driver.current_window_handle
        self.wait.until(EC.number_of_windows_to_be(2))
        windows = self.driver.window_handles
        # 切换到新的tab
        self.driver.switch_to.window(windows[1])
        # 点击历年试卷
        # /html/body/app-root/div/app-main/div[2]/app-catalog/div/main/div[1]/div[1]/fb-tiku-catalog/div/ul/li[2]/div
        # liannian = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-main/div[2]/app-catalog/div/main/div[1]/div[1]/fb-tiku-catalog/div/ul/li[2]")))
        liannian = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                               "/html/body/app-root/div/app-main/div[2]/app-catalog/div/main/div[1]/div[1]/fb-tiku-catalog/div/ul/li[2]")))
        liannian.click()

        # #qusetion-list > main > div.shenlun-list-detail > app-paper-item:nth-child(1)

        for i in range(3):
            sleep(3)
            # 题库
            exams = self.driver.find_elements(By.TAG_NAME, "app-paper-item");
            print("exams len ", len(exams))
            sleep(1)
            for exam in exams:
                exam.click()
                self.complete_exam()
                self.extract_data()

                # 推出当前试卷, 下次点击新的试卷
                exit = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/app-nav-header/header/div/div[1]/a")))
                exit.click()

            # 点击加载新的试卷分页
            page = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-main/div[2]/app-real-test/div/footer/fb-pager/div/div[5]/div")))
            page.click()
        
        # 点击推荐下的2025年国家公务员录用考试《行测》题
        # exam = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'2025年国家公务员录用考试《行测》题（副省级网友回忆版）')]")))
        # exam.click()
        
    def complete_exam(self):
        """完成试题并获取结果"""
        # 等待试题加载
        time.sleep(2)
        
        # 点击完成交卷按钮
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/app-root/app-exercise/app-nav-header/header/div/div[3]/div"))).click()
        # submit_btn.click()
        sleep(2)
        # 确认交卷
        confirm_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-modal-common/div/div/div[2]/button[2]")))
        confirm_btn.click()

    # @with_goto
    def extract_data(self):
        # label .begin
        """提取得分数据"""
        # 等待数据加载
        time.sleep(3)

        # 获取所有题目数据
        # questions = self.driver.find_elements(By.CSS_SELECTOR, ".question-item")
        # 获取所有题目类型
        try:
            # 标识跳转并开始执行的地方
            # /html/body/app-root/app-solution/div/app-tis/div/div[1]/div[1]/text()
            categorys  = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'chapter-container')]")
            print("categorys len ", len(categorys))

            allnums = 0
            for j, category in enumerate(categorys):
                try:
                    category_name = category.find_element(By.CSS_SELECTOR, "[class*='chapter-name']").text.removeprefix("\"").removesuffix("\"").split("\n")[0].strip(" ")
                    question_nums = category.find_element(By.CSS_SELECTOR, "[class*='chapter-num']").text.removeprefix("（").removesuffix("）").removesuffix("题").strip(" ")

                    print("category_name ", category_name, "question_nums ", question_nums)
                    # while allnums < int(question_nums):
                        # question_num = question_nums[allnums]
                    for i in range(int(question_nums)):
                        try:
                            data = []
                            if allnums >= 120:
                                return
                            # /html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[1]/text()
                            # /html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[1]
                            # /html/body/app-root/app-solution/div/app-tis/div/div[3]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p
                            # /html/body/app-root/app-solution/div/app-tis/div/div[3]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p
                            # /html/body/app-root/app-solution/div/app-tis/div/div[4]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p
                            # /html/body/app-root/app-solution/div/app-tis/div/div[5]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p
                            # /html/body/app-root/app-solution/div/app-tis/div/div[37]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p

                            # /html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[1]
                            print("/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums+ i + j + 2) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[2]/div/p[2]")

                            # /html/body/app-root/app-solution/div/app-tis/div/div[28]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[2]/img
                            # # 构建操作链 然后perform 完成操作链每一步
                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[1]")))
                            self.action.move_to_element(el).perform()
                            title = el.text.strip(" ")
                            print("\ntitle \n", title)

                            # title = "12"
                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[1]/label/p")))
                            self.action.move_to_element(el).perform()
                            item1 = el.text.strip(" ")
                            print("\nitem1 \n", item1)

                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[2]/label/p")))
                            self.action.move_to_element(el).perform()
                            item2 = el.text.strip(" ")
                            print("\nitem2 \n", item2)

                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[3]/label/p")))
                            self.action.move_to_element(el).perform()
                            item3 = el.text.strip(" ")
                            print("\nitem3 \n", item3)

                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[4]/label/p")))
                            self.action.move_to_element(el).perform()
                            item4 = el.text.strip(" ")
                            print("\nitem4 \n", item4)
                            # 答案
                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-solution-overall/div/div[1]/span[1]")))
                            self.action.move_to_element(el).perform()
                            res = el.text.strip(" ")
                            print("\nres \n", res)
                            # /html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-solution-overall/div/div[3]/span[1]/text()
                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                           "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-solution-overall/div/div[3]/span[1]")))
                            self.action.move_to_element(el).perform()
                            rightRate = el.text.strip(" ").split("\n")[0]
                            print("\nrightRate \n", rightRate)

                            # /html/body/app-root/app-solution/div/app-tis/div/div[6]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[1]/app-solution-title/div/div
                            # /html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[2]/div
                            el = self.driver.find_element(By.XPATH, "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) +"]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[1]/app-solution-title/div/div")
                            if el is not None and el.text.find("解析时评"):
                                self.action.move_to_element(el).perform()
                                el = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                                 "/html/body/app-root/app-solution/div/app-tis/div/div[" + str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[2]/div")))

                            analyzes = []
                            ps = el.find_elements(By.TAG_NAME, "p")
                            if ps is not None and len(ps) > 0:
                                for p in ps:
                                    self.action.move_to_element(p).perform()
                                    print("\n span \n", p.text.strip(" "))
                                    analyzes.append(p.text.strip(" "))

                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                     "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[3]/app-solution-keypoint/div/div/span")))
                            self.action.move_to_element(el).perform()
                            knowledgePoint = el.text.strip(" ")
                            print("\nknowledgePoint \n", knowledgePoint)

                            el = self.wait.until(EC.element_to_be_clickable((By.XPATH,
                                                     "/html/body/app-root/app-solution/div/app-tis/div/div["+ str(allnums + 2 + i + j) + "]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[4]/div")))
                            self.action.move_to_element(el).perform()
                            origin = el.text.strip(" ")
                            print("\norigin \n", origin)

                            # print(title + "\n" + item1 + "\n" + item2 + "\n" + item3 + "\n" + item4 + "\n" + res + "\n" + rightRate + "\n"+ analyze1 + "\n" + analyze2 + "\n" + analyze3 + "\n" + knowledgePoint + "\n" + origin)
                            data.append({
                                'category_name': category_name,
                                'title':title,
                                'item1':item1,
                                'item2':item2,
                                'itme3':item3,
                                'item4':item4,
                                'result':res,
                                'rightRate':rightRate,
                                'analyzes':analyzes,
                                'knowledgePoint':knowledgePoint,
                                'origin':origin
                            })
                            self.save_to_excel(data)

                        except Exception as e:
                            print(f"1提取数据时出错: {str(e)}")
                            print(f"spider error\n", i , question_nums, j, category_name)
                            continue
                    allnums += int(question_nums)

                except Exception as e:
                    print(f"2提取数据时出错: {str(e)}")
                    print(f"spider error will lost a category \n", j , category_name)
                    continue

        except Exception as e:
            print(f"3提取数据时出错: {str(e)}")

        # return data

        # data = []
        # for question in questions:
        #     try:
        #         question_type = question.find_element(By.CSS_SELECTOR, ".question-type").text
        #         question_text = question.find_element(By.CSS_SELECTOR, ".question-content").text
        #         answer = question.find_element(By.CSS_SELECTOR, ".correct-answer").text
        #         correct_rate = question.find_element(By.CSS_SELECTOR, ".correct-rate").text
        #
        #         data.append({
        #             '题型': question_type,
        #             '题目': question_text,
        #             '答案': answer,
        #             '正确率': correct_rate
        #         })

    
    def save_to_excel(self, data):
        """保存数据到Excel"""
        if data is None or len(data) == 0:
            return
        # if self.df is None:
        df = pd.DataFrame(data)
        if os.path.exists('fenbi_exam_data.xlsx'):
            # if self.existing_df is None:
            existing_df = pd.read_excel('fenbi_exam_data.xlsx')
            df = pd.concat([existing_df, df])
        df.to_excel('fenbi_exam_data.xlsx', index=False)
        print("数据已保存到 fenbi_exam_data.xlsx")
        
    def run(self):
        """运行爬虫"""
        try:
            self.login()
            self.navigate_to_exam()
            # self.complete_exam()
        except Exception as e:
            print(f"运行出错: {str(e)}")
        finally:
            # 停止监控
            # self.monitor.stop()
            print("not quit")
            self.driver.quit()

if __name__ == "__main__":
    spider = FenbiSpider()
    spider.run() 