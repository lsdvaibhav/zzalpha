#------flask libraries code-------------------
import os
import json
import requests
from flask import Flask,render_template,request,jsonify,make_response , send_file,redirect,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import glob
#------flask libraries code end----------------

#-------scraper libraries code ----------------
import pandas as pd
import numpy as np
import re
import os
import warnings
warnings.filterwarnings('ignore')
import json
import csv
import io
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import time
#------scraper libraries code end-------------

#------download pdf libraries code------------
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import ImageFont, ImageDraw, Image
import img2pdf
import PyPDF2
import os
import urllib
from urllib.request import urlopen
import random
import textwrap
#---------download pdf libraries code end------------


#-----flask app code-----------

app = Flask(__name__)
#-----flask app code end-------

#-----app database code-------------

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False 
db=SQLAlchemy(app)
#-----app database code end---------


#----routing landing page--------------------------------
@app.route('/')
def home():
    return render_template('index.html')
    
#----routing pdfViewer code----------------------------------
@app.route('/pdfViewer')
def pdfviewer():
    return render_template('pdf.html')
    #return send_file("static\downloads\Consolidated.pdf",as_attachment=True)  
#----routing pdfViewer code----------------------------------
@app.route('/downloadpdf')
def downloadpdf():
    return send_file("static\downloads\Consolidated.pdf",as_attachment=True)      
    
#----routing file clear code----------------------------------
@app.route('/clear', methods=['GET', 'POST'])
def clear():
    os.unlink("static\downloads\Consolidated.pdf")
    print('Consolidated removed')
    return redirect("/")
   

#----routing scrap code----------------------------------
@app.route('/scrap', methods=['GET', 'POST'])
def scrapfirst():
    if request.method == "POST":
        try:
            url = request.form['scrapURLinput']
            catlist = scrap(url)
            responseDF = showItems(catlist)
            res = make_response(jsonify({"Cat": catlist , "data" : responseDF}),200)
        except:
            error =["not working" , " not available"]
            res = make_response(jsonify({"Cat": error, "data": error} , 200))
    return res

#----routing filter code----------------------------------
@app.route('/filter', methods=['GET', 'POST'])
def filter():
    if request.method == "POST":
        try:    
            catlist = []
            req = request.form['CatList']
            catlist = req.split(",")
            responseDF = showItems(catlist)
            res = make_response(jsonify({"Cat": catlist , "data" : responseDF}),200)
        except:
            error =["not working" , " not available"]
            res = make_response(jsonify({"Cat": error, "data": error} , 200))
    
    return res
#----routing download code----------------------------------

@app.route('/downloadPDF', methods=['GET', 'POST'])
def Download_PDF():
    if request.method=="POST":
        try:
            req = request.form['itemList']
            itemList = req.split(",")
            data = pd.read_csv('frendy_grocery.csv')
            data.rename( columns={'Unnamed: 0':'Index'}, inplace=True )
            testDF = data[data['Index'].isin(itemList)]
            downloadPDF(testDF)
            message = "Please check the PDF"
            alert = "success"
        except:
            print("not working")
            message= "not working"
            alert = "danger"
    res = make_response(jsonify({"message": message , "alert" : alert}),200 )
    
    return res

#----routing download code end------------------------------


