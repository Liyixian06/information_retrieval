stop_words = []

with open('hit_stopwords.txt','r',encoding='utf-8',errors='ignore') as f:
    word = f.readline()
    while word:
        stop_words.append(word)
        word = f.readline()
    print(len(stop_words))
with open('baidu_stopwords.txt','r',encoding='utf-8',errors='ignore') as f:
    word = f.readline()
    while word:
        stop_words.append(word)
        word = f.readline()
    print(len(stop_words))
with open('scu_stopwords.txt','r',encoding='utf-8',errors='ignore') as f:
    word = f.readline()
    while word:
        stop_words.append(word)
        word = f.readline()
    print(len(stop_words))
with open('cn_stopwords.txt','r',encoding='utf-8',errors='ignore') as f:
    word = f.readline()
    while word:
        stop_words.append(word)
        word = f.readline()
    print(len(stop_words))

stop_words = list(set(stop_words))
print(len(stop_words))

with open('./stopwords.txt','w',newline='') as f:
    f.writelines(stop_words)