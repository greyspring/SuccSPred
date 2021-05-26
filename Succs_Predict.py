#-*- coding: UTF-8 -*-
from sklearn.externals import joblib
from sklearn.svm import SVC
import pandas as pd
import numpy as np
import collections
import fliter
import shutil
import glob
import sys
import os

def main(argv):

    filepath = argv[1]
    datapath,filename = os.path.split(filepath)

    afterpro = r"BioSeq-Analysis\Input_data\data\test.fasta"

    fliter.fileFilter(filepath,afterpro)
    
    f = open(r"BioSeq-Analysis\Input_data\data\test.fasta")
    ls = []
    K_position = []
    sequence_data = []
    for line in f:
        if line.startswith('>'):
            line1 = line.strip('\n')
            for i in range(0,len(line1)):
                if line1[i+1]=='[':
                    break
            ls.append(line1[0:i+1])
            K_position.append(line1[i+2:len(line1)-1])
        else:
            line1 = line.strip('\n')
            sequence_data.append(line1)
    f.close()
    
    os.chdir("BioSeq-Analysis")
    os.system("python Feature_repretation.py Input_data\data\test.fasta")
    os.chdir("..")

    deldir = "BioSeq-Analysis\Input_data\data"
    filelist = os.listdir(deldir)
    for file in filelist:
        del_file = deldir + '\\' + file
        if '.fasta' in file:
            os.remove(del_file)
        else:
            shutil.rmtree(del_file,True)

    tmpdir = "BioSeq-Analysis\Input_data\Input_data_feature\data"

    test = glob.glob(tmpdir + '/test*')

    filegroup = {}
    filegroup['test'] = test

    datadics = datadic(filegroup)
    
    datadics = collections.OrderedDict([("DR.csv",datadics["DR.csv"]),("-PSSM-DT.csv",datadics["-PSSM-DT.csv"]),("SC-PseAAC.csv",datadics["SC-PseAAC.csv"]),("SC-PseAAC-General.csv",datadics["SC-PseAAC-General.csv"]),("-PSSM-RT.csv",datadics["-PSSM-RT.csv"]),("kmer",datadics["kmer"]),("PC-PseAAC.csv",datadics["PC-PseAAC.csv"]),("PC-PseAAC-General.csv",datadics["PC-PseAAC-General.csv"]),("PDT.csv",datadics["PDT.csv"]),("-DT.csv",datadics["-DT.csv"]),("DP.csv",datadics["DP.csv"]),("-Top-n-gram.csv",datadics["-Top-n-gram.csv"]),("-PDT-Profile.csv",datadics["-PDT-Profile.csv"]),("-CC-PSSM.csv",datadics["-CC-PSSM.csv"]),("ACC-PSSM.csv",datadics["ACC-PSSM.csv"]),("-AC-PSSM.csv",datadics["-AC-PSSM.csv"]),("feature-AC.csv",datadics["feature-AC.csv"]),("ACC.csv",datadics["ACC.csv"]),("feature-CC.csv",datadics["feature-CC.csv"])])
    
    processed = process(datadics)

    data = pd.concat([pd.DataFrame(processed["DR.csv"]),pd.DataFrame(processed["-PSSM-DT.csv"]),pd.DataFrame(processed["SC-PseAAC.csv"]),pd.DataFrame(processed["SC-PseAAC-General.csv"]),pd.DataFrame(processed["-PSSM-RT.csv"]),pd.DataFrame(processed["kmer"]),pd.DataFrame(processed["PC-PseAAC.csv"]),pd.DataFrame(processed["PC-PseAAC-General.csv"]),pd.DataFrame(processed["PDT.csv"]),pd.DataFrame(processed["-DT.csv"]),pd.DataFrame(processed["DP.csv"]),pd.DataFrame(processed["-Top-n-gram.csv"]),pd.DataFrame(processed["-PDT-Profile.csv"]),pd.DataFrame(processed["-CC-PSSM.csv"]),pd.DataFrame(processed["ACC-PSSM.csv"]),pd.DataFrame(processed["-AC-PSSM.csv"]),pd.DataFrame(processed["feature-AC.csv"]),pd.DataFrame(processed["ACC.csv"]),pd.DataFrame(processed["feature-CC.csv"])],axis=1)

    anova = joblib.load('saved_model/anova.pkl')
    data = anova.transform(data)

    model = joblib.load('saved_model/pred_model.pkl')
    y_score = model.predict_proba(data)

    y_score1 = np.array(y_score)[:,0]
    y_score2 = np.array(y_score)[:,1]

    pddata = []

    for i in range(0,len(K_position)):
        pddata1 = []
        pddata1.extend(K_position[i:i+1])
        pddata1.extend(sequence_data[i:i+1])
        pddata1.extend(y_score1[i:i+1])
        pddata1.extend(y_score2[i:i+1])
        pddata.append(pddata1)
    
    result = pd.DataFrame(columns=["K-position","sequence","Non-Succinylation","Succinylation"],index=ls,data=pddata)
    result.to_csv("Output/"+filename+".csv")
    print(result)
    
    deldir = "BioSeq-Analysis\Input_data\Input_data_feature\data"
    filelist = os.listdir(deldir)
    for file in filelist:
        del_file = deldir + '\\' + file
        os.remove(del_file)

def dataprocessing(filepath):
    print ("Loading feature files")
    print (filepath)
    
    dataset1 = pd.read_csv(filepath[0],header=None,low_memory=False)
    print ("Feature processing")

    dataset1 = dataset1.convert_objects(convert_numeric=True)

    dataset1.dropna(inplace = True)

    data = pd.DataFrame(dataset1)
    
    return data

def datadic(filegroup):
    
    method = ["-DT.csv","-PDT-Profile.csv","-Top-n-gram.csv","-PSSM-RT.csv","-PSSM-DT.csv","-CC-PSSM.csv","-AC-PSSM.csv","ACC-PSSM.csv","kmer","feature-AC.csv","ACC.csv","feature-CC.csv","DP.csv","DR.csv","PC-PseAAC.csv","PC-PseAAC-General.csv","PDT.csv","SC-PseAAC.csv","SC-PseAAC-General.csv"]

    test = filegroup["test"]

    file_method = {}
    filepath = []
    test_method = ''
    for methodname in method:
        for i in test:
            if methodname in i:
                test_method = i
                break

        filepath = [test_method]
        
        file_method[methodname] = dataprocessing(filepath)

    return file_method

def process(datadic):

    index = []

    for i in datadic:
        data = datadic[i]
        index.append(i)
        print(i)

        normalizer = joblib.load('saved_model/normalizer_'+i+'.pkl')
        data = normalizer.transform(data)

        lda = joblib.load('saved_model/lda_'+i+'.pkl')
        data = lda.transform(data)
        
        datadic[i] = data

    return datadic

if __name__ == '__main__':
	main(sys.argv)