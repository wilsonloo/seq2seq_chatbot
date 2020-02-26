import re  
import sys 
import pickle
from tqdm import tqdm
from word_sequence import WordSequence

def make_split(line):
    if re.match(r'.*([，。…？！\.,!? ])$', ''.join(line)):
        return []
    return ['，']


def good_line(line):
    if len(re.findall(r'[a-zA-Z0-9]',''.join(line)))>2:
        return False
    return True 

def regular(sen):
    sen=re.sub(r'\.{3,100}','…',sen)
    sen =re.sub(r'…{2,100}','…',sen)
    sen =re.sub(r'[,]{1,100}','，',sen)
    sen=re.sub(r'[\.]{1,100}','。',sen)
    sen=re.sub(r'[\?]{1,100}','？',sen)
    sen=re.sub(r'[!]{1,100}','！',sen)

    return sen

def checkLimit(x, y, limit, x_limit, y_limit):
    return len(x) < limit and len(y) < limit and len(y)>=y_limit and len(x)>=x_limit

def main(limit=20, x_limit=3,y_limit=6):
    print("extract lines")

    fp = open("./data/dgk_shooter_min.conv",'r',encoding='utf-8')
    groups =[]
    group=[]

    for line in tqdm(fp):
        if line.startswith('M '):
            line = line.replace('\n','')
            if '/' in line:
                line = line[2:].split('/')
            else:
                line = list(line[2:])
            line = line[:-1] #

            group.append(list(regular(''.join(line))))
        else:
            lsat_line=None
            if group:
                groups.append(group)
                group=[]
    print('extract group')


    x_data=[]
    y_data=[]
    
    for group in tqdm(groups):
        for i,line in enumerate(group):
            last_line=None
            if i>0:
                last_line = group[i-1]
                if not good_line(last_line):
                    lsat_line=None
            
            next_line = None
            if i <len(group) -1 :
                next_line= group[i+1]
                if not good_line(next_line):
                    next_line=None
            next_next_line = None
            if i<len(group)-2:
                next_next_line=group[i+2]
                if not good_line(next_next_line):
                    next_next_line=None
            
            if next_line:
                if checkLimit(line, next_line, limit, x_limit, y_limit):
                    x_data.append(line)
                    y_data.append(next_line)
            
            if last_line and next_line:
                a = last_line + make_split(last_line) + line
                b = next_line
                if checkLimit(a, b, limit, x_limit, y_limit):
                    x_data.append(a)
                    y_data.append(b)
            
            if next_line and next_next_line:
                a = line
                b = next_line + make_split(next_line) + next_next_line
                if checkLimit(a, b, limit, x_limit, y_limit):
                    x_data.append(a)
                    y_data.append(b)
    
    x_len = len(x_data)
    y_len = len(y_data)
    print(x_len, y_len)

    for ask,answer in zip(x_data[:20],y_data[:20]):
        print(''.join(ask))
        print(''.join(answer))
        print('-'*20)

    """
    print("listing zip...")
    data = list(zip(x_data,y_data))

    print("fixing data...")
    data = [
        (x,y)
        for x,y in data
        if len(x) <limit \
        and len(y) < limit \
        and len(y)>=y_limit \
        and len(x)>=x_limit

    ]

    print("rezipping data...")
    x_data,y_data=zip(*data)
    """

    """
    print('fit word_sequence...')
    for k in tqdm(range(x_len-1, -1, -1)):
        x = x_data[k]
        y = y_data[k]
        xLen = len(x)
        yLen = len(y)
        if not (xLen < limit and yLen < limit and yLen >= y_limit and xLen >= x_limit):
            old = id(x_data)
            x_data.remove(x)
            y_data.remove(y)
            print("elem removed, x_data address delta:", old, id(x_data))
    """

    print('fit word_sequence..done')

    ws_input = WordSequence()
    ws_input.fit(x_data + y_data)

    print('dump')

    pickle.dump(
        (x_data,y_data),
        open('./data/chatbot.pkl','wb')
    ) 
    pickle.dump(ws_input,open('./data/ws.pkl','wb'))
    print('done')




if __name__ == '__main__':
    main()
        
