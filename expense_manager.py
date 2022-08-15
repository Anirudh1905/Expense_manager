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
            return "refund"
        return "UPI"
    elif "REFUND" in x or "UPIRET" in x or "REV-UPI"==x[:7] or "REVERS" in x or "RRR" in x:
        return "refund"
    elif x[:3]=="ATW":
        return 'ATM'
    elif x[:3]=="POS":
        return 'Card'
    elif "INTEREST" in x:
        return 'savings interest'
    elif x[:4]=="PRIN":
        return "FD returns"
    elif x[:4]=="INT.":
        return "FD interest"
    elif x[0].isdigit():
        return 'acc_transfer'
    else:
        return 'others'

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
            
        elif df.iloc[i,-1]=="refund":
            if df.iloc[i,-2]==0.0:
                df.iloc[i,-1]="others"
            user_info.append("others")
            info.append(df.iloc[i,-1])
        
        else:
            user_info.append("others")
            info.append(df.iloc[i,-1])
        
    df["info"]=info
    df["msg"]=user_info
    return df
        
def get_category(df,args_dict):
    f = open(args_dict["data"], "r")
    data = json.load(f)
    tmp=list(data.keys())
    category=[]

    for i in range(len(df)):
        info=str(df.iloc[i,-2])
        msg=str(df.iloc[i,-1])
        
        if msg=="UPI" or msg=="Card" or msg=="others":
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
        else:
            if msg=="UPI" or msg=="Card":
                category.append(msg+" Transfer")
            else:
                category.append("Others")
    #     print(t_data,t_conf,category[i])
    
    df['category']=category
    return df

def plot(x,y,type,args_dict):
    porcent = 100.*y/y.sum()

    patches, texts = plt.pie(y, startangle=90, radius=50)
    labels = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(x, porcent)]

    sort_legend = True
    if sort_legend:
        patches, labels, dummy =  zip(*sorted(zip(patches, labels, y),
                                              key=lambda x: x[2],
                                              reverse=True))

    plt.axis('equal') 
    plt.legend(patches, labels, loc='upper left', bbox_to_anchor=(-1, 1.),
               fontsize=11)

    plt.savefig(args_dict["output_img"]+type+"_"+args_dict["month"]+".png", bbox_inches='tight')
    # plt.show()

def main(args_dict):
    df=pd.read_csv(args_dict["input"])
    df.drop(df.head(1).index,inplace=True)
    df=df.drop(['Value Dat','Chq/Ref Number   ','Closing Balance'],axis=1)
    df.columns=['date','description','debit','credit']
    print("Length: ",len(df))
    
    df['type'] = df['description'].apply(chk)
    print(df['type'].value_counts())
    
    df=get_descriptions(df)
    df=get_category(df,args_dict)
    print(df['category'].value_counts())
    
    df_debit=df[df.credit==0.0]
    df_debit.reset_index(inplace=True,drop=True)
    df_debit.drop(columns=['credit'],inplace=True)
    print(df[df.category=="Others"])
    
    df_credit=df[df.debit==0.0]
    df_credit.reset_index(inplace=True,drop=True)
    df_credit.drop(columns=['debit'],inplace=True)
    
    debit=df_debit.groupby(['category']).agg({'debit':sum}).sort_values(by='debit',ascending=False)
    debit.reset_index(inplace=True)
    plot(debit['category'],debit['debit'],"debit",args_dict)
    print("Debit Plot Stored...")
    
    credit=df_credit.groupby(['category']).agg({'credit':sum}).sort_values(by='credit',ascending=False)
    credit.reset_index(inplace=True)
    plot(credit['category'],credit['credit'],"credit",args_dict)
    print("Credit Plot Stored...")
    
    df.to_csv(args_dict["output_csv"]+args_dict["month"]+"_op.csv",index=False)
    print("CSV File Stored...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help="input csv data")
    parser.add_argument('--data', type=str, help="data dict file")
    parser.add_argument('--month', type=str, help="month name")
    parser.add_argument('--output_img', type=str, help="output image file")
    parser.add_argument('--output_csv', type=str, help="output csv file")
    
    args = parser.parse_args()
    args_dict = args.__dict__
    
    main(args_dict)