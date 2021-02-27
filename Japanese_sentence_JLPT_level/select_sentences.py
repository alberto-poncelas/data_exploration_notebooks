
import numpy as np
import pandas as pd
import bisect 

HIRAGANA = list('ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすず'
                'せぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴ'
                'ふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろわ'
                'をんーゎゐゑゕゖゔ')

KATAKANA = list('ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズ'
                'セゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピ'
                'フブプヘベペホボポマミムメモャヤュユョヨラリルレロワ'
                'ヲンーヮヰヱ')

ASCII_chars = list('ゝゞ・「」。、!！"#$%&\'()*+,-./:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789０１２３４５６７８９'
                  '[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ')



JLPT_vocab_path="../HSKandJLPTkanji/data/JLPT_vocab.txt"
pair_sentences_path='data/parallel.ja-en'




#Input parameters
input_vocab="data/input_vocab_extract"
output_path="data/out_sample"
num_selected_sentences=100
JLPT_num_level=2
len_penalty=3



JLPT_vocab = pd.read_csv(JLPT_vocab_path, header = None, sep="\t", names=["kanji","hiragana","English","grade"])

non_kanji_set=set(HIRAGANA+KATAKANA+ASCII_chars)


JLPT_kanji_set = JLPT_vocab["kanji"].astype(str).apply(lambda x:  set(x) - non_kanji_set )
#get pairs of [kanji,grade]
kanji_set=pd.concat([JLPT_kanji_set,JLPT_vocab["grade"]], axis=1)
kanji_grade_list_nested=kanji_set.apply(lambda row: [[x,row['grade']] for x in list(row['kanji'])], axis=1).tolist()
#flatten the list
kanji_grade_list=[item for sublist in kanji_grade_list_nested for item in sublist]
#store in a dictionary where each kanji has the highest (easiest) JLPT grade
kanji_grade_dict=dict()
for x in kanji_grade_list:
    [kj,gr]=x
    kj_grade=kanji_grade_dict.get(kj,0)
    new_grade=max(kj_grade,gr)
    kanji_grade_dict[kj]=new_grade





#Grade sentences
def grade_sentence(s):
    slist=list(s)
    s_kanji_level=[kanji_grade_dict.get(x,0) for x in slist if x not in non_kanji_set]
    if len(s_kanji_level)==0:
        return 0
    else:
        return min(s_kanji_level)

par_sentences = pd.read_csv(pair_sentences_path, header = None, sep="\t", names=["jp","en"] )
JLPT_level=par_sentences["jp"].astype(str).apply(lambda x: grade_sentence(x))
par_sentences["JLPT_level"]=JLPT_level
#remove sentences without kanji or kanji not in the JLPT list
par_sentences=par_sentences[par_sentences["JLPT_level"]>0]





df_sent_level=par_sentences[par_sentences["JLPT_level"]==JLPT_num_level].reset_index()
sentence_list=list(df_sent_level["jp"])
vocab=list( JLPT_vocab[JLPT_vocab["grade"]==JLPT_num_level]["kanji"] )

vocab_df = pd.read_csv(input_vocab, header = None)
vocab=vocab_df[0].tolist()




#Select sentences
N=num_selected_sentences


v_val=dict()
for v in vocab:
    v_val[v]=1.0

def create_tuple(index,list_w,val,slen):
    return (val,index,list_w,slen)

def get_val(tupl):
    return tupl[0]

def get_index(tupl):
    return tupl[1]

def get_list_w(tupl):
    return tupl[2]

def get_len(tupl):
    return tupl[3]

def update_val(tupl):
    list_w=get_list_w(tupl)
    slen=float(get_len(tupl))**len_penalty #increase the penalty of sentence length
    if len(list_w)==0:
        return (0.0,tupl[1],tupl[2],tupl[3])
    s_val=float(sum([v_val.get(x,0.0) for x in list_w]))
    new_val= s_val/slen
    return (new_val,tupl[1],tupl[2],tupl[3])

def decay(v_list):
    for v in v_list:
        old_val=v_val.get(v,0.0)
        new_val=old_val/2.0
        v_val[v]=new_val

def getvocab(s,vocab):
    list_w=[]
    for v in vocab:
        if str(v) in s:
            list_w.append(v)
    return list(set(list_w))

tuples=[]
for i in range(len(sentence_list)):
    s=sentence_list[i]
    list_w=getvocab(s,vocab)
    slen=len(s)
    cur_tuple=create_tuple(i,list_w,0,slen)
    cur_tuple=update_val(cur_tuple)
    tuples.append(cur_tuple)


tuples.sort(key=lambda x: x[0])


i=len(tuples)-1

selected=[]
while i>0 and len(selected)<N:
    top_tuple=tuples[i]
    old_val=get_val(top_tuple)
    top_tuple=update_val(top_tuple)
    new_val=get_val(top_tuple)
    if new_val!=old_val:
        bisect.insort(tuples, top_tuple )
    else:
        i=i-1
        selected.append(get_index(top_tuple))
        decay(get_list_w(top_tuple))




#Write output
dfOut=df_sent_level[["jp","en"]].loc[selected]
dfOut.to_csv(output_path,sep='\t')
dfOut


