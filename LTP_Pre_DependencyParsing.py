import os
import networkx as nx
import matplotlib.pyplot as plt
from pyltp import Segmentor, Postagger, Parser
# 保证生成的图表，能正常显示中文。
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 定义“有向图”形式的可视化组件
def visualize_dependency_tree(words, child_dict_list):
    '''
    输入1：words = ['小', '吴', '在', '净月潭', '徒步', '，', '偶遇', '了', '小王', '。']
    输入2：child_dict_list = [{}, {'ATT': [0]}, {'POB': [3]}, {}, {'SBV': [1], 'ADV': [2], 'WP': [5]}, {}, {'ADV': [4], 'RAD': [7], 'VOB': [8], 'WP': [9]}, {}, {}, {}]
    '''
    G = nx.DiGraph()
    for i, word in enumerate(words):  # 添加节点
        G.add_node(word)
    for i, child_dict in enumerate(child_dict_list):  # 添加边
        for relation, children in child_dict.items():
            for child in children:
                G.add_edge(words[i], words[child], label=relation)
    pos = nx.spring_layout(G, k=0.5)  # 自定义布局
    nx.draw(G, pos, with_labels=True, arrows=True)  # 绘制节点和边
    labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, label_pos=0.5, font_size=8)
    plt.show()

# 基于pyltp预训练模型的依存句法分析实现
class LtpParser:
    def __init__(self):
        LTP_DIR = "./myLTP/ltp_data_v3.4.0"
        self.segmentor = Segmentor()  # 分词
        self.segmentor.load(os.path.join(LTP_DIR, "cws.model"))
        self.postagger = Postagger()  # 词性标注
        self.postagger.load(os.path.join(LTP_DIR, "pos.model"))
        self.parser = Parser()  # 句法依存分析
        self.parser.load(os.path.join(LTP_DIR, "parser.model"))

    def build_parse_child_dict(self, words, postags):
        '''
            输入1：words = ['小', '吴', '在', '净月潭', '徒步', '，', '偶遇', '了', '小王', '。']
            输入2：postags = ['a', 'nh', 'p', 'ns', 'd', 'wp', 'v', 'u', 'nh', 'wp']
            输出：child_dict_list = [{}, {'ATT': [0]}, {'POB': [3]}, {}, {'SBV': [1], 'ADV': [2], 'WP': [5]}, {}, {'ADV': [4], 'RAD': [7], 'VOB': [8], 'WP': [9]}, {}, {}, {}]
        '''
        child_dict_list = []
        arcs = self.parser.parse(words, postags)  # 获取句子的依存句法分析结果
        rely_ids = [arc.head - 1 for arc in arcs]  # 提取每个分词的依存父节点id【-1表示ROOT，id从0开始】
        heads = ['Root' if rely_id == -1 else words[rely_id] for rely_id in rely_ids]  # 根据rely_ids记录每个分词的依存父节点分词
        relations = [arc.relation for arc in arcs]  # 提取依存关系
        for word_index in range(len(words)):  # 循环遍历每个分词，为每个分词构建一个字典：键为依存关系，值为存储对应依存关系词语索引的列表
            child_dict = dict()
            for arc_index in range(len(arcs)):
                if word_index == rely_ids[arc_index]:
                    if relations[arc_index] in child_dict:
                        child_dict[relations[arc_index]].append(arc_index)
                    else:
                        child_dict[relations[arc_index]] = []
                        child_dict[relations[arc_index]].append(arc_index)
            child_dict_list.append(child_dict)
        return child_dict_list

    def parser_main(self, sentence):
        words = list(self.segmentor.segment(sentence))  # 分词
        postags = list(self.postagger.postag(words))  # 词性标注
        child_dict_list = self.build_parse_child_dict(words, postags)  # 依存句法分析
        return words, postags, child_dict_list

# 主函数
if __name__ == '__main__':
    # 实例化句法分析实现类
    parse = LtpParser()
    # 定义待处理的中文句子
    sentence = '小吴在净月潭徒步，偶遇了小王。'
    # 调用parse对象中的parser_main函数，完成句子的分词、词性标注及依存句法分析任务
    words, postags, child_dict_list = parse.parser_main(sentence)
    # 在控制台打印结果
    print("\n\n\n分词-->len(words) = {0}----words = {1}".format(len(words), words))
    print("\n词性标注-->len(postags) = {0}----postags = {1}".format(len(postags), postags))
    print("\n依存句法分析-->每个词对应的依存关系儿子节点和其关系-->len(child_dict_list) = {0}----child_dict_list = {1}".format(len(child_dict_list), child_dict_list))
    # 生成依存句法分析结果的有向图表示
    visualize_dependency_tree(words, child_dict_list)