# 粉笔网试题爬虫

这是一个用于爬取粉笔网试题数据的Python爬虫程序。

## 功能特点

- 自动登录粉笔网
- 自动导航到指定试题
- 自动完成试题并获取结果
- 提取题型、题目、答案、正确率等数据
- 将数据保存为Excel文件

## 环境要求

- Python 3.7+
- Chrome浏览器
- 相关Python包（见requirements.txt）

## 安装步骤

1. 克隆或下载本项目
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 程序会自动打开Chrome浏览器并访问粉笔网
3. 等待手动完成登录
4. 登录完成后按回车继续
5. 程序会自动完成后续操作
6. 数据将保存在当前目录下的`fenbi_exam_data.xlsx`文件中

## 注意事项

- 请确保您有权限访问目标试题
- 程序运行过程中请勿关闭浏览器
- 如遇到网络问题，可能需要适当调整等待时间
- 建议使用稳定的网络环境运行程序 


## 爬虫

```python

/html/body/app-root/app-solution/div/app-tis/div/div[1]/div[1]/text()
/html/body/app-root/app-solution/div/app-tis/div/div[1]/div[1]/div

/html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[1]/text()
/html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p[2]
/html/body/app-root/app-solution/div/app-tis/div/div[2]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[2]/label/p

/html/body/app-root/app-solution/div/app-tis/div/div[3]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p/text()
/html/body/app-root/app-solution/div/app-tis/div/div[3]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[1]/label/p

/html/body/app-root/app-solution/div/app-tis/div/div[4]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p

题目

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p

选项

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/app-choice-radio/ul/li[1]/label/p

/html/body/app-root/app-solution/div/app-tis/div/div[24]/div/app-ti/div/div[2]/app-solution-choice/div/app-question-choice/div/article/p
答案

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-solution-overall/div/div[1]/span[1]

正确率

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-solution-overall/div/div[3]/span[1]


解析1

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[2]/div/p[1]

解析2

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[2]/div/p[2]

解析3

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[2]/div/p[3]

考点

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[3]/app-solution-keypoint/div/div/span

来源

/html/body/app-root/app-solution/div/app-tis/div/div[16]/div/app-ti/div/div[2]/app-solution-choice/div/app-result-common/div/section[4]/div
```
