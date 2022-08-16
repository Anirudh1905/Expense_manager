from calendar import month
import sys
import os
import json
import argparse
import pandas as pd
import numpy as np
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def chk(x):
    if x[:3]=="UPI":
        if "REFUND" in x or "UPIRET" in x or "REV-UPI"==x[:7] or "REVERS" in x or "RRR" in x:
            return "Refund"
        return "UPI"
    elif "REFUND" in x or "UPIRET" in x or "REV-UPI"==x[:7] or "REVERS" in x or "RRR" in x:
        return "Refund"
    elif x[:3]=="ATW":
        return 'ATM'
    elif x[:3]=="POS":
        return 'Card'
    elif "INTEREST" in x:
        return 'Savings Interest'
    elif x[:4]=="PRIN":
        return "FD returns"
    elif x[:4]=="INT.":
        return "FD interest"
    elif x[0].isdigit():
        return 'Account Transfer'
    else:
        return 'Others'

def get_descriptions(df):
    user_info=[]
    info=[]
    for i in range(len(df)):
        if df.iloc[i,-1]=="UPI":
            tmp=str(df.iloc[i,1]).rstrip(" ").split('-')
            msg=tmp[-1]
            if msg[:3]=="UPI":
                msg="UPI"
            user_info.append(msg)
            info.append(tmp[1])
            
        elif df.iloc[i,-1]=="Card":
            tmp=str(df.iloc[i,1]).rstrip(" ").split(' ')
            tmp=tmp[2:]
            msg=" "
            msg=msg.join(tmp)
            msg=msg.rstrip(" ")
            user_info.append("Card")
            info.append(msg)
            
        elif df.iloc[i,-1]=="Refund":
            if df.iloc[i,-2]==0.0:
                df.iloc[i,-1]="Others"
            user_info.append("Others")
            info.append(df.iloc[i,-1])
        
        else:
            user_info.append("Others")
            info.append(df.iloc[i,-1])
        
    df["info"]=info
    df["msg"]=user_info
    return df
        
def get_category(df,args_dict):
    f = open(args_dict["data"], "r")
    data = json.load(f)
    tmp=list(data.keys())
    category=[]
    sub_category=[]

    for i in range(len(df)):
        info=str(df.iloc[i,-2])
        msg=str(df.iloc[i,-1])
        
        if msg=="UPI" or msg=="Card" or msg=="Others":
            t1=process.extract(info,tmp) 
            t_key,t_conf,t_data=t1[0][0],t1[0][1],info   
        else:
            t1=process.extract(info,tmp)
            t2=process.extract(msg,tmp)
            t1_key,t1_conf=t1[0][0],t1[0][1]
            t2_key,t2_conf=t2[0][0],t2[0][1]
            t_key,t_conf,t_data=[t1_key,t1_conf,info] if t1_conf>t2_conf else [t2_key,t2_conf,msg]
            
        if t_conf>60:
            category.append(data[t_key])
            sub_category.append(t_key)
        else:
            if msg=="UPI" or msg=="Card":
                category.append(msg+" Transfer")
                sub_category.append(msg+" Transfer")
            else:
                category.append("Others")
                sub_category.append("Others")
    #     print(t_data,t_conf,category[i])
    
    df['sub_category']=sub_category
    df['category']=category
    return df

def plot(x,y,type,filepath):
    percent = 100.*y/y.sum()
    cdict = dict(zip(x, plt.cm.tab10.colors if len(x)<=10 else plt.cm.tab20.colors)) 
    
    patches, texts = plt.pie(y, startangle=90, radius=50, colors=None if len(x)>20 else [cdict[v] for v in x])

    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x, percent)]

    sort_legend = True
    if sort_legend:
        patches, labels, dummy =  zip(*sorted(zip(patches, labels, y),
                                              key=lambda x: x[2],
                                              reverse=True))

    plt.axis('equal') 
    plt.title(type+" Plot")
    plt.legend(patches, labels, loc='upper left', bbox_to_anchor=(-1, 1.),
               fontsize=11)

    plt.savefig(filepath+type+".png", bbox_inches='tight')
    # plt.show()