#---Scraping url code---------------------------------------
def scrap(url):
    
    df = pd.DataFrame(columns = ['Website','City','img','img_url','Category','Item','mrp','discount','item_url','Quantity','Price'])
    qty=[]
    price = []
    name=[]
    cat=[]
    img_url=[]
    img=[]
    disc=[]
    mrp=[]
    prod_url=[]
    for k in range(0,6):
        headers = {
        'authority': 'catalog.service.frendy.in:3000',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://shop.frendy.in',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://shop.frendy.in/',
        'accept-language': 'en-US,en;q=0.9',
        }

        #d = '{"categories":"64","ipp":"20","paginator":"1"}'
        #data = '{"categories":"64","ipp":"20","paginator":'+ "{}".format(i)+'}'

        d = '{"categories":"64","ipp":"20","paginator":'+ "{}".format(k)+'}'

        response = requests.post('https://catalog.service.frendy.in:3000/api/product/list', headers=headers, data=d)
        data = json.loads(response.text)
        data2 = data['productDefinitions']
        url = 'https://shop.frendy.in/#/product-detail?productId='

        for i in range(len(data['productDefinitions'])):
            for j in range(len(data2[i]['Variations'])):
                try:
                    qty.append(data2[i]['Variations'][j]['Attributes'][0]['ProductAttributeValue']['value']) # for this nan have to be filled using regex
                except:
                    qty.append(np.nan)
                try:
                    price.append(data2[i]['Variations'][j]['ProductPrices'][0]['frendyPrice'])
                except:
                    price.append(np.nan)
                              #i              #j
                try:
                    name.append(data2[i]['identifier'])
                except:
                    name.append(np.nan)
                try:    
                    cat.append(data2[i]['Categories'][0]['identifier'])
                except:
                    cat.append(np.nan)
                try:
                    img_url.append(data2[i]['imageAbsolutePath'])
                except:
                    img_url.append(np.nan)
                try:
                    img.append(data2[i]['image'])
                except:
                    img.append(np.nan)
                try:
                    disc.append(data2[i]['Variations'][j]['ProductPrices'][0]['discount'])
                except:
                    disc.append(np.nan)
                try:
                    mrp.append(data2[i]['Variations'][j]['ProductPrices'][0]['mrp'])
                except:
                    mrp.append(np.nan)
                try:
                    prod_url.append(url+str(data2[i]['id']))
                except:
                    prod_url.append(np.nan)

                
                
    df['img'] = pd.Series(img)
    df['img_url'] = pd.Series(img_url)
    df['Category'] = pd.Series(cat)
    df['Item'] =pd.Series(name)
    df['mrp'] = pd.Series(mrp)
    df['discount'] =pd.Series(disc)
    df['item_url'] = pd.Series(prod_url)
    df['Quantity'] = pd.Series(qty)
    df['Price'] = pd.Series(price)
    df['Website'] = 'Frendy'
    df['City'] = 'Ahmedabad'
    df['Item'] = df['Item'].apply(lambda x: re.sub('[0-9]{1,3}[' '] [a-zA-Z]{1,5}','',x))
    df['Quantity']=df.Quantity.apply(lambda x: str(x).replace(' ','') )
    
    df.reset_index(inplace=True)
    df1 = df["Category"].unique().tolist()
    df.drop('index',axis=1,inplace=True)
    df.drop_duplicates(['Item','Price'],inplace=True)
    df.to_csv('frendy_grocery.csv')
    return df1

#---Scraping url code end-----------------------------------

#---download pdf code / final grid  code--------------------------------


def downloadPDF(data):
    
    data = data
    
    for cat in data['Category'].unique():
        dataframe = data[data['Category']==cat]
        pages = []
        grid_list = []
        links = []

        ## ------ Best Discount Item ------------
        per_disc = round((dataframe['discount']/(dataframe['mrp'].astype(float)))*100,1)
        if len(dataframe)%2 == 1 and len(dataframe) !=1:
            print("processing best discount Item of category = ",cat)
            max_disc = dataframe[per_disc == max(per_disc)]
            create_jpg(max_disc, 1, cat, pages, grid_list, links)
            draw = ImageDraw.Draw(pages[0])
            font2 = ImageFont.truetype("static/fonts/Roboto-BoldItalic.ttf", 100)
            draw.text((228,53), 'Best Offer' , font=font2, fill=(252,3,3))
            draw.text((225,50), 'Best Offer' , font=font2, fill=(255,255,255))
            dataframe = dataframe.drop(max_disc.index[0])


        main(dataframe, cat, pages, grid_list, links)

        ## ------Create PDF----------------
        pages[0].save("static/pdfs/"+cat+" final.pdf", save_all = True, append_images = pages[1:])
        print("PDF Saved.")

        ## ------------Adding Links to final.pdf------------
        pdfs_out_cat = open("static/pdfs/"+cat+" final.pdf", 'rb')
        pdf_input = PyPDF2.PdfFileReader(pdfs_out_cat)
        pdf_output = open("static/pdfs/"+cat+" linked.pdf", 'wb')
        pdf_result = PyPDF2.PdfFileWriter()

        rectangles = []
        for i in All_coordinates:
            rectangle = []
            for j in i:
                coordinates = [j[2],1280-j[1],j[3],1280-j[0]]
                rectangle.append(coordinates.copy())
            rectangles.append(rectangle.copy())
            
        for pagenum in range(pdf_input.getNumPages()):
            pdf_page = pdf_input.getPage(pagenum)
            pdf_result.addPage(pdf_page)

        j = 0
        for pagenum in range(pdf_input.getNumPages()):
            grid_no = grid_list[pagenum]
            for rect in rectangles[grid_no-1]:
                pdf_result.addURI(pagenum, links[j], rect, border = None)
                j += 1
        pdf_result.write(pdf_output)

        print("Links Added.")
        pdfs_out_cat.close()
        pdf_output.close()


    pdfs = os.listdir('static/pdfs')
    pdfs = popper(pdfs)
    pdf_output = open("static/downloads/Consolidated.pdf", 'wb')
    pdf_result = PyPDF2.PdfFileWriter()


    file_handles = []
    j = 0
    for i in pdfs:
        file_handles.append(open("static/pdfs/"+i, 'rb'))
        pdf_input = PyPDF2.PdfFileReader(file_handles[j])
        for pagenum in range(pdf_input.getNumPages()):
            pdf_page = pdf_input.getPage(pagenum)
            pdf_result.addPage(pdf_page)
        j = j+1

    pdf_result.write(pdf_output)
    for fh in file_handles:
        fh.close()
    
    pdf_output.close()
    print("PDFs Consolidated.")


