from datetime import datetime
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import json
from typing import Union, List, Dict

class JSONSaver:
    def __init__(self, filename: str = None, indent: int = 4, ensure_ascii: bool = False):
        """
        JSON数据存储工具

        参数:
            filename: 目标文件名（可选）
            indent: 缩进空格数（默认4）
            ensure_ascii: 是否转义非ASCII字符（默认False保留中文）
        """
        self.filename = filename or f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        self.data = []

    def add_data(self, new_data: Union[Dict, List[Dict]]) -> None:
        """添加单条或多条数据"""
        if isinstance(new_data, dict):
            self.data.append(new_data)
        elif isinstance(new_data, list):
            self.data.extend(new_data)
        else:
            raise TypeError("只接受字典或字典列表")

    def save(self, filename: str = None, mode: str = 'w') -> None:
        """
        保存数据到文件

        参数:
            filename: 覆盖默认文件名（可选）
            mode: 写入模式
                'w' - 覆盖写入（默认）
                'a' - 追加到现有文件
        """
        target_file = filename or self.filename

        try:
            # 追加模式处理
            if mode == 'a' and os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                combined_data = existing_data + self.data
            else:
                combined_data = self.data

            # 写入文件
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(
                    combined_data,
                    f,
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii,
                    separators=(',', ': ') if self.indent else (',', ':')
                )

            print(f"成功保存 {len(self.data)} 条数据到 {target_file}")
            self.data = []  # 清空缓存

        except Exception as e:
            print(f"保存失败: {str(e)}")
            raise

    def pretty_print(self) -> None:
        """打印格式化后的JSON数据"""
        print(json.dumps(self.data, indent=2, ensure_ascii=False))

