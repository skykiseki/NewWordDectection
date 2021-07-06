import numpy as np
import re
import pandas as pd
from datetime import datetime

def extract_cadicateword(doc, max_word_len):
    """
    提取文档中的候选词汇索引

    Parameters:
    ----------
    doc: 输入的剔除了特殊符号的语料

    max_word_len: 最长的单词长度

    Returns:
    -------
    indexs: 候选词的索引
    """
    indexes = []
    doc_length = len(doc)
    for i in range(doc_length):
        for j in range(i + 1, min(i + 1 + max_word_len, doc_length + 1)):
            indexes.append((i, j))
    return indexes

def compute_entropy(word_list):
    """
    计算单词的左熵 或者 右熵

    熵计算公式 = -1 * 临近词汇词频 / 临近词汇个数 * ln(临近词汇词频 / 临近词汇个数)

    Parameters:
    ----------
    word_list: 邻近的单词列表

    Returns:
    -------
    基于临近词计算的左右熵结果
    """
    # 邻近的单词个数
    length = len(word_list)

    # 临近词字典， word: word_frequency
    frequence = {}
    if length == 0:
        return 0
    else:
        for i in word_list:
            frequence[i] = frequence.get(i, 0) + 1

        return sum([- f / length * np.log(f / length) for f in frequence.values()])



class WordInfo(object):
    """
    词频的类, 记录单词的词频, 左右熵, pmi等

    Attributes:
    ----------
    word: 单词
    len_word: 单词长度
    freq: 单词词频
    freq_tf: 单词词频占比
    left: 单词左邻单词
    right: 单词右邻单词
    left_ent: 单词左熵
    right_ent: 单词右熵
    lr_ent: 单词左右熵 = min(单词左熵, 单词右熵)
    pmi: 互信息
    """

    def __init__(self, word):
        self.word = word
        self.len_word = len(word)
        self.freq = 0
        self.freq_tf = 0
        self.left = []
        self.right = []
        self.left_ent = 0
        self.right_ent = 0
        self.lr_ent = 0
        self.pmi = 0

    def update_word(self, left, right):
        """
        更新单词的词频，左右邻词

        Parameters:
        ----------
        left: 左词
        right: 右词

        Returns:
        -------
        self
        """
        # 词频加1
        self.freq += 1

        # 添加左右邻词
        if len(left) > 0:
            self.left.append(left)

        if len(right) > 0:
            self.right.append(right)

    def compute_indexes(self, doc_length):
        """
        计算单词的左右熵

        Parameters:
        ----------
        doc_length: 文档长度

        Returns:
        -------
        self
        """
        # 更新单词的词频占比
        self.freq_tf = self.freq / doc_length

        # 更新左熵
        self.left_ent = compute_entropy(self.left)

        # 更新右熵
        self.right_ent = compute_entropy(self.right)

        # 左右熵
        self.lr_ent = min(self.left_ent, self.right_ent)

    def compute_pmi(self, word_cad):
        """
        计算单词的pmi

        pmi = 2-gram拆分后, ln[本词词频占比 / (左边词词频占比 * 右边词词频占比)]

        Parameters:
        ----------
        word_cad: 输入的候选词词典 {word: word_obj}

        Returns:
        -------
        self
        """
        # n_gram
        sub_n_gram = [(self.word[0: i], self.word[i:]) for i in range(1, len(self.word))]

        if len(sub_n_gram) > 0:
            self.pmi = min([np.log(self.freq_tf / (word_cad[sub[0]].freq_tf * word_cad[sub[1]].freq_tf)) for sub in sub_n_gram])

