import matplotlib.pyplot as plt
import pandas as pd


def plot_learning_curves(history, label, epochs, min_value, max_value):
        data = {}
        data[label+'0'] = history[label+'0']
        data[label + '0.2'] = history[label + '0.2']
        data[label + '0.5'] = history[label + '0.5']
        data[label + '0.8'] = history[label + '0.8']
        plt.rcParams["figure.dpi"] = 140
        plt.style.use('ggplot')
        pd.DataFrame(data).plot(figsize=(8, 5))

        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.grid(True)
        plt.axis([0, epochs, min_value, max_value])
        plt.ylabel('Recall@5')
        plt.xlabel('迭代次数')
        plt.title('MIMIC-III数据集')
        plt.show()


if __name__ == '__main__':
    data = {}
    data['Dropout rate=0'] = [0, 0.17575517883271943, 0.21165603304044578, 0.2308848099642392, 0.24680579501634026, 0.2523783906906704, 0.2607169941067118, 0.2640765013910655, 0.2705173461910425, 0.27315292035343663, 0.2753873709954681, 0.2772869857669603, 0.2812802465791237, 0.28104603106940673, 0.2828757395384719, 0.2820917390571036, 0.2844146502896069, 0.28325676575630776, 0.28569765448166173, 0.28556659079598873, 0.2874838861006091, 0.2855425429319422, 0.28418189635887764, 0.2837941324291408, 0.2845437046589145, 0.28247113104807287, 0.28166688461956524, 0.2828105102942053, 0.2801805663724371, 0.2806087190010359, 0.2795200511893221, 0.27704707169568565, 0.27798352093116385, 0.2771237910841776, 0.27645986762681957, 0.2736089614024877, 0.27351268583095195, 0.2743165874117545, 0.2726286141498151, 0.2709757713203311, 0.269171452320287, 0.268298545545042, 0.2683841226337502, 0.2666688254369583, 0.26279144580484803, 0.26603032944839605, 0.262700426000889, 0.2607078277170833, 0.2595524906025374, 0.25799926972113557]
    data['Dropout rate=0.2'] = [0, 0.18355480365316873, 0.2253519683056792, 0.24259366198176602, 0.2548899037001917, 0.26690253124608593, 0.27518161606027325, 0.28221688925367217, 0.29090550837501084, 0.29011396817037577, 0.2936871001781188, 0.2937448538702283, 0.30104771609623554, 0.30769066012338653, 0.3079669787776703, 0.30728336970828213, 0.3071401050771438, 0.31281729376286943, 0.3068758540282711, 0.3123616338657382, 0.3110863391766525, 0.3132964429483014, 0.31445963194450743, 0.3182756024242332, 0.31674087742937346, 0.3168177214184377, 0.31798114163337976, 0.3163326171796072, 0.3195148670803509, 0.3177065102554918, 0.3137456603678192, 0.3151636290264462, 0.3155389134998266, 0.3169597944212755, 0.31799820996895795, 0.31831100153269914, 0.31685724697284323, 0.3159469346132948, 0.3125346235971083, 0.31435871799366105, 0.3132565051904461, 0.31490127957297853, 0.3142966544771136, 0.31372325818165414, 0.3145670362764208, 0.3117474173739448, 0.31444344519198386, 0.31419835477384706, 0.3138263733732323, 0.31048583115844625]
    data['Dropout rate=0.5'] = [0, 0.1706910700721199, 0.2200505490005364, 0.23498350144643654, 0.2524681040513909, 0.2569730612256779, 0.27470632957386704, 0.2789105636602101, 0.28244254608298547, 0.2867990740047079, 0.29418665919459946, 0.29558559551083846, 0.3014860891019266, 0.30084466801137555, 0.30327536415532963, 0.31050072926526684, 0.3076699273084726, 0.3144333284056145, 0.31241732863504007, 0.31498552832976096, 0.31577348264572574, 0.31064426970377906, 0.31460200028552393, 0.31343261196922156, 0.32009573745647735, 0.3197541887013178, 0.3207292885939303, 0.31872462860037665, 0.3234930696885472, 0.32085418142025035, 0.3221283821151024, 0.3234022459672761, 0.3155974649422905, 0.32523161865037875, 0.3212000390058844, 0.3212885147612926, 0.32409450471877826, 0.3231638931711302, 0.3233080835415442, 0.3246521763269503, 0.3238586314762487, 0.32648022904690577, 0.3241459284684133, 0.32820393984794466, 0.3234745693982036, 0.3232658355983706, 0.3236581217256874, 0.3241523527914206, 0.32682864645423826, 0.3264179269461859]
    data['Dropout rate=0.8'] = [0, 0.15845513507281678, 0.20325562973966818, 0.21941082726333339, 0.22318860876442456, 0.2329342225880974, 0.25050813358474505, 0.2588321955141629, 0.2578515021532559, 0.2629881576205228, 0.27711020515156987, 0.2766223009101461, 0.28663677281573147, 0.2851531122016726, 0.29144331049233657, 0.28415835791421235, 0.2956563957727053, 0.2981009231511066, 0.29764678338326045, 0.300142145713773, 0.29043258524773163, 0.30478255485047434, 0.304403138475993, 0.30837352611962454, 0.3102466209063148, 0.31124024332085154, 0.3114914424515244, 0.31201606694181644, 0.3128833655766479, 0.3136521091154698, 0.3166132166077048, 0.31402884393551034, 0.31298320330834073, 0.3155953147802198, 0.3176121546859037, 0.3188856123487871, 0.32170105644201047, 0.31629677013385415, 0.32046207831558965, 0.31914257956872755, 0.31946885733154856, 0.31755890394369723, 0.3196983078819323, 0.3203031254812066, 0.321655162458033, 0.32001664458112683, 0.3213154188670394, 0.32389717956036157, 0.3212038474013905, 0.3239015202174321]

    plot_learning_curves(data, 'Dropout rate=', 50, 0.15, 0.4)