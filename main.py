import pandas as pd
from selenium import webdriver
import time
import random
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as Bs
import requests
import json
import csv

#Sets the webdriver for the operation as the firefox webdriver


def create_webdriver():
    driver_path = "/usr/local/bin/chromedriver"
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    return driver


def netigate_go_to_survey_page(survey_url, driver):
    driver.get(survey_url)
    return


def close_webdriver(driver):
    driver.close()
    return


def click_on_random_button_in_box(box):
    list_of_buttons = box.find_elements('class name', 'form-check')
    button_integer = random.randint(0, len(list_of_buttons)-1)
    list_of_buttons[button_integer].click()
    return


def create_list_of_entrys_from_csv(input_file):
    df = pd.read_csv(input_file)
    df.columns = ['entries']
    output_list = df['entries'].values.tolist()
    return output_list


def get_list_of_questions(driver):  #returns a list of all the questions on a page
    content_container = driver.find_element('id','contentContainer')
    list_of_questions = content_container.find_elements("xpath","./*")
    return (list_of_questions)


def get_question_class(question): #checks the question type and returns it
    question_class = question.get_attribute('class')
    return question_class


def answer_button_questions(question): #for radio-button, check-box
    question_form = question.find_element('class name','form-group')
    list_of_buttons = question_form.find_elements('class name','form-check')
    button_integer = random.randint(0,len(list_of_buttons)-1)
    list_of_buttons[button_integer].click()
    return


def answer_matrix_question(question):
    dots = question.find_element('class name','dots')
    list_of_dots = dots.find_elements('xpath','./*')
    number_of_boxes = sum(1 for i in list_of_dots if 'dot' in str(i.get_attribute('class')))
    for x in range (0, number_of_boxes):
        box = question.find_element('css selector','.netigate_slide.slide_active')
        click_on_random_button_in_box(box)
        time.sleep(2)
    return


def answer_dropdown_question(question):
    dropdown_select = Select(question.find_element('css selector','.netigatedropdown.form-control'))
    dropdown = question.find_element('css selector','.netigatedropdown.form-control')
    list_of_options = dropdown.find_elements('class name','netigatedropdownoption')
    dropdown_integer = random.randint(1,len(list_of_options)-1)
    dropdown_select.select_by_index(dropdown_integer)
    return


def answer_slider_question(question,driver):
    slider = question.find_element('css selector','.ui-slider.ui-corner-all.ui-slider-horizontal.ui-widget.ui-widget-content')
    slider_width = slider.size['width']
    random_factor = random.uniform(0,1)
    slider_button = slider.find_element('css selector','.ui-slider-handle.ui-corner-all.ui-state-default')
    move = ActionChains(driver)
    move.click_and_hold(slider_button).move_by_offset(random_factor*slider_width,0).release().perform()
    return


def answer_text_question(question, list_free_text):
    free_text = list_free_text[random.randint(0, len(list_free_text))]
    question.find_element('css selector', '.netigatetexbox.form-control').send_keys(free_text)
    return


def answer_question(question_class,question,driver,list_free_text): #Answers the given question and executes the correct answer function
    button_question_types = ['netigateRadiobutton','netigateCheckboxes','netigateStarRating','npscontainer']
    for i in button_question_types:
        if i in question_class:
            answer_button_questions(question)
    if 'netigateMatrix' in question_class:
        answer_matrix_question(question)
    elif 'netigateDropdown' in question_class:
        answer_dropdown_question(question)
    elif 'netigateSlider' in question_class:
        answer_slider_question(question,driver)
    elif 'netigateTextbox' in question_class:
        answer_text_question(question, list_free_text)
    return

def go_to_next_page(driver):
    next_button = driver.find_element('id','nextQuestion')
    next_button.click()
    time.sleep(2)
    return


def last_page(driver):
    next_button = driver.find_element('id','nextQuestion')
    button_class = next_button.get_attribute('class')
    if 'finnishSurvey' in button_class:
        return True
    else:
        return False


def choose_random_language(driver):
    language_box = driver.find_element('css selector','.row.survey-translator')
    language_options = language_box.find_elements('class','lang-link-container')
    number_of_options = len(language_options)
    language_int = random.randint(0,number_of_options)
    language_options[language_int].click()
    return

def answer_whole_survey(survey_url, free_text_csv):
    list_free_text = create_list_of_entrys_from_csv(free_text_csv)
    webdriver = create_webdriver()
    netigate_go_to_survey_page(survey_url,webdriver)
    while last_page(webdriver)==False:
        print(last_page(webdriver))
        list_of_questions = get_list_of_questions(webdriver)
        time.sleep(2)
        for i in list_of_questions:
            question_class = get_question_class(i)
            answer_question(question_class,i,webdriver,list_free_text)
            time.sleep(3)
        go_to_next_page(webdriver)
    else:
        print(last_page(webdriver))
        list_of_questions = get_list_of_questions(webdriver)
        time.sleep(3)
        for i in list_of_questions:
            question_class = get_question_class(i)
            answer_question(question_class,i,webdriver,list_free_text)
            time.sleep(3)
        go_to_next_page(webdriver)
        time.sleep(3)
        close_webdriver(webdriver)
    return

answer_whole_survey('https://www.netigate.se/ra/s.aspx?s=1121247X367409907X22438','freitext_antworten.csv')