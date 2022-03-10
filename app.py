import streamlit as st
from PIL import Image
import json
import imageio
import requests
import time
import db_communication
import hydralit_components as hc


DB = db_communication.DatabaseCommunicator()

def load_image(image_file):
	img = Image.open(image_file)
	return img

st.set_page_config(layout='wide')

showtitle = st.empty()
showimg = st.empty()
showtitle.markdown("<h1 style='text-align: center; color: firebrick;'>ImageToInsulin Estimator</h1>", unsafe_allow_html=True)
image_file = showimg.file_uploader("", type=["png","jpg","jpeg"], key = 1)


if image_file is not None:
    initial_state = 0

    # if initial_state == 0:
    #     with hc.HyLoader('Food detective running...',hc.Loaders.standard_loaders,index=[2,2]):
    #         showimg.empty()
    #         resp = requests.post("http://34.134.211.187:8080/", files={'file': image_file.getvalue()})
    #         time.sleep(2)
    resp = requests.post("http://34.134.211.187:8080/", files={'file': image_file.getvalue()})
    initial_state = 0
    response_list = json.loads(resp.json()['result'].replace("'",'"'))
    response = response_list[-1]
    pred_list = [k for k in response_list[:-1]]
    labels=[]
    confidences = {}
        
    imgcol, identified_food, inputs = st.columns((1, 1, 1))
    imgcol.image(load_image(image_file),width=600)

    for idx, r in enumerate(pred_list):
        for cls, conf in r.items():
            labels.append(cls)
            confidences[cls] = conf


    food_to_carb = {k:0 for k in labels}
    food_to_weight = {k:0 for k in labels}
    food_to_feedback = {k:1 for k in labels}
    f = open('carb_lookup.json')
    data = json.load(f)

    insulin_factor = identified_food.number_input('Your Insulin Factor: ' ,key=10)
    identified_food.subheader('Identified foods:')
    inputs.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    inputs.write('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    inputs.write('Correctly identified food?')
    
    for idx, label in enumerate(labels):

        identified_food.write(str(idx+1)+'. '+str(label).upper())
        agree = inputs.checkbox(str(idx+1)+'. '+str(label).upper(),key=idx+1)
        
        
        if not agree:
            food_to_feedback[label] = 0
        else:
            number = inputs.number_input('weight in grams',key=idx)
            food_to_weight[label] = number 

        try:# To check carb amount of this label, if isnt found then 0 is assigned.
            food_to_carb[label] = data[label]['carbs']

        except:
            food_to_carb[label] = 0


    submit_button = inputs.button('Submit')
    if submit_button:
        inputs.write('Calculating...')
        sum = 0

        for item1, item2 in zip(food_to_carb.items(), food_to_weight.items()):
            food, carb = item1
            _, weight = item2
            sum += (carb/100)*weight
        insulin_dosage = insulin_factor * sum

        inputs.subheader('Insulin dosage recommended: '+str(round(insulin_dosage, 2)))

        DB.add_entry(entries=[{'classname':l, 'confidence':confidences[l], 'accepted':food_to_feedback[l], 'weight': food_to_weight[l]} for l in labels], insulin_factor=insulin_factor, model_used='nano', response_time=response['Response_time'], insulin_amount=insulin_dosage)

    # else:
    #     st.header('Sorry we couldnt service you.')