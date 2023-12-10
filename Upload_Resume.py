import tempfile
import joblib
import pickle
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
import mysql.connector
from nltk.corpus import stopwords
from csv import DictWriter
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

#Cleaning the Resume uploaded
def clean(df):
    df['Resume'] = df['Resume'].apply(lambda x:x.lower())
    ps = list(";?.:!,")
    for p in ps:   
        df['Resume'] = df['Resume'].str.replace(p, '')
    df['Resume'] = df['Resume'].str.replace("    ", " ")
    df['Resume'] = df['Resume'].str.replace('"', '')
    df['Resume'] = df['Resume'].apply(lambda x: x.replace('\t', ' '))
    df['Resume'] = df['Resume'].str.replace("'s", "")
    df['Resume'] = df['Resume'].apply(lambda x: x.replace('\n', ' '))
    sw = list(stopwords.words('english'))
    for s in sw:
        rs = r"\b" + s + r"\b"
        df['Resume'] = df['Resume'].str.replace(rs, '')
    return df


mydb = mysql.connector.connect(user='root', password='password',
                                                host='127.0.0.1', database='resumes',
                                                auth_plugin='mysql_native_password')
cur = mydb.cursor()
query0 = """SELECT POSITION FROM HR"""
cur.execute(query0)
positin1 = cur.fetchall()


mydb.commit()


position1 = list(positin1[0])
pos= "HR's requirement\: " + position1[0].upper()
query2=f"""Select skills from skills where LOWER(position)='{position1[0].lower()}'"""
cur.execute(query2)

skills = cur.fetchall()
mydb.commit()
ski=list(skills[0])
skill="Main keywords\:\n "+ ski[0].upper()


#UI design
st.set_page_config(page_title="Upload Resumé")

st.title("AI Resumé Screening")
st.header(pos)
st.header(skill)
st.subheader("Please Upload your Resumé in the dropbox")

st.write('Accepted formats: pdf, docx, txt')

final=pd.DataFrame(columns=['Email Id','Name','Mobile No','Resume'])
with st.form("Registration Form"):   
    email = st.text_input(label = 'Email Address', placeholder = "Please enter your email address")
    fullName = st.text_input(label = 'Full Name', placeholder="Please enter your full name") 
    mobile = st.text_input(label='Mobile', placeholder="Please enter subject your Mobile No.")
    location=st.text_input(label='Location',placeholder='Please enter location')
    uploaded_file = st.file_uploader(label='Resumé',type=['pdf','docx','txt'],accept_multiple_files=False)
    submitted = st.form_submit_button("Submit")
if submitted:
    if uploaded_file:
            content=''
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    fp = Path(tmp_file.name)
                    fp.write_bytes(uploaded_file.getvalue())
                    if uploaded_file.type=='text/plain':
                        bytes_data = uploaded_file.getvalue()
                        content=str(bytes_data)
                    if uploaded_file.type=='application/pdf':
                        import PyPDF2
                        pdffileobj=open(tmp_file.name,'rb')
                        pdfreader=PyPDF2.PdfReader(pdffileobj)
                        x=len(pdfreader.pages)
                        for i in range(x):
                            pageobj=pdfreader.pages[i]
                            text=pageobj.extract_text()
                            content+=text
                    if uploaded_file.type=='application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        import docx2txt
                        content=docx2txt.process(tmp_file.name)
            data={'Resume':[content]}
            
            frame=pd.DataFrame(data)
            frame = clean(frame)
            
            #scoring
            a = ski[0].split(',')
            score=0
            for i in a:
                if(i.lower() in content.lower()):
                    score=score+1
            length=ski[0].count(',')
            score=score*100/(length+1)                 
            
            
            #Vectorizing and passing into pre trained model
            
            cv = pickle.load(open('cv.pickle','rb'))
            cv1 = TfidfVectorizer(max_features=20000)
            X = cv1.fit_transform(frame['Resume'])
            first_vector_tfidfvectorizer=X
            # place tf-idf values in a pandas data frame 
            df = pd.DataFrame(first_vector_tfidfvectorizer.T.todense(), index=cv1.get_feature_names_out(), columns=["tfidf"])
            model = joblib.load('RF.joblib')
            
            import numpy as np
            l1=cv.get_feature_names_out()
            l2=cv1.get_feature_names_out()
            df1={}
            for x in l1:
                if x in l2:
                    df1[x]=df.loc[x,'tfidf']
                else:
                    df1[x]=0
            val=[]
            df2=pd.DataFrame([df1.values()],columns=df1.keys())
            import scipy
            from scipy.sparse import csr_matrix
            csr_matrix = csr_matrix(df2.astype(pd.SparseDtype("float64",0)).sparse.to_coo())
            
            
            #Prediction and result Shown
            pred=model.predict(csr_matrix)
            dict_category={0: 'ACCOUNTANT', 1: 'ADVOCATE', 2: 'AGRICULTURE', 3: 'APPAREL', 4: 'ARTS', 5: 'AUTOMOBILE', 6: 'AVIATION', 7: 'Advocate', 8: 'Arts', 9: 'Automation Testing', 10: 'BANKING', 11: 'BPO', 12: 'BUSINESS-DEVELOPMENT', 13: 'Blockchain', 14: 'Business Analyst', 15: 'CHEF', 16: 'CONSTRUCTION', 17: 'CONSULTANT', 18: 'Civil Engineer', 19: 'DESIGNER', 20: 'DIGITAL-MEDIA', 21: 'Data Science', 22: 'Database', 23: 'DevOps Engineer', 24: 'DotNet Developer', 25: 'ENGINEERING', 26: 'ETL Developer', 27: 'Electrical Engineering', 28: 'FINANCE', 29: 'FITNESS', 30: 'HEALTHCARE', 31: 'HR', 32: 'Hadoop', 33: 'Health and fitness', 34: 'INFORMATION-TECHNOLOGY', 35: 'Java Developer', 36: 'Mechanical Engineer', 37: 'Network Security Engineer', 38: 'Operations Manager', 39: 'PMO', 40: 'PUBLIC-RELATIONS', 41: 'Python Developer', 42: 'SALES', 43: 'SAP Developer', 44: 'Sales', 45: 'TEACHER', 46: 'Testing', 47: 'Web Designing'}
            print(pred)
            pred2=f'The resume is fit for {dict_category[pred[0]].upper()} category..'
            st.header(pred2)
            pred3=max(list(pred))
            prediction_category = dict_category[pred[0]].upper()

        #If category matches the requirement    
            if dict_category[pred[0]].lower()==position1[0].lower():
                    file_path = tmp_file.name
                    
                #Storing it in database (MYSQL)    
                    
                    def convertToBinaryFile(filename):
                        with open(filename, 'rb') as file:
                            binarydata = file.read()
                        return binarydata


                    def convertBinaryToFile(binarydata, filename):
                        with open(filename, 'wb') as file:
                            file.write(binarydata)


                    
                    query = """INSERT INTO employees (Name,Email,Resume,score,location,category) value (%s,%s,%s,%s,%s,%s)"""
                    convertfile = convertToBinaryFile(file_path)
                    value = (fullName,email, convertfile,score,location,prediction_category.upper())
                    cur.execute(query,value)
                    mydb.commit()


