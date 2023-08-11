from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from lime.lime_text import LimeTextExplainer
import numpy as np
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
from nltk.corpus import stopwords

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
import time
import pandas as pd
from keras.models import load_model
from keras.utils import pad_sequences
import pickle
from flask import Flask, redirect, render_template,request

app = Flask(__name__)
model = load_model('news_ChatBot.h5')

class_names=["fake","true"]

explainer= LimeTextExplainer(class_names=class_names)
posts_dd = []
text_list = []
post_urls = []
global poster_info
poster_info = []

def retrieve_feed(driver):
    username= "kavyababu17@gmail.com"
    password = "Kavyababu1789@!"
    driver.get('https://www.linkedin.com/home')
    driver.find_element(By.XPATH,"//input[@type='text']").send_keys(username)
    driver.find_element(By.XPATH,"//input[@type='password']").send_keys(password)
    driver.find_element(By.XPATH,"//button[@type='submit']").click()
    # driver.get('https://www.linkedin.com/feed/')
    driver.current_url
    feed_complete_block = driver.find_elements(By.XPATH,"//div[@class='scaffold-finite-scroll__content']/div")
    # print(feed_complete_block)
    for feed in feed_complete_block:
        driver.execute_script("arguments[0].scrollIntoView();",feed)
        time.sleep(3)

    total = len(feed_complete_block)
    return total

def preprocess_text(text):
    text = re.sub(r'http\S+', '', text.lower())
    text = re.sub('[^a-zA-Z\s]', '', str(text))
    stopwords_dict = {word: 1 for word in stopwords.words("english")}
    text = " ".join([word for word in text.split() if word not in stopwords_dict])
    return text

def test_news(str):

    str = preprocess_text(str)
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    str = tokenizer.texts_to_sequences(str);
    str = pad_sequences(str, maxlen=1000);
    res = model.predict(str)
    result = (res >=0.5).astype(int);

    value = result[0][0]

    if value == 1:
        return round(res[0][0],2),"True"
    else:
        return round(res[0][0],2),"Fake"

@app.route('/')
def home():
    service_obj = Service(r"C:/Users/kavya/Downloads/chromedriver_win32/chromedriver.exe")
    driver = webdriver.Chrome(options=chrome_options,service=service_obj)
    total = retrieve_feed(driver)
    for i in range(0,7):
        post_details = {}
        img_src = driver.find_elements(By.XPATH,"//div[contains(@class,'update-components-actor__image relative')]/span/div/div/img")[i].get_attribute('src')
        post_details['Image'] = img_src
        url = driver.find_elements(By.XPATH,"//div[contains(@class,'update-components-actor')]/a")[i].get_attribute('href')
        post_details['url'] = url
        post_urls.append(url)
        poster_name = driver.find_elements(By.XPATH,"//span[contains(@class,'update-components-actor__title')]")[i].text
        pp = poster_name.split("\n")
        post_details['name'] = pp[0]
        posts_text = driver.find_elements(By.XPATH,"//div[contains(@class,'update-components-text relative feed-shared-update-v2__commentary')]/span")[i].text
        post_details['text'] = posts_text
        text_list.append(posts_text)
        post_details['predict_score'],post_details['result'] = test_news([posts_text])
        posts_dd.append(post_details)

    poster_info = retrieve_poster_information(driver,post_urls)
    with open("poster_info.json", "w") as outfile:
        json.dump(poster_info, outfile)
    return render_template('index.html', posts_details = enumerate(posts_dd), text_list=text_list)

@app.route('/result', methods=['POST'])
def index():
    text = request.form['text']
    ind = request.form.get('index_val')
    with open('poster_info.json', 'r') as openfile:
     poster_info = json.load(openfile)
    ind = int(ind)
    poster_info_idx = poster_info[ind]
    text = preprocess_text(text)
    ex = explainer.explain_instance(text,predict_prob)
    return render_template('index.html', exp=ex.as_html(), poster_info = poster_info_idx)

def predict_prob(text):
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    text = tokenizer.texts_to_sequences(text)
    text = pad_sequences(text, maxlen=1000)
    result = model.predict(text)
    returnable=[]
    for i in result:
        temp=i[0]
        returnable.append(np.array([1-temp,temp]))

    return np.array(returnable)

# def display_image(url):
#     return f'<img src="{url}" width="50" height="50">'

def retrieve_poster_information(driver,post_urls):
    total = len(post_urls)
    for i in range(0,total):
        url_path = post_urls[i]
        driver.get(url_path)
        if len(driver.find_elements(By.XPATH,"//ul[contains(@class,'org-page-navigation__items')]//li/a[text()='Posts']"))>0:
            driver.find_element(By.XPATH,"//ul[contains(@class,'org-page-navigation__items')]//li/a[text()='Posts']").click()
            driver.implicitly_wait(10)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='scaffold-finite-scroll__content']/div")))
            profile_complete_post = driver.find_elements(By.XPATH,"//div[@class='scaffold-finite-scroll__content']/div")
            for feed in profile_complete_post:
                driver.execute_script("arguments[0].scrollIntoView();",feed)
                time.sleep(10)
            empty_arr = []
            length = len(profile_complete_post)
            for i in range(0,length):
                post_details = {}
                posts_text = driver.find_elements(By.XPATH,"//div[contains(@class,'update-components-text relative feed-shared-update-v2__commentary')]/span")[i].text
                post_details['text'] = posts_text
                text_list.append(posts_text)
                empty_arr.append(post_details)
            poster_info.append(empty_arr)
        else:
            driver.implicitly_wait(10)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "(//footer[contains(@class,'artdeco-card__actions profile-creator-shared-content-view__footer-actions')])[1]/a")))
            driver.find_element(By.XPATH,"(//footer[contains(@class,'artdeco-card__actions profile-creator-shared-content-view__footer-actions')])[1]/a").click()
            driver.implicitly_wait(10)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='scaffold-finite-scroll__content']/div")))
            profile_complete_post = driver.find_elements(By.XPATH,"//div[contains(@class, 'feed-shared-update-v2--e2e')]")
            for feed in profile_complete_post:
                driver.execute_script("arguments[0].scrollIntoView();",feed)
                time.sleep(10)
            empty_arr = []
            length = len(profile_complete_post)
            for i in range(0,length):
                post_details = {
                    "text": ""
                }
                posts_text = driver.find_elements(By.XPATH,"//div[contains(@class,'update-components-text relative feed-shared-update-v2__commentary')]/span")[i].text
                post_details['text'] = posts_text
                empty_arr.append(post_details)
            poster_info.append(empty_arr)

    return poster_info


if __name__ == "__main__":
    app.run(debug=True)