def main(args_dict):
    
    filepath=args_dict["output_path"]
    if not os.path.isdir(filepath):
        os.mkdir(filepath)
        print("Output directory created")
    if filepath[-1]!="/":
        filepath=filepath+"/"

    df=pd.read_csv(args_dict["input"])
    df.drop(df.head(1).index,inplace=True)
    df=df.drop(['Value Dat','Chq/Ref Number   ','Closing Balance'],axis=1)
    df.columns=['date','description','debit','credit']
    print("Length: ",len(df))
    
    df['type'] = df['description'].apply(chk)
    # print(df['type'].value_counts())
    
    df=get_descriptions(df)
    df=get_category(df,args_dict)
    # print(df['sub_category'].value_counts())
    
    df_debit=df[df.credit==0.0]
    df_debit.reset_index(inplace=True,drop=True)
    df_debit.drop(columns=['credit'],inplace=True)
    # print(df[df.category=="Others"])
    
    df_credit=df[df.debit==0.0]
    df_credit.reset_index(inplace=True,drop=True)
    df_credit.drop(columns=['debit'],inplace=True)
    
    if args_dict["type"]:
        debit=df_debit.groupby(['type']).agg({'debit':sum}).sort_values(by='debit',ascending=False)
        debit.reset_index(inplace=True)
        plot(debit['type'],debit['debit'],args_dict["month"].capitalize()+" Debit Transactions",filepath)
        print("Debit Transactions Plot Stored...")
        
        credit=df_credit.groupby(['type']).agg({'credit':sum}).sort_values(by='credit',ascending=False)
        credit.reset_index(inplace=True)
        plot(credit['type'],credit['credit'],args_dict["month"].capitalize()+" Credit Transactions",filepath)
        print("Credit Transactions Plot Stored...")
        
    debit=df_debit.groupby(['category']).agg({'debit':sum}).sort_values(by='debit',ascending=False)
    debit.reset_index(inplace=True)
    plot(debit['category'],debit['debit'],args_dict["month"].capitalize()+" Debit",filepath)
    print("Debit Plot Stored...")
    
    if args_dict["sub_category"]:
        debit=df_debit.groupby(['sub_category']).agg({'debit':sum}).sort_values(by='debit',ascending=False)
        debit.reset_index(inplace=True)
        plot(debit['sub_category'],debit['debit'],args_dict["month"].capitalize()+" Sub Category Debit",filepath)
        print("Sub category Debit Plot Stored...")
        
    credit=df_credit.groupby(['category']).agg({'credit':sum}).sort_values(by='credit',ascending=False)
    credit.reset_index(inplace=True)
    plot(credit['category'],credit['credit'],args_dict["month"].capitalize()+" Credit",filepath)
    print("Credit Plot Stored...")
    
    df_sum=df.sum(axis=0,numeric_only = True).to_frame(name='Sum')
    df_sum.index=["Debit","Credit"]
    df_sum.reset_index(inplace=True)
    plot(df_sum['index'],df_sum['Sum'],args_dict["month"].capitalize()+" Credit vs Debit",filepath)
    print("Credit vs Debit Plot Stored...")
    
    df.to_csv(filepath+args_dict["month"]+"_op.csv",index=False)
    print("CSV File Stored...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help="input csv data")
    parser.add_argument('--data', type=str, help="data dict file")
    parser.add_argument('--month', type=str, help="month name")
    parser.add_argument('--output_path', type=str, help="output path")
    parser.add_argument('--sub_category', type=bool, nargs='?', const=False, help="shows sub-category")
    parser.add_argument('--type', type=bool, nargs='?', const=False, help="shows type of transaction")
    
    args = parser.parse_args()
    args_dict = args.__dict__
    
    main(args_dict)