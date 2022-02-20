from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import telebot

#your telegram bot token
token = ''

def telegram_bot(token):

    bot = telebot.TeleBot(token)
    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, 'Добрый день! Введите серию и номер паспорта:')


    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if len(message.text) == 10 and message.text.isdigit() == True:
            bot.send_message(message.chat.id, 'Идет проверка...')
            bot.send_message(message.chat.id, get_data(message.text))
        else:
            bot.send_message(message.chat.id, 'Некорректный формат. Введите серию и номер паспорта в формате: 8000123456')

    bot.polling()


def get_data(pass_number):
    #rucaptcha service api key https://rucaptcha.com/enterpage
    rucaptcha_apikey = ''
    seriya = pass_number[:4]
    nomer = pass_number[4:]

    driver = webdriver.Chrome(executable_path="C:\chromedriver\chromedriver.exe")
    url = "http://services.fms.gov.ru/info-service.htm?sid=2000"

    try:
        driver.get(url=url)
        time.sleep(1)

        seriya_input =  driver.find_element(By.ID, value="form_DOC_SERIE")
        seriya_input.clear()
        seriya_input.send_keys(seriya)

        number_input =  driver.find_element(By.ID, value="form_DOC_NUMBER")
        number_input.clear()
        number_input.send_keys(nomer)

        captcha_img = driver.find_element(By.ID, value="captcha_image").screenshot_as_base64
        url_captcha = 'http://rucaptcha.com/in.php'
        param_request = {'key': rucaptcha_apikey, 'method': 'base64', 'body': captcha_img, 'json': '1', 'numeric': '1'}
        response = requests.post(url_captcha, param_request)
        captcha_id = response.json()['request']
        time.sleep(5)

        captcha_answer = 'CAPCHA_NOT_READY'

        while captcha_answer == 'CAPCHA_NOT_READY':
                url_captcha_res = 'http://rucaptcha.com/res.php'
                param_get = {'key': rucaptcha_apikey, 'action': 'get', 'id': captcha_id, 'json': '1'}
                captcha_get = requests.get(url_captcha_res, param_get)
                captcha_answer = captcha_get.json()['request']
        captcha_input =  driver.find_element(By.ID, value="form_captcha-input")
        captcha_input.clear()
        captcha_input.send_keys(captcha_answer)

        send_button = driver.find_element(By.ID, value="form_submit").click()


        pass_result = driver.find_element(By.CLASS_NAME, value='ct-h4').text
        return(pass_result)

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    telegram_bot(token)
