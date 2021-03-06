import tensorflow as tf
import keras
from keras import backend as K
from keras.callbacks import Callback
import pickle
import numpy as np
import heapq
import operator
import os
import MaskFlatten
from graph import GraphConvolution
from utils import *

_TEST_RATIO = 0.15
_VALIDATION_RATIO = 0.1
gru_dimentions = 128
codeCount = 5608  # icd9+ccs分类数
labelCount = 272  # 标签的类别数
SYM_NORM = True


# gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)
# os.environ['CUDA_VISIBLE_DEVICES'] = '2'


def load_data(seqFile, labelFile, treeFile=''):
    sequences = np.array(pickle.load(open(seqFile, 'rb')))
    labels = np.array(pickle.load(open(labelFile, 'rb')))
    labels = np.expand_dims(labels, axis=1)
    if len(treeFile) > 0:
        trees = np.array(pickle.load(open(treeFile, 'rb')))

    np.random.seed(0)
    dataSize = len(labels)
    ind = np.random.permutation(dataSize)
    nTest = int(_TEST_RATIO * dataSize)
    nValid = int(_VALIDATION_RATIO * dataSize)

    test_indices = ind[:nTest]
    valid_indices = ind[nTest:nTest+nValid]
    train_indices = ind[nTest+nValid:]

    train_set_x = sequences[train_indices]
    train_set_y = labels[train_indices]
    test_set_x = sequences[test_indices]
    test_set_y = labels[test_indices]
    valid_set_x = sequences[valid_indices]
    valid_set_y = labels[valid_indices]
    train_set_t = None
    test_set_t = None
    valid_set_t = None

    if len(treeFile) > 0:
        train_set_t = trees[train_indices]
        test_set_t = trees[test_indices]
        valid_set_t = trees[valid_indices]

    def len_argsort(seq):
        return sorted(range(len(seq)), key=lambda x: len(seq[x]))

    train_sorted_index = len_argsort(train_set_x)
    train_set_x = [train_set_x[i] for i in train_sorted_index]
    train_set_y = [train_set_y[i] for i in train_sorted_index]

    valid_sorted_index = len_argsort(valid_set_x)
    valid_set_x = [valid_set_x[i] for i in valid_sorted_index]
    valid_set_y = [valid_set_y[i] for i in valid_sorted_index]

    test_sorted_index = len_argsort(test_set_x)
    test_set_x = [test_set_x[i] for i in test_sorted_index]
    test_set_y = [test_set_y[i] for i in test_sorted_index]

    if len(treeFile) > 0:
        train_set_t = [train_set_t[i] for i in train_sorted_index]
        valid_set_t = [valid_set_t[i] for i in valid_sorted_index]
        test_set_t = [test_set_t[i] for i in test_sorted_index]

    train_set = (train_set_x, train_set_y, train_set_t)
    valid_set = (valid_set_x, valid_set_y, valid_set_t)
    test_set = (test_set_x, test_set_y, test_set_t)

    return train_set, valid_set, test_set


def padMatrix(seqs, labels, treeseqs=''):
    # lengths = np.array([len(seq) for seq in seqs]) - 1
    n_samples = len(seqs)
    # maxlen = np.max(lengths)
    maxlen = 41

    x = np.zeros((n_samples, maxlen, codeCount), dtype=np.int8)
    y = np.zeros((n_samples, 1, labelCount), dtype=np.int8)

    # mask = np.zeros((maxlen, n_samples), dtype=np.int8)

    for idx, (seq, lseq) in enumerate(zip(seqs, labels)):
        for xvec, subseq in zip(x[idx, :, :], seq[:-1]):
            xvec[subseq] = 1.
        for yvec, subseq in zip(y[idx, :], lseq):
            yvec[subseq] = 1.
        # mask[:lengths[idx], idx] = 1.
    y = np.squeeze(y)
    return x, y


class MyEmbedding(keras.layers.Layer):
    def __init__(self,embedding_matrix, **kwargs):
        self.embedding_matrix = embedding_matrix
        super(MyEmbedding, self).__init__(**kwargs)

    def build(self, input_shape):
        # assert isinstance(input_shape, list)
        # Create a trainable weight variable for this layer.
        self.kernel = self.add_weight(name='embedding_matrix',
                                      shape=(self.embedding_matrix.shape[0], self.embedding_matrix.shape[1]),
                                      initializer=keras.initializers.constant(self.embedding_matrix),
                                      trainable=True)
        super(MyEmbedding, self).build(input_shape)  # Be sure to call this at the end

    def call(self, inputs):
        # assert isinstance(x, list)
        emb = K.tanh(K.dot(inputs, self.kernel))
        return emb


