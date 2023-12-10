import streamlit as st
import mysql.connector
import pandas as pd
st.title("HR's Requirement")
with st.form("HR form"):
    position = st.text_input(label = "Position", placeholder = "Please enter the HR's required position")
    exp = st.text_input(label = "Minimum Experience (in years)", placeholder="Please enter the minimum experience required (in years)")
    submitted = st.form_submit_button("Submit")
mydb = mysql.connector.connect(user='root', password='password',
                                                host='127.0.0.1', database='resumes',
                                                auth_plugin='mysql_native_password')
cur = mydb.cursor()   
if submitted:
    
    position=position.lower()
    exp=int(exp)
    
    
    query0 = """TRUNCATE TABLE HR"""
    cur.execute(query0)
    mydb.commit()
    query = """INSERT INTO HR (Position,Experience) value (%s,%s)"""
    value = (position,exp)
    cur.execute(query,value)
    mydb.commit()
show = st.button("Show Resumes")

if show:
    query1 = """SELECT NAME,EMAIL,LOCATION,SCORE,RESUME FROM EMPLOYEES ORDER BY SCORE DESC"""
    cur.execute(query1)
    resumes = cur.fetchall()

    colms = st.columns((1, 2, 2, 1))
    fields = ["Name", 'Email', 'Location', "Resume"]
    for col, field_name in zip(colms, fields):
        # header
        col.write(field_name)
    c=0
    for row in resumes:
        col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1))
        col1.write(row[0])  #name
        col2.write(row[1])  # email
        col3.write(row[2])  # location
        # col4.write(row[3])   # score
        disable_status = "X"  # flexible type of button
        # button_type = "Show" if disable_status else "Seen"
        button_phold = col5.empty()  # create a placeholder
        # do_action = button_phold.button(button_type, key=c)
        do_action = button_phold.button("Show", key=c, type="primary")
        if do_action:
            c+=1