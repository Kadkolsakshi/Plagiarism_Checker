from flask import Flask, render_template,request,redirect,url_for
from colorama import Fore, Back, Style
import mysql.connector as connector
import numpy as np
import glob
import os
app = Flask(__name__)

def connectivity():
    try:
        return connector.connect(host="localhost", user="root", password="", database="plagiarism")
    except :
        print("Connection Error")

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1

    matrix = np.zeros((size_x, size_y))

    for x in range(size_x):
        matrix[x, 0] = x  # row aray with elements of x
    for y in range(size_y):
        matrix[0, y] = y  # column array with elements of y
    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x - 1] == seq2[y - 1]:  # if the alphabets at the postion is same
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1
                )

            else:  # if the alphabbets at the position are different
                matrix[x, y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1] + 1,
                    matrix[x, y - 1] + 1
                )

    # returning the levenshtein distance
    return (matrix[size_x - 1, size_y - 1])


@app.route('/')
def home():
    return render_template("Log.html")



@app.route('/login',methods=['GET','POST'])
def login():
    connection = connectivity()
    # try:
    if (connection is not None):
        username = request.form['uname']
        password = request.form['psw']

        sql = f"SELECT * from login where Email = '{username}' and Pass='{password}'"
        cursor = connection.cursor()
        cursor.execute(sql)
        resultset = cursor.fetchone()
        print(resultset)
        if (resultset!=None):
            return redirect(url_for("textchecker"))
        else:
            print("Login Failure")
            return redirect(url_for("home"))

    else:
        print("ERROR IN DATABASE CONNECTION")
        return redirect(url_for("home"))

    # except:
    #     print("MySQLInterfaceError")
    # return render_template("Log.html")

@app.route('/signup')
def signup():
    return render_template("sign.html")

@app.route('/checkfromfile',methods=['GET','POST'])
def checkfromfile():
    plag = 10
    path2 = "source.txt"
    path3 = "target.txt"

    with open(path2, 'r') as file:
        data = file.read().replace('\n', '')
        str1 = data.replace(' ', '')

    with open(path3, 'r') as file:
        data = file.read().replace('\n', '')
        str2 = data.replace(' ', '')

    if (len(str1) > len(str2)):
        length = len(str1)

    else:
        length = len(str2)

    n = 100 - round((levenshtein(str1, str2) / length) * 100, 2)

    message = ""
    if (n > plag):
        # print("\nFor the data", source, "and", target, n, "% similarity")
        message = f"<center><h1>For the data in file </h1> <h2> Has </h2> <b> {n}% similarity</b></h1></center>"
    else:
        message = f"Similarities are below the given level"
    return message


@app.route('/check',methods=['GET','POST'])
def check():
    source = request.form['source']
    target = request.form['target']
    plag = 10
    if (len(source) > len(target)):
        length = len(source)

    else:
        length = len(target)

    n = 100 - round((levenshtein(source, target) / length) * 100, 2)
    message = ""
    if (n > plag):
        # print("\nFor the data", source, "and", target, n, "% similarity")

        message = f"<center><h1>For the data <h2>Text 1 and Text 2</h2><b> {n}% similarity</b></center></h1>"
        message.rjust(20,' ')
    else:
        message = f"<center><b>Choose File</center></b>"
    return message

@app.route('/source_upload', methods=['POST'])
def sourceupload():
    if request.method == 'POST':
        f = request.files['sourcefile']
        f.save("source.txt")
        return render_template("file.html")

@app.route('/target_upload', methods=['POST'])
def targetupload():
    if request.method == 'POST':
        f = request.files['targetfile']
        f.save("target.txt")
        return render_template("file.html")

@app.route('/text-checker')
def textchecker():
    return render_template("admin.html")

@app.route('/log-out')
def logout():
    return render_template("Log.html")

@app.route('/file-checker')
def filechecker():
    return render_template("file.html")


if __name__ =='__main__':
    app.run(debug = True)