import pandas as pd
from selenium import webdriver
import time
import random
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
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


def click_on_random_button_in_box(box, webdriver):
    actions = ActionChains(webdriver)
    list_of_buttons = box.find_elements('class name', 'form-check')
    button_integer = random.randint(0, len(list_of_buttons)-1)
    element = list_of_buttons[button_integer]
    try:
        actions.move_to_element(element).perform()
        element.click()
        return
    except ElementClickInterceptedException:
        webdriver.execute_script("arguments[0].scrollIntoView()", element)
        time.sleep(0.5)
        element.click()
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


def answer_button_questions(question, webdriver): #for radio-button, check-box
    actions = ActionChains(webdriver)
    question_form = question.find_element('class name','form-group')
    list_of_buttons = question_form.find_elements('class name','form-check')
    button_integer = random.randint(0,len(list_of_buttons)-1)
    element = list_of_buttons[button_integer]
    try:
        actions.move_to_element(element).perform()
        element.click()
        return
    except ElementClickInterceptedException:
        try:
            webdriver.execute_script("arguments[0].scrollIntoView()", element)
            time.sleep(1)
            element.click()
            return
        except ElementClickInterceptedException:
            actions.move_to_element(element).perform()
            webdriver.execute_script("arguments[0].click()", element)
            return


def answer_matrix_question(question, driver):
    dots = question.find_element('class name','dots')
    list_of_dots = dots.find_elements('xpath','./*')
    number_of_boxes = sum(1 for i in list_of_dots if 'dot' in str(i.get_attribute('class')))
    for x in range (0, number_of_boxes):
        box = question.find_element('css selector','.netigate_slide.slide_active')
        click_on_random_button_in_box(box, driver)
        time.sleep(1)
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


def answer_text_field_question(question, list_free_text):
    form_field =  question.find_element('css selector','.netigatetexbox.form-control')
    if 'datepicker' in form_field.get_attribute('class'):
        answer_date_picker_textfield(question)
    elif 'sum' in form_field.get_attribute('class'):
        answer_date_numeric_textfield(question)
    else:
        free_text = list_free_text[random.randint(0, len(list_free_text)-1)]
        question.find_element('css selector', '.netigatetexbox.form-control').send_keys(free_text)
    return


def answer_text_area_question(question, list_free_text):
    free_text = list_free_text[random.randint(0, len(list_free_text)-1)]
    question.find_element('css selector', '.netigatetextarea.form-control').send_keys(free_text)
    return



def answer_date_picker_textfield(question):
    day = str(random.randint(0,30))
    month = str(random.randint(1,12))
    year = str(random.randint(1950,1994))
    date = day+"."+month+"."+year
    question.find_element('css selector', '.netigatetexbox.form-control').send_keys(date)
    return


def answer_date_numeric_textfield(question):
    number = str(random.randint(18,68))
    question.find_element('css selector', '.netigatetexbox.form-control').send_keys(number)
    return


def answer_question(question_class,question,driver,list_free_text): #Answers the given question and executes the correct answer function
    actions = ActionChains(driver)
    actions.move_to_element(question).perform()
    button_question_types = ['netigateRadiobutton','netigateCheckboxes','netigateStarRating','npscontainer','radiobuttons','checkboxes']
    for i in button_question_types:
        if i in question_class:
            answer_button_questions(question, driver)
    if 'netigateMatrix' in question_class:
        answer_matrix_question(question, driver)
    elif 'netigateDropdown' in question_class:
        answer_dropdown_question(question)
    elif 'netigateSlider' in question_class:
        answer_slider_question(question,driver)
    elif 'netigateTextbox' in question_class:
        answer_text_field_question(question, list_free_text)
    elif 'netigateTextArea' in question_class:
        answer_text_area_question(question, list_free_text)
    return

def go_to_next_page(driver):
    try:
        next_button = driver.find_element('id', 'nextQuestion')
        next_button.click()
        time.sleep(1)
        return
    except ElementNotInteractableException:
        driver.close()
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
    language_options = language_box.find_elements('class name','lang-link-container')
    number_of_options = len(language_options)-1
    language_int = random.randint(0,number_of_options)
    language_options[language_int].click()
    return


def check_for_language_selector(driver):
    try:
        driver.find_element('css selector','.row.survey-translator')
    except NoSuchElementException:
        return False
    return True

def answer_questions_on_page(driver, free_text_answers):
    list_of_questions = get_list_of_questions(driver)
    time.sleep(1)
    for i in list_of_questions:
        question_class = get_question_class(i)
        answer_question(question_class, i, driver, free_text_answers)
        time.sleep(1)
    go_to_next_page(driver)
    return


def answer_whole_survey(survey_url, free_text_csv):
    list_free_text = create_list_of_entrys_from_csv(free_text_csv)
    webdriver = create_webdriver()
    netigate_go_to_survey_page(survey_url,webdriver)
    if check_for_language_selector(webdriver) == True:
        choose_random_language(webdriver)
    while last_page(webdriver)==False:
        answer_questions_on_page(webdriver,list_free_text)
    else:
        answer_questions_on_page(webdriver,list_free_text)
    return


def main(number_of_tests, survey_url, free_text_answers):
    for i in tqdm(range (0,number_of_tests)):
        answer_whole_survey(survey_url,free_text_answers)
    return

#if __name__ =="__main__":
#    main(100,'https://www.netigate.se/a/s.aspx?s=1130051X372713211X28429','freetext_english.csv')
