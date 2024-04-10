from pyhanlp import *
import zipfile
import os
from pyhanlp.static import download, remove_file, HANLP_DATA_PATH

# 获取存储数据的根目录：D:\software\miniconda\envs\version37\Lib\site-packages\pyhanlp\static\data\test
def test_data_path():
    data_path = os.path.join(HANLP_DATA_PATH, 'test')
    if not os.path.isdir(data_path):
        os.mkdir(data_path)
    return data_path

# 验证是否存在语料库CTB8.0，如果没有自动下载
def ensure_data(data_name, data_url):
    root_path = test_data_path()  # 获取根路径
    dest_path = os.path.join(root_path, data_name)  # 根据根路径和语料库名称，构造目标路径
    if os.path.exists(dest_path):  # 若目标路径存在，则直接返回该路径，表明语料库已经存在
        return dest_path
    if data_url.endswith('.zip'):
        dest_path += '.zip'
    download(data_url, dest_path)  # 调用download函数，下载指定语料库文件到目标路径
    if data_url.endswith('.zip'):  # 解压并删除下载的压缩文件
        with zipfile.ZipFile(dest_path, "r") as archive:
            archive.extractall(root_path)
        remove_file(dest_path)
        dest_path = dest_path[:-len('.zip')]
    return dest_path  # 返回目标路径

# 从HanLP库中导入“KBeamArcEagerDependencyParser”类（封装有依存句法分析实现）
KBeamArcEagerDependencyParser = JClass('com.hankcs.hanlp.dependency.perceptron.parser.KBeamArcEagerDependencyParser')
# 定义用于训练、验证、测试和CTB8.0数据集的文件路径
CTB_ROOT = ensure_data("ctb8.0-dep", "http://file.hankcs.com/corpus/ctb8.0-dep.zip")
CTB_TRAIN = CTB_ROOT + "/train.conll"
CTB_DEV = CTB_ROOT + "/dev.conll"
CTB_TEST = CTB_ROOT + "/test.conll"
CTB_MODEL = CTB_ROOT + "/ctb.bin"  # 存储训练好的依存句法分析模型，以便于按需加载使用
# 导入wiki-cn-cluster.txt文件，用于中文分词的嵌入表示
BROWN_CLUSTER = ensure_data("wiki-cn-cluster.txt", "http://file.hankcs.com/corpus/wiki-cn-cluster.zip")
# 训练依存句法解析器
parser = KBeamArcEagerDependencyParser.train(CTB_TRAIN, CTB_DEV, BROWN_CLUSTER, CTB_MODEL)
# 使用训练好的解析器，对指定句子完成依存句法分析
doc = parser.parse("小吴在净月潭徒步的过程中偶遇了小王。")
# 依存分析结果
print(doc)