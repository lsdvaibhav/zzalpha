from flask import Flask,render_template,request,jsonify,make_response,send_file
import response
import numpy
import pandas as pd
#-----flask app code-----------
app = Flask(__name__)


#----routing landing page--------------------------------
@app.route('/')
def index():
    return render_template('index.html')
#----routing landing page--------------------------------
@app.route('/download')
def download():
    return send_file("Quality Sheet.xlsx",as_attachment=True)
#----routing dashboard page--------------------------------
@app.route('/home')
def dashboard():
   
    return render_template('index.html')

#----routing integration page--------------------------------
@app.route('/integration')
def integration():
    return render_template('integration.html')   

#----routing reports page--------------------------------
@app.route('/reports')
def reports():
    return render_template('reports.html')   
    
#----routing Week data and response week data--------------------------------
@app.route('/weekData' , methods=['POST','GET'])
def weekData():
    week = request.form['week']   
    df = pd.read_excel("Quality Sheet.xlsx",sheet_name="Sheet1",header=0,keep_default_na=True,index_col=False)
    df = df[df['Week']==week]
    count = df.groupby('Audit Date')['Associate Code'].nunique()
    dates = df["Audit Date"].unique()
    count1 = []
    for val in count:
        count1.append(val)
    datesList= []
    for date in dates:
        datesList.append(numpy.datetime_as_string(date, unit='D'))
    
    res = make_response(jsonify({ "datares" : count1,"label" : datesList,"TableData" : df.to_html(index = False,classes="table table-hover table-hover-sm ",justify ='left')}),200)
    return res

#----routing Add Row and response added row--------------------------------
@app.route('/addRow' , methods=['POST','GET'])
def addRow():
    
    datalist = request.form['dataRow'].split(",")
    valsReq = request.form['vals'].split(",")
    obs = request.form['obs']
    aoi = request.form['aoi']
    vals =[]
    for i in valsReq:
        if i == "NaN":
            vals.append("NA")
        else :
            vals.append(int(i))
    
    scroreList  = score(vals)
    
    
    final_List = []
    final_List.extend(datalist)
    final_List.extend(vals)
    final_List.append(obs)
    final_List.append(aoi)
    final_List.extend(scroreList)
    
    addROW(final_List)
    res = make_response(jsonify({ "dataRow" : final_List}),200)
    
    return res     

# #----routing Add Row and response added row--------------------------------
# @app.route('/pddProcess' , methods=['POST','GET'])
# def pdProcess():   
    # df = pd.read_excel("Book1.xlsx",sheet_name="Sheet1",header=0,index_col=False,keep_default_na=True)
    # return df.iloc[-1]                

def score(vals):
    vals = vals
    vals1 =[3,3,3,3,3,3,3,2,8,5,8,4,5,5,5,3,5,3,5,10,10,1]
    fatalReasons = [
        'NA','NA','NA','NA','NA','NA','NA','NA',
        'Effective Objection handling and Relevant rebuttals given',
        'Stated the Waiting period and Exclusions',
        'Creates Interest and Urgency (Need Creation)',
        'NA','NA',
        'Correct disposition tagged',
        'NA','NA',
        'Agent Informed the recording Statement as per IRDA (Disclaimer)',
        'NA','NA',
        'Plan presentation, mis-selling or misguiding' ,
        'Correctly premium calculation done & offer (Health Declaration/10% Loading charges)',
        'Agent Rude on call/Sound Sarcastic on call/Call disconnection observed from associate end'
        ]
    summ = 0
    total = 0

    count = 0
    for i in range(len(vals)):
        if(vals[8]==0 or vals[9]==0 or vals[10]==0 or vals[13]==0 or vals[16]==0 or vals[19]==0 or vals[20]==0 or  vals[21]==0  ):
            summ = int(0)
            total = int(100)
            fatal = int(100)
            if vals[i] == 0:
                fatalR = fatalReasons[i]
        else:    
            if (vals[i] == 'NA' or vals[i] == 'nA' or vals[i] == 'Na' or vals[i] == 'na'):
                print(i)
            else:
                summ += vals[i]
                total += vals1[i]
                count += 1
                fatal = "-"
                fatalR = 'NA'
    tota =  summ*100/total
    
    return [fatalR, int(total), int(summ) , int(tota) , fatal] 

def addROW(final_List):
    List_data = final_List
    df = pd.read_excel("Quality Sheet.xlsx",sheet_name="Sheet1",header=0,keep_default_na=True,index_col=False)
    new_Row ={
        'Associate Code':int(List_data[0]),
        'Associate Name':List_data[1],
        'Team Leader Name':List_data[2],
        'DOF':List_data[3],
        'Tenure Bucket':List_data[4],
        'Call Date':List_data[5],
        'Audit Date':List_data[6],
        'Unique No':int(List_data[7]),
        'Call Duration':List_data[8],
        'Auditor Name':List_data[9],
        'Disposition':List_data[10],
        'Sub - Disposition':List_data[11],
        'Week':List_data[12],
        'Greeting / Self & Company introduction done' :List_data[13],
        'Active Listening And Avoid Interruption':List_data[14],
        'Polite And Professional approach throughout The Call(Voice modulation)':List_data[15],
        'Maintains customer pace/Rate of speech/ Grammar':List_data[16],
        'Acknowledge on customer response':List_data[17],
        'Personalization & rapport building with the customer.':List_data[18],
        'Use of proper Phonetics/ apology & sympathy observed on call':List_data[19],
        'Adhered To Hold And Transfer Procedures/ no dead air / unnecessary mute usage ':List_data[20],
        'Effective Objection handling and Relevant rebuttals given':List_data[21],
        'Stated the Waiting period and Exclusions ':List_data[22],
        'Creates Interest and Urgency (Need Creation)':List_data[23],
        'Pitching for 5 or 10 Lacks (Associate can reduce to 3 lack as per cx requirement)':List_data[24],
        'Effective Probing (Health) & Capturing correct  Customer details/ Nominee details, Maintain in Tracker':List_data[25],
        'Correct disposition tagged' :List_data[26],
        'Follow up established with timelines':List_data[27],
        'Verification verbiage-Further assistance offered & appropriate closing done or Trail Closing ( 3 attempt)' :List_data[28],
        'Agent Informed the recording Statement as per IRDA (Disclaimer)':List_data[29],
        'Confirmed the Right Party contact--"Am I speaking with Mr/Mrs._?" & taken permission to continue and language preference checked ' :List_data[30],
        'Purpose of the call informed':List_data[31],
        'Plan presentation, mis-selling or misguiding ':List_data[32],
        'Correctly premium calculation done & offer (Health Declaration/10% Loading charges)':List_data[33],
        'Agent Rude on call/Sound Sarcastic on call/Call disconnection observed from associate end':List_data[34],
        'Call Observation':List_data[35],
        'Area of Opportunity':List_data[36],
        'Fatal Reasons':List_data[37],
        'Total Score':List_data[38],
        'Scorable Achived':List_data[39],
        'QA Score':List_data[40],
        'Fatal Score':List_data[41]
        }
    df = df.append(new_Row, ignore_index=True)
    df.to_excel("Quality Sheet.xlsx", sheet_name='Sheet1' ,index=False) 
    
#-----flask app code-----------
if __name__=='__main__':
    app.run(debug=True)