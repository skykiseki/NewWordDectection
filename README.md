# NewWordDectection
"新词发现"

目前仅有基于苏神（苏剑林）文章写的左右熵以及互信息方法进行词库建设，其他的算法后面有空会继续更新


具体链接参考
[《新词发现的信息熵方法与实现》](https://spaces.ac.cn/archives/3491)

# 安装说明

```shell
pip install new-words-detection
```

# 使用说明
```python
# 加载模块
from new_words_detection.wordSegment import get_doc_words
    
# 准备预料, 输入时一个字符长串, 可含特殊字符
corpus = '哈哈哈哈哈哈哈哈哈哈哈或或或或或或或或或或或或或或或或或或或或或或或或或或或或或'
    
# 得到的输出是可成的词以及对应的pmi, 左右熵等信息
df_words = get_doc_words(corpus)
```

# 最终结果

| word                   | word_length | word_freq | word_pmi | word_entropy |
|:-----------------------|:------------|:----------|:---------|:-------------|
| 我爱你你爱我蜜雪冰城甜蜜蜜  | 13          | 1       | 3.3      | 2.333333333  |


# 参数解释

- corpus: 输入的长文本字符串,可包含特殊字符
- max_word_len: N-gram滑动的窗口大小
- min_tf: 最小的词频占比
- min_entropy: 最小左右熵阈值
- min_pmi: 最小互信息阈值
- min_tf: 最小的词频占比


