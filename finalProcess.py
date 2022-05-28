import openpyxl
import pandas as pd
import numpy as np
import re
import xlrd
from sklearn.utils import shuffle

excel_path = 'data/standard.xlsx'
wb = openpyxl.load_workbook(excel_path)
# 获取workbook中所有的表格
sheets = wb.sheetnames
print(sheets)
allTrainData = pd.DataFrame()
allTestData = pd.DataFrame()

def dataPreprocess(data):
    prodata = data
    prodata.drop_duplicates()
    print("dropna前的行数：" + str(prodata.shape[0]))
    prodata.replace(to_replace=r'来源：[\u4e00-\u9fa5]+', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'作者：[\u4e00-\u9fa5]+', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'图——[\u4e00-\u9fa5]+', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'\s+', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'\([^()]*\)|\（[^（）]*\）|\（[^（)]*\)|\([^(）]*\）', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'【[^【】]*】', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'\[[^[]]*\]', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'\{.*\}', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'<.*>', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'●|■|◆|�', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'↑①|↑②|↑③|↑④|↑⑤|↑⑥|↑⑦|↑⑧|↑⑨|↑⑩', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'原标题：', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'我要反馈', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'相关新闻', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'相关微博', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'加载中', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'点击加载更多', value='', regex=True, inplace=True)
    prodata.replace(to_replace=r'分享让更多人看到', value='', regex=True, inplace=True)
    print("dropna后的行数：" + str(prodata.shape[0]))
    print("清理空格换行——————————————-")
    return prodata


sheet = wb[sheets[0]]
print('\n\n' +  'sheet: ' + sheet.title + '->>>')
df = pd.read_excel(excel_path, sheet_name=0, index=False, encoding='utf8')
allTrainData = allTrainData.append(df)
trainData = dataPreprocess(allTrainData)

print(trainData)
trainData.to_csv("data/finaltest.csv", index=False, encoding='utf_8_sig')
print("Done")