class FenbiSpider:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 无头模式，取消注释即可启用
        chrome_options.add_argument('--start-maximized')

        chrome_options.add_argument("--disable-blink-features=AutomationControlled") # 禁用 Blink引擎的自动化控制特征； Chrome 的 Blink 引擎会暴露自动化特征（如 navigator.webdriver=true），此参数部分隐藏这些
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) #移除浏览器顶部的 "Chrome 正受到自动测试软件控制" 提示 禁用 Chrome 的 enable-automation 开关，避免触发浏览器内置的自动化检测机制
        chrome_options.add_experimental_option("useAutomationExtension", False) # 某些网站会检测 Chrome 扩展列表，自动化扩展（如 chrome-driver-extension）可能暴露自动化

        # driver = webdriver.Chrome(options=chrome_options)
        # 添加反检测参数（仅适用于简单场景） or 使用更隐蔽的自动化工具（如 Puppeteer 或 Playwright）。
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", { # 在页面加载前注入 JavaScript，彻底隐藏 navigator.webdriver 属性
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                    """
        })
        self.wait = WebDriverWait(self.driver, 10)
        self.action = ActionChains(self.driver)
        self.dataSaver = JSONSaver(ensure_ascii=False)

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
        tiku = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div[1]/fb-header/div/div[1]/div[2]/a[3]")))
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
                exit = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/app-root/app-solution/app-nav-header/header/div/div[1]/a")))
                exit.click()

            # 点击加载新的试卷分页
            page = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/app-root/div/app-main/div[2]/app-real-test/div/footer/fb-pager/div/div[5]/div")))
            page.click()



    """"
    大模型生成 查询单一题目 非资料分析
    """
    def get_question_data(self, following_div=None, category=None):
        time.sleep(1)
        question_container = following_div  #following_div.find_element((By.CSS_SELECTOR, "div.ti-container.showBg"))
        if question_container:
            self.action.move_to_element(question_container).perform()
        else:
            print("find category {} error".format(category))
            return None

        return {
            "category": category,
            "type": self._get_category(question_container),
            "title": self._get_title(question_container),
            "options": self._get_options(question_container),
            "answer": self._get_correct_answer(question_container),
            "right_rate": self._get_correct_rate(question_container),
            "analysis": self._get_analysis(question_container),
            "knowledge_point": self._get_knowledge_points(question_container),
            "origin": self._get_origin(question_container)
        }

    def _get_category(self, container):
        try:
            return container.find_element(
                By.CSS_SELECTOR, "div.title-type-name.ng-star-inserted").text.strip()
        except NoSuchElementException:
            return "未知题型"

    def _get_title(self, container):
        try:
            content = container.find_element(
                By.CSS_SELECTOR, "app-question-choice article.content")
            return content.get_attribute("innerHTML").replace("\n", "</br>")
        except NoSuchElementException:
            return ""

    def _get_options(self, container):
        options = []
        try:
            options_container = container.find_element(
                By.CSS_SELECTOR, "app-choice-radio ul.choice-radios")
            options_elements = options_container.find_elements(
                By.CSS_SELECTOR, "li.choice-radio")

            for opt in options_elements:
                # 处理包含图片的选项
                img_tags = opt.find_elements(By.TAG_NAME, "img")
                if img_tags:
                    options.append(
                        f'<img src="{img_tags[0].get_attribute("src") + "https:"}">')
                else:
                    options.append(
                        opt.find_element(By.CSS_SELECTOR, "p.input-text").text)
        except NoSuchElementException:
            pass
        return options

    def _get_correct_answer(self, container):
        try:
            return container.find_element(
                By.CSS_SELECTOR, "span.correct-answer.ng-star-inserted").text
        except NoSuchElementException:
            return ""

    def _get_correct_rate(self, container):
        try:
            return container.find_element(
                By.CSS_SELECTOR, "span.correct-rate").text.replace("\n", "").replace("%%", "%").strip()
        except NoSuchElementException:
            return ""

    def _get_analysis(self, container):
        try:
            # 定位包含解析的section
            section = container.find_element(
                By.XPATH, ".//section[.//div[@class='solution-title' and text()='解析']]")
            return section.find_element(
                By.CSS_SELECTOR, "div.content").get_attribute("innerHTML")
        except NoSuchElementException:
            return ""

    def _get_knowledge_points(self, container):
        points = []
        try:
            keypoint_section = container.find_element(
                By.CSS_SELECTOR, "app-solution-keypoint")
            elements = keypoint_section.find_elements(
                By.CSS_SELECTOR, "span.solution-keypoint-item-name")
            points = [e.text for e in elements]
        except NoSuchElementException:
            pass
        return points

    def _get_origin(self, container):
        try:
            # 定位来源section
            section = container.find_element(
                By.XPATH, ".//section[.//div[@class='solution-title' and text()='来源']]")
            return section.find_element(
                By.CSS_SELECTOR, "div.content").text.strip()
        except NoSuchElementException:
            return ""

        """"
        查询单一题目 非资料分析
        """

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
        confirm_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-modal-common/div/div/div[2]/button[2]")))
        confirm_btn.click()

    def find_all_category(self):
        try:
            # 标识跳转并开始执行的地方
            # /html/body/app-root/app-solution/div/app-tis/div/div[1]/div[1]/text()
            categories = []
            categorys = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'chapter-container')]")
            print("categorys len ", len(categorys))
            if categorys and len(categorys):
                for category_el in categorys:
                    self.action.move_to_element(category_el).perform()
                    nums_el = category_el.find_element(By.XPATH, "//*[contains(@class, 'chapter-num')]")
                    if nums_el:
                        category = category_el.text.removeprefix("\"").removesuffix("\"").split("\n")[0].strip(" ")
                        question_nums_str = nums_el.text.removeprefix("（").removesuffix("）").removesuffix("题").strip(" ")
                        if question_nums_str:
                            question_nums = int(question_nums_str)
                        else:
                            continue
                    else:
                        continue
                    categories.append({"category": category, "question_nums": question_nums})
            else:
                print("error categorys len ", categorys, len(categorys))
            print("categories \n", categories)

        except Exception as  e:
            print(e)
            return None
        return categories,categorys

    # @with_goto
    def extract_data(self):
        # label .begin
        """提取得分数据"""
        # 等待数据加载
        time.sleep(3)
        categoriy_dict, categorys = self.find_all_category()

        for i, category in enumerate(categorys):
            self.action.move_to_element(category).perform()
            # 先找到包含chapter-name的div元素
            # chapter_div = driver.find_element(By.CSS_SELECTOR, "div[class*='chapter-name']")
            # 获取其后20个兄弟div元素
            xpath = "./following-sibling::div[contains(@class, 'ti')][position() <= {}]".format(categoriy_dict[i].get("question_nums"))
            print("xpath", xpath)
            time.sleep(1)
            try:
                # 获取所有题目信息元素
                following_divs = category.find_elements(By.XPATH, xpath)

                if following_divs and len(following_divs):
                    for following_div in following_divs:
                        print(following_div)
                        try:
                            # 暂时排除资料分析
                            if categoriy_dict[i].get("category") != "资料分析":
                                data = self.get_question_data(following_div, categoriy_dict[i].get("category"))
                                self.dataSaver.add_data(data)
                                self.dataSaver.save(mode='a')
                            # self.dataSaver.append_to_excel(data) if data else None
                            print(data)
                        except Exception as e:
                            print("get question data error",e)
                            continue
                else:
                    print("find following_divs error")
                    continue
            except Exception as e:
                print(e)
                continue

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