##--------------- Delete PDFs ---------------
    
    files=glob.glob('static/pdfs/' + '*.pdf')
    for filename in files:
    	os.unlink(filename)
    	print('pdf removed')
        

def popper(l):
    for i in range(len(l)):
        if (l[i][-5:] == 'l.pdf'):
            
            l.pop(i)
        if (i == len(l)-1):
            return l
    popper(l)


def main(dataframe, category, pages, grid_list, links):
    data = dataframe
    category = category
    if len(data)>9: 
        if len(data) < 18:
            print(f"processing {len(data)//2} Items of category = {category}")
            create_jpg(data[:len(data)//2], len(data)//2, category, pages, grid_list, links)
            main(dataframe[len(data)//2:], category, pages, grid_list, links)
            
        else:    
            print("processing 9 Items of category = ",category)    
            create_jpg(data[:9], 9, category, pages, grid_list, links)
            main(dataframe[9:], category, pages, grid_list, links)
        
    else:
        print(f"processing {len(data)} Items of category = {category}")
        create_jpg(data[:len(data)], len(data), category, pages, grid_list, links)

def url_to_image(url):
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def resize_image(img, i):
    img = cv2.resize(img, (i, i))
    return img

def split_text(text):
    t1 = text[:28]
    i = 28
    for char in t1[::-1]:
        if char == " ":
            t1 = text[:i]
            t2 = text[i:]
            break
        i = i-1
    return( t1.strip(), t2.strip())


def design_image(img, name, off, r_s):
    product_name = name.strip()
    discount_percent = str(off) + '%'
    radius_discount = int(0.25*r_s)
    bottom = int(0.095*r_s)+5

    img = resize_image(img, r_s)
    img = cv2.circle(img, (0,0), radius_discount, (3,3,252), -1, cv2.LINE_AA)
    img[r_s-bottom+5:r_s,:, :] = (222, 255, 250) 
    
    point_off = (r_s*0.032, r_s*0.11)
    point_product_name = (int(0.08*r_s),int(r_s*.88))
    point_discount_percent = ((r_s*0.024, r_s*0.012))
    
    #font_hb_discount_percent = ImageFont.truetype("hb.ttf", int(r_s*0.094))
    font =  ImageFont.truetype("static/fonts/OpenSans-Bold.ttf", int(r_s*0.07))
    font1 =  ImageFont.truetype("static/fonts/RobotoCondensed-BoldItalic.ttf", int(r_s*0.094))
    
    x_font, y_font = font.getsize(product_name)
    x = (r_s - x_font-20)/2
    point_product_name = (int(x+10),int(r_s*.90))
    if x_font > int(r_s*0.85) and x_font<=int(r_s*1.0):
        font = ImageFont.truetype("static/fonts/OpenSans-Bold.ttf", int(r_s*0.063))
        x_font, y_font = font.getsize(product_name)
        x = (r_s - x_font-20)/2
        point_product_name = (int(x+10),int(r_s*.90))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
    elif x_font > int(r_s*1.0):
        font = ImageFont.truetype("static/fonts/OpenSans-Bold.ttf", int(r_s*0.067))
        img[r_s-bottom-10:r_s,:, :] = (222, 255, 250) 
        product_name1, product_name = split_text(product_name)
        x_font, y_font = font.getsize(product_name1)
        x = (r_s - x_font-0)/2
        point_product_name1 = (int(x),int(r_s*.83))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text(point_product_name1, product_name1, font=font, fill=(0, 0, 0))
        x_font, y_font = font.getsize(product_name)
        x = (r_s - x_font-0)/2
        point_product_name = (int(x),int(r_s*.90))
        
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
    
    draw.text(point_product_name, product_name, font=font, fill=(0, 0, 0))
    draw.text(point_off, 'off', font=font1, fill=(255, 255, 255))
    draw.text(point_discount_percent, discount_percent, font=font1, fill=(255, 255, 255))
   
    img = np.array(img_pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

  
All_coordinates = [[(175,675,205,705)],
     [(257,557,127,427),(257,557,484,784)],
     [(43,343,47,347),(43,343,560,860),(608,908,301,601)],
     [(80,430,35,385),(80,430,518,868),(735,1085,35,385),(735,1085,518,868)],
     [(80,330,54,304),(78,328,593,843),(472,722,333,583),(898,1148,52,302),(898,1148,593,843)],
     [(97,318,63,284),(97,318,350,571),(97,318,621, 842),(547,768,63,284),(547,768,350,571), (547,768,621,842)],
     [(65,315,42,292),(65,315,618, 868),(483,733,41,291),(483,733,618,868),(898,1148,42,292),(897,1147,330,580),(897,1147,618,868)],
     [(138,338,52,252),(139,339,354,554),(139,339,656, 856),(490,690,52,252),(490,690,656,856),(839,1039,50,250),(839,1039,355,555),(839,1039,655,855)],
     [(65,285,68,288),(65,285,338,558),(65,285,603, 823),(440,660,68,288),(440,660,338,558), (440,660,603,823),(957,1177,68,288),(957,1177,338,558), (957,1177,603,823)],
     [(29,229,51,251),(31,231,354,554),(31,231,639,839),(335,535,51,251),(335,535,639,839),(663,863,51,251),(666,866,641,841),(975,1175,51,251),(977,1177,354,554),(977,1177,641,841)],
     [(29,229,51,251),(31,231,354,554),(31,231,639,839),(335,535,51,251),(335,535,354,554),(335,535,639,839),(663,863,51,251),(666,866,641,841),(975,1175,51,251),(977,1177,354,554),(977,1177,641,841)],
     [(31,204,157,330),(31,204,368,541),(31,204,577, 750),(310,483,157,330),(310,483,368,541),(310,483,577, 750),(586,759,157,330),(586,759,368,541),(586,759,577, 750),(861,1034,157,330),(861,1034,368,541),(861,1034,577, 750)]]


attrs = {'r_s' : [500,300,300,350,250,221,250,200,220,200,200,173],
        'font_size' : [74,40,43,44,30,26,35,28,26,24,24,22],
        'font1_size' : [38,28,25,30,24,20,22,17,20,18,18,18],
        'font2_size' : [85,85,54,60,60,60,60,54,60,60,54,60],
        'text_font_loc' : [(215,185),(65,38),(70,24),(70,25),(60,13),(50,23),(57,10),(50,13),(50,15),(50,22),(50,22),(38,10)],
        'text_font1_loc' : [(295,308),(210,77),(215,67),(245,70),(180,42),(160,52),(180,44),(140,43),(160,44),(150,47),(150,47),(130,32)],
        'text_font1_1_loc' : [(255,265),(100,77),(105,67),(115,70),(83,42),(77,52),(80,44),(65,43),(77,44),(69,47),(69,47),(60,32)],
        'line_loc' : [[(255,293),(325,293)],[(32,98),(145,98)],[(35,85),(140,85)],[(35,93),(160,93)],[(25,60),(120,60)],[(23,66),(110,66)],
                    [(30,60),(110,60)],[(20,56),(90,56)],[(23,58),(110,58)],[(20,60),(100,60)],[(20,60),(100,60)],[(18,44),(85,44)]],
        'text_font2_loc' : [(3,773),(3,773),(3,1063),(43,603),(3,853),(3,1103),(3,453),(3,588),(43,803),(3,603),(3,633),(3,1153)],
        'text_font2_1_loc' : [(0,770),(0,770),(0,1060),(40,600),(0,850),(0,1100),(0,450),(0,585),(40,800),(0,600),(0,630),(0,1150)]}
attrs = pd.DataFrame(attrs)


def create_jpg(data, length, category, img_array, grid_array, link_array):
    grid_array.append(length)
    coordinates = All_coordinates[length-1]
    temp = cv2.imread('grid_temp/' + str(length) +'grid.jpg')
    r_s = attrs['r_s'][length-1]
    
    for x in zip(data['Item'], data['mrp'], data['discount'], data['img_url'],data['item_url'],coordinates,data['Quantity']):
        name = x[0] + ' ' + str(x[6]) #str()
        mrp = float(x[1])
        save = x[2]
        y1, y2, x1, x2 = x[5]
        off = round((save/mrp)*100,1)
        price = str(int(mrp - save))
        img_url = x[3]
        item_url = x[4]
        img = url_to_image(img_url)
        img = design_image(img, name, off, r_s)
        temp[y1:y2,x1:x2, :] = img
        img = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype("static/fonts/RobotoCondensed-BoldItalic.ttf", attrs['font_size'][length-1])
        font1 = ImageFont.truetype("static/fonts/RobotoCondensed-BoldItalic.ttf", attrs['font1_size'][length-1])
        draw.text((x1+attrs['text_font_loc'][length-1][0], y2+attrs['text_font_loc'][length-1][1]), price, font=font, fill=(0,0,0))
        draw.text((x1+attrs['text_font1_loc'][length-1][0],y2+attrs['text_font1_loc'][length-1][1]), str(int(save)), font=font1, fill=(27,109,9))
        draw.text((x1+attrs['text_font1_1_loc'][length-1][0],y2+attrs['text_font1_1_loc'][length-1][1]), str(int(mrp)), font=font1, fill=(100,100,100))

        img = np.array(img_pil)
        temp = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        image = cv2.line(temp,(x1+attrs['line_loc'][length-1][0][0], y2+attrs['line_loc'][length-1][0][1]) ,(x1+attrs['line_loc'][length-1][1][0], y2+attrs['line_loc'][length-1][1][1]) , (8,8,255), 2, cv2.LINE_AA) 
        link_array.append(item_url)

    temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
    temp = Image.fromarray(temp)
    font2 = ImageFont.truetype("static/fonts/Roboto-BoldItalic.ttf", attrs['font2_size'][length-1])

    if length in [5,7,8,10,11]:
        cat_list = category.split()
        h=0
        for cat in cat_list:
            x_font, y_font = font2.getsize(cat)
            x = (300-x_font)//2+300
            draw = ImageDraw.Draw(temp)
            draw.text((x+attrs['text_font2_loc'][length-1][0],attrs['text_font2_loc'][length-1][1]+h), cat , font=font2, fill=(232, 210, 14))
            draw.text((x+attrs['text_font2_1_loc'][length-1][0],attrs['text_font2_1_loc'][length-1][1]+h), cat , font=font2, fill=(255,255,255))
            h=h+60

    elif length in [1,2,3,4,6,9,12]:
        x_font, y_font = font2.getsize(category)
        x = (900-x_font+80)//2
        draw = ImageDraw.Draw(temp)
        draw.text((x+attrs['text_font2_loc'][length-1][0],attrs['text_font2_loc'][length-1][1]), category , font=font2, fill=(232, 210, 14))
        draw.text((x+attrs['text_font2_1_loc'][length-1][0],attrs['text_font2_1_loc'][length-1][1]), category , font=font2, fill=(255,255,255))

    img_array.append(temp)


#---download pdf code end--------------------------------
def showItems(catlist):
    catlist = catlist
    with open('frendy_grocery.csv') as f :
        data =csv.reader(f , delimiter =',')
        first_line = True
        responseDF = []
        
        for row in data:
            if not first_line:
                if row[5] in catlist:
                    responseDF.append({
                    "Index" :row[0],
                    "Category" :row[5],
                    "Item" :row[6],
                    "Price" :row[11]})
            else :
                first_line = False
    return responseDF
if __name__=='__main__':
    app.run(debug=True)