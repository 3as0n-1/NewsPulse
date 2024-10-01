import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoTokenizer, AutoModel



file_path = 'data/analysis_report.csv'  
df = pd.read_csv(file_path)

source = "extracted_news_info"
# 2. 标签分割
df['tags'] = df[source].apply(lambda x: x.split('/'))

# 3. 标签编码
mlb = MultiLabelBinarizer()
tag_encoded = mlb.fit_transform(df['tags'])
tag_df = pd.DataFrame(tag_encoded, columns=mlb.classes_)

# 4. 初始化 tokenizer 和 model
tokenizer = AutoTokenizer.from_pretrained("hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2")
model = AutoModel.from_pretrained("hw2942/bert-base-chinese-finetuning-financial-news-sentiment-v2")

# 5. 定义获取 BERT 嵌入向量的函数
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():  # 禁用梯度计算以节省内存
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()  # 获取 [CLS] token 的输出向量

# 6. 获取所有文本的嵌入向量
valid_texts = df[source].tolist()  # 使用原始文本
embeddings = np.array([get_embedding(text) for text in valid_texts])

# 7. KMeans 聚类
num_clusters = 5  
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(embeddings)

# 8. 输出聚类结果
for index, row in df.iterrows():
    print(f"News: {df['ID'][index]}, Cluster: {row['cluster']}")



# 8. 降维到二维进行可视化
# pca = PCA(n_components=2)
# reduced_embeddings = pca.fit_transform(embeddings)

# # 9. 可视化聚类结果
# plt.figure(figsize=(12, 8))
# sns.scatterplot(x=reduced_embeddings[:, 0], y=reduced_embeddings[:, 1], hue=df['cluster'], palette='Set1', s=100)

# # 添加每个点的文本标签
# for i, txt in enumerate(valid_texts):
#     plt.annotate(i + 1, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]), fontsize=9, alpha=0.7)

# plt.title('KMeans Clustering of News Articles')
# plt.xlabel('PCA Component 1')
# plt.ylabel('PCA Component 2')
# plt.legend(title='Cluster')
# plt.grid(True)
# plt.show()