class SegDocument(object):
    """
    切词的类

    Attributes:
    ----------
    doc: 原始语料

    max_word_len: 单个词的最长长度

    min_tf: 最小的词频占比

    min_entropy: 最小的熵值

    min_pmi: 最小的互信息值

    word_info: 字对象列表

    avg_frq: 平均词频

    avg_ent: 平均熵

    avg_pmi:平均pmi

    word_tf_pmi_ent: 满足阈值条件的词对象列表
    """

    def __init__(self, doc, max_word_len=15, min_tf=1e-08, min_entropy=1, min_pmi=3.0):
        # 基本属性
        self.max_word_len = max_word_len
        self.min_tf = min_tf
        self.min_entropy = min_entropy
        self.min_pmi = min_pmi
        self.word_info = self.gen_words(doc=doc)
        self.avg_frq = sum([word.freq for word in self.word_info]) / len(self.word_info)
        self.avg_ent = sum([word.lr_ent for word in self.word_info]) / len(self.word_info)
        self.avg_pmi = sum([word.pmi for word in self.word_info]) / len(self.word_info)

        self.word_tf_pmi_ent = []
        for word_obj in self.word_info:
            # print(word_obj.word, word_obj.lr_ent, word_obj.pmi, word_obj.freq_tf)
            if word_obj.lr_ent > self.min_entropy and word_obj.pmi > self.min_pmi and word_obj.freq_tf > self.min_tf:
                if word_obj.len_word > 1:
                    self.word_tf_pmi_ent.append(word_obj)

    def gen_words(self, doc):
        """
        基于语料的n-gram模型, 计算pmi

        Parameters:
        ----------
        doc: 原始语料

        Returns:
        -------
        list_words: 字对象的列表
        """
        # 剔除特殊符号
        #pattern = re.compile(u'[\\s\\d,.<>/?:;\'\"[\\]{}()\\|~!@#$%^&*\\-_=+a-zA-Z，。《》、？：；“”‘’｛｝【】（）…￥！—┄－]+')
        #doc = pattern.sub(r'', doc)
        pattern = re.compile(u'[\u4e00-\u9fa5]')
        doc = ''.join(pattern.findall(pattern))

        # 文档长度
        len_doc = len(doc)

        # 提取所有可能的候选词汇索引
        word_index = extract_cadicateword(doc, max_word_len=self.max_word_len)

        # 遍历索引组合, 生成候选词词典, 一个词生成一个词对象
        word_cad = {}
        for suffix in word_index:
            # 抓取单词
            word = doc[suffix[0]: suffix[1]]

            # 如果单词不在候选词典, 则创建该词语以及对象, 初始词频是0
            if word not in word_cad.keys():
                word_cad[word] = WordInfo(word)
            # 更新单词的对象信息
            left_word = doc[suffix[0] - 1: suffix[0]]
            right_word = doc[suffix[1]: suffix[1] + 1]

            word_cad[word].update_word(left=left_word, right=right_word)

        # 计算每个词的左右熵
        for word in word_cad.keys():
            word_cad[word].compute_indexes(doc_length=len_doc)

        # 计算每个词的pmi
        for word_obj in word_cad.values():
            if len(word_obj.word) == 1:
                continue
            else:
                word_obj.compute_pmi(word_cad=word_cad)

        list_words = sorted(list(word_cad.values()), key=lambda w: len(w.word), reverse=False)
        return list_words

def get_doc_words(corpus, max_word_len=15, min_tf=1e-08, min_entropy=1, min_pmi=3.0):
    """
    最终提供调用的函数

    Parameters:
    ----------
    corpus: 输入的长文本字符串,可包含特殊字符
    max_word_len: N-gram滑动的窗口大小
    min_tf: 最小的词频占比
    min_entropy: 最小左右熵阈值
    min_pmi: 最小互信息阈值

    Returns:
    -------
    df_words: Dataframe, 最后形成的词库df统计

    """
    # 记录开始时间
    st_time = datetime.now()

    # 初始化词表
    doc_obj = SegDocument(corpus,
                          max_word_len=max_word_len,
                          min_tf=min_tf,
                          min_entropy=min_entropy,
                          min_pmi=min_pmi)

    # 将对应的词表以及相关统计值形成dataframe
    df_words = pd.DataFrame(columns=['word', 'word_length', 'word_freq', 'word_pmi', 'word_entropy'])
    # 将词逐个插入dataframe
    for word_obj in doc_obj.word_tf_pmi_ent:
        df_words = df_words.append({'word': word_obj.word,
                                    'word_length': word_obj.len_word,
                                    'word_freq': word_obj.freq,
                                    'word_pmi': word_obj.pmi,
                                    'word_entropy': word_obj.lr_ent}, ignore_index=True)

    # 记录结束时间
    ed_time = datetime.now()

    # 记录执行时间
    print('Time executed:{0}'.format(ed_time - st_time))

    return df_words