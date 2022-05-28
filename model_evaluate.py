# -*- coding: utf-8 -*-
# @Time : 2020/12/23 15:28
# @Author : Jclian91
# @File : model_evaluate.py
# @Place : Yangpu, Shanghai
# 模型评估脚本
import json
import numpy as np
import pandas as pd
from keras.models import load_model
# from keras_bert import get_custom_objects
from albert import get_custom_objects
from sklearn.metrics import classification_report

from model_train import token_dict, OurTokenizer
import xlwt
# 导入CSV安装包
import csv
maxlen = 300

# 加载训练好的模型
model = load_model("albert_model.h5", custom_objects=get_custom_objects())
tokenizer = OurTokenizer(token_dict)
with open("label.json", "r", encoding="utf-8") as f:
    label_dict = json.loads(f.read())


# 对单句话进行预测
def predict_single_text(text):
    # 利用BERT进行tokenize
    text = text[:maxlen]
    x1, x2 = tokenizer.encode(first=text)
    X1 = x1 + [0] * (maxlen - len(x1)) if len(x1) < maxlen else x1
    X2 = x2 + [0] * (maxlen - len(x2)) if len(x2) < maxlen else x2

    # 模型预测并输出预测结果
    predicted = model.predict([[X1], [X2]])
    y = np.argmax(predicted[0])
    return label_dict[str(y)]

# 模型单条数据的预测
def predSingle(title, content):
    pred_y = predict_single_text(title+content)
    return pred_y


# 模型文件预测
def predCSV():
    test_df = pd.read_csv("data/finaltest.csv").fillna(value="")
    true_y_list, pred_y_list = [], []
    # 创建一个workbook 设置编码
    workbook = xlwt.Workbook(encoding='utf-8')
    # 创建一个worksheet
    worksheet = workbook.add_sheet('My Worksheet')

    # 写入excel
    # 参数对应 行, 列, 值
    worksheet.write(0, 0, label='编号')
    worksheet.write(0, 1, label='channelName')
    worksheet.write(0, 2, label='title')
    worksheet.write(0, 3, label='content')
    for i in range(test_df.shape[0]):
    # for i in range(30):
    #     print("predict %d samples" % (i+1))
        num, label, title, content = test_df.iloc[i, :]
        # content, label = test_df.iloc[i, :]
        pred_y = predict_single_text(content)
        pred_y_list.append(pred_y)
        # print(num, label, title, content)
        worksheet.write(i + 1, 0, label=str(num))
        worksheet.write(i + 1, 1, label=str(pred_y))
        worksheet.write(i + 1, 2, label=str(title))
        worksheet.write(i + 1, 3, label=str(content))
        print(pred_y, content)

    # 保存
    workbook.save('data/test_result.xls')
    # return classification_report(true_y_list, pred_y_list, digits=4)

# 单条新闻的评估类别
def evalSingle(label, title, content):
    pred_y = predict_single_text(title+content)
    return '真实类别：', label, '预测类别', pred_y



# 模型评估
def evaluate():
    test_df = pd.read_csv("data/test.csv").fillna(value="")
    true_y_list, pred_y_list = [], []
    for i in range(test_df.shape[0]):
        print("predict %d samples" % (i+1))
        content, true_y = test_df.iloc[i, :]
        pred_y = predict_single_text(content)
        true_y_list.append(true_y)
        pred_y_list.append(pred_y)
        if true_y == pred_y:
            print('yes', true_y, pred_y)
        else:
            print('no', true_y, pred_y)

    return classification_report(true_y_list, pred_y_list, digits=4)
# 返回数据分类的结果 分析结果


output_data = evaluate()
# predCSV()
print("model evaluate result:\n")
print(output_data)
