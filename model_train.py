# -*- coding: utf-8 -*-
# @Time : 2020/12/23 14:19
# @Author : Jclian91
# @File : model_train.py
# @Place : Yangpu, Shanghai
import codecs
import json
import os
import numpy as np
import pandas as pd
from keras.layers import *
from keras.models import Model
from keras.optimizers import Adam
from keras_bert import Tokenizer
from albert import load_brightmart_albert_zh_checkpoint, build_albert
from sklearn.utils import shuffle

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# 建议长度 <= 510
maxlen = 300
BATCH_SIZE = 1
dict_path = './albert_xlarge_zh_183k/vocab.txt'




token_dict = {}
with codecs.open(dict_path, 'r', 'utf-8') as reader:
    for line in reader:
        token = line.strip()
        token_dict[token] = len(token_dict)


class OurTokenizer(Tokenizer):
    def _tokenize(self, text):
        R = []
        for c in text:
            if c in self._token_dict:
                R.append(c)
            else:
                R.append('[UNK]')  # 剩余的字符是[UNK]
        return R


tokenizer = OurTokenizer(token_dict)


def seq_padding(X, padding=0):
    L = [len(x) for x in X]
    ML = max(L)
    return np.array([
        np.concatenate([x, [padding] * (ML - len(x))]) if len(x) < ML else x for x in X
    ])


class DataGenerator:

    def __init__(self, data, batch_size=BATCH_SIZE):
        self.data = data
        self.batch_size = batch_size
        self.steps = len(self.data) // self.batch_size
        # self.steps = 10
        if len(self.data) % self.batch_size != 0:
            self.steps += 1

    def __len__(self):
        return self.steps

    def __iter__(self):
        while True:
            idxs = list(range(len(self.data)))
            np.random.shuffle(idxs)
            X1, X2, Y = [], [], []
            for i in idxs:
                d = self.data[i]
                text = d[0][:maxlen]
                x1, x2 = tokenizer.encode(first=text)
                y = d[1]
                X1.append(x1)
                X2.append(x2)
                Y.append(y)
                if len(X1) == self.batch_size or i == idxs[-1]:
                    X1 = seq_padding(X1)
                    X2 = seq_padding(X2)
                    Y = seq_padding(Y)
                    yield [X1, X2], Y
                    [X1, X2, Y] = [], [], []


# 构建模型
def create_cls_model(num_labels):
    albert_model = load_brightmart_albert_zh_checkpoint('albert_xlarge_zh_183k', training=False)

    for layer in albert_model.layers:
        layer.trainable = True

    x1_in = Input(shape=(None,))
    x2_in = Input(shape=(None,))

    x = albert_model([x1_in, x2_in])
    x = Lambda(lambda x: x[:, 0])(x)  # 取出[CLS]对应的向量用来做分类
    p = Dense(num_labels, activation='softmax')(x)  # 多分类

    model = Model([x1_in, x2_in], p)
    model.compile(
        loss='categorical_crossentropy',
        optimizer=Adam(1e-5),  # 用足够小的学习率
        metrics=['accuracy']
    )
    model.summary()

    return model


if __name__ == '__main__':

    # 数据处理, 读取训练集和测试集
    print("begin data processing...")
    train_df = pd.read_csv("data/train.csv").fillna(value="")#dropna(axis=0,subset=["content", "title"])
    train_df = shuffle(train_df)
    print(train_df.head(100))
    test_df = pd.read_csv("data/testData.csv").fillna(value="")

    labels = train_df["channelName"].unique()
    with open("label.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(dict(zip(range(len(labels)), labels)), ensure_ascii=False, indent=2))

    train_data = []
    test_data = []
    for i in range(train_df.shape[0]):
        content, label = train_df.iloc[i, :]

        label_id = [0] * len(labels)
        for j, _ in enumerate(labels):
            if _ == label:
                label_id[j] = 1
        if len(content) > 300:
            train_data.append((content, label_id))

    for i in range(test_df.shape[0]):
        content, label = test_df.iloc[i, :]
        label_id = [0] * len(labels)
        for j, _ in enumerate(labels):
            if _ == label:
                label_id[j] = 1
        test_data.append((content, label_id))

    print("finish data processing!")

    # 模型训练
    model = create_cls_model(len(labels))
    train_D = DataGenerator(train_data)
    test_D = DataGenerator(test_data)

    print("begin model training...")
    model.fit_generator(
        train_D.__iter__(),
        # steps_per_epoch=len(train_D),
        steps_per_epoch=7000,
        epochs=1,
        validation_data=test_D.__iter__(),
        validation_steps=len(test_D)
    )

    print("finish model training!")

    # 模型保存
    model.save('albert_model.h5')
    print("Model saved!")

    result = model.evaluate_generator(test_D.__iter__(), steps=len(test_D))
    print("模型评估结果:", result)