class metricsHistory(Callback):
    def __init__(self):
        super().__init__()
        self.Recall_5 = []
        self.Precision_5 = []
        # self.path = 'G:\\模型训练保存\\ourmodel_' + str(gru_dimentions) + '_dropout\\rate05_02\\'
        # self.fileName = 'model_metrics.txt'

    def on_epoch_end(self, epoch, logs={}):
        pred = model.predict(x_test)
        # precision5 = visit_level_precision(test_set[1], convert2preds(
        #     model.predict(x_test)))[0]
        recall5 = self.code_level_accuracy(test_set[1], self.convert2preds(pred))[0]
        # self.Precision_5.append(precision5)
        self.Recall_5.append(recall5)
        # metricsInfo = 'Epoch: %d, - Recall@5: %f, - Precision@5: %f' % (epoch+1, recall5, precision5)
        metricsInfo = 'Epoch: %d, - Recall@5: %f' % (epoch + 1, recall5)
        # self.print2file(metricsInfo, self.path, self.fileName)
        print(metricsInfo)

    def on_train_end(self, logs={}):
        print('Recall@5为:',self.Recall_5,'\n')
        print('Precision@5为:',self.Precision_5)
        # self.print2file('Recall@5:'+str(self.Recall_5), self.path, self.fileName)
        # self.print2file('Precision@5:'+str(self.Precision_5), self.path, self.fileName)

    def visit_level_precision(self, y_true, y_pred, rank=[5]):
        recall = list()
        for i in range(len(y_true)):
            thisOne = list()
            codes = y_true[i]
            tops = y_pred[i]
            for rk in rank:
                thisOne.append(len(set(codes).intersection(set(tops[0][:rk]))) * 1.0 / min(rk, len(set(codes))))
            recall.append(thisOne)
        return (np.array(recall)).mean(axis=0).tolist()

    def code_level_accuracy(self, y_true, y_pred, rank=[5]):
        recall = list()
        y_true = np.squeeze(y_true)
        for i in range(len(y_true)):
            thisOne = list()
            codes = y_true[i]
            tops = y_pred[i]
            for rk in rank:
                thisOne.append(len(set(codes).intersection(set(tops[0][:rk]))) * 1.0 / len(set(codes)))
            recall.append(thisOne)
        return (np.array(recall)).mean(axis=0).tolist()

    # 按从大到小取预测值中前30个ccs分组号
    def convert2preds(self, preds):
        ccs_preds = []
        for i in range(len(preds)):
            temp = []
            temp.append(list(zip(*heapq.nlargest(30, enumerate(preds[i]), key=operator.itemgetter(1))))[0])
            ccs_preds.append(temp)
        return ccs_preds

    def print2file(self, buf, dirs, fileName):
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        outFile = dirs + fileName
        outfd = open(outFile, 'a')
        outfd.write(buf + '\n')
        outfd.close()


def convert_sparse_matrix_to_sparse_tensor(X):
    coo = X.tocoo()
    indices = np.mat([coo.row, coo.col]).transpose()
    return tf.SparseTensor(indices, coo.data, coo.shape)


if __name__ == '__main__':
    seqFile = '../resource/mimic3_all.seqs'
    labelFile = '../resource/mimic3.labels'
    adjFile = '../resource/mimic3.adj'
    # graphFile = '../resource/mimic3.graph'
    # g = pickle.load(open(graphFile, 'rb'))
    A = pickle.load(open(adjFile,'rb'))
    # data_seqs = pickle.load(open('./resource/process_data/process.dataseqs', 'rb'))
    # label_seqs = pickle.load(open('./resource/process_data/process.labelseqs', 'rb'))
    # types = pickle.load(open('./resource/build_trees.types', 'rb'))
    # retype = dict([(v, k) for k, v in types.items()])

    train_set, valid_set, test_set = load_data(seqFile, labelFile)
    x, y = padMatrix(train_set[0], train_set[1])
    x_valid, y_valid = padMatrix(valid_set[0], valid_set[1])
    x_test, y_test = padMatrix(test_set[0], test_set[1])

    A_ = preprocess_adj(A, SYM_NORM)
    A_ = convert_sparse_matrix_to_sparse_tensor(A_)
    B = [A_ for i in range(5626)]
    B = np.asarray(B)
    C = [A_ for i in range(749)]
    C = np.asarray(C)
    support = 1
    graph = [x, B]
    G = [keras.Input(shape=(None, None), batch_shape=(None, None), sparse=True)]
    # G = K.expand_dims(G, 0)
    model_input = keras.layers.Input((x.shape[1], x.shape[2]), name='model_input')
    transponse = keras.layers.Permute((2, 1))(model_input)
    mask = keras.layers.Masking(mask_value=0)(transponse)
    # mask = tf.expand_dims(mask, axis=-1)
    # embLayer = MyEmbedding(glove_patient_emb)
    # emb = embLayer(mask)
    # print(g.shape)
    print(mask.shape.ndims)
    H = GraphConvolution(16, support, activation='relu')([mask] + G)
    # gru = keras.layers.GRU(gru_dimentions, dropout=0.5)(mask)
    # sa = keras.layers.Attention(use_scale=True)([gru_out,gru_out])
    # regcn = keras.layers.Permute((1, 2))(gcn)
    print(H.shape)
    H = MaskFlatten.MyFlatten()(H)
    model_output = keras.layers.Dense(labelCount, activation='softmax', name='model_output')(H)

    model = keras.models.Model(inputs=[model_input]+G, outputs=model_output)

    # checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath='G:\\模型训练保存\\ourmodel_' + str(gru_dimentions) + '_dropout\\rate05_02\\model_{epoch:02d}', save_freq='epoch')
    # batch_print_callback = tf.keras.callbacks.LambdaCallback(
    #     on_epoch_end=lambda batch, logs: print('Precision@5:',visit_level_precision(process_label(test_set[1]), convert2preds(model.predict([x_test, tree_test], batch_size=100)))[0],
    #                                             'Recall@5:',code_level_accuracy(process_label(test_set[1]), convert2preds(model.predict([x_test, tree_test], batch_size=100)))[0]))

    model.summary()
    model.compile(optimizer='adam', loss='binary_crossentropy')

    callback_history = metricsHistory()
    history = model.fit(graph, y,
                        epochs=1,
                        batch_size=100,
                        validation_data=([x_valid, C], y_valid))
                        # callbacks=[callback_history])
