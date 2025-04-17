from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
import time

# jetbrains://pycharm/navigate/reference?project=BQ_Spider&path=spider.html
# file:///H:/project/cursor/BQ_Spider/spider.html
class FenbiSpider:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def get_question_data(self, url):
        self.driver.get(url)
        time.sleep(3)  # 等待页面基础加载

        # 定位题目容器
        question_container = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ti-container.showBg")))

        return {
            "category": self._get_category(question_container),
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
                        f'<img src="{img_tags[0].get_attribute("src")+"https:"}">')
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
                By.CSS_SELECTOR, "span.correct-rate").text.replace(" ", "") + "%"
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

    def run(self, url):
        try:
            data = self.get_question_data(url)
            print(json.dumps(data, ensure_ascii=False, indent=2))
        finally:
            self.driver.quit()


if __name__ == "__main__":
    spider = FenbiSpider()
    target_url = "file:///H:/project/cursor/BQ_Spider/t.html"
    # target_url = "https://spa.fenbi.com/ti/exam/solution/1_1_31k49p8?routecs=xingce"
    spider.run(target_url)
