import telebot
import requests
import time
from telebot import types

bot = telebot.TeleBot('6205918867:AAG7Vz4DSicKhCFMnRYe6BDDxkEO90ScdQo')

# Define the list of subjects
subjects = ['Mathematics (9709)', 'Computer Science (9608)', 'Computer Science (9618)', 'Physics (9702)', 'Chemistry (9701)', 'Biology (9700)', 'Business (9609)']
dic_subjects = {'9709' : 'Mathematics (9709)', '9608' : 'Computer Science (9608)', '9618' : 'Computer Science (9618)', '9702' : 'Physics (9702)', '9701' : 'Chemistry (9701)', '9700' : 'Biology (9700)', '9609' : 'Business (9609)'}
dic_name = {'(9608)' : 'Computer%20Science%20(for%20final%20examination%20in%202021)%20(9608)', '(9618)' : 'Computer%20Science%20(for%20first%20examination%20in%202021)%20(9618)', '(9709)' : 'Mathematics%20(9709)', '(9702)' : 'Physics%20(9702)', '(9700)' : 'Biology%20(9700)', '(9701)' : 'Chemistry%20(9701)', '(9609)' : 'Business%20(9609)'}

# Handler for the /start command
@bot.message_handler(commands=['start'])
def start(message):
    text = f'<b>Hi, {message.from_user.first_name}!</b>\n\nUse the /help command to see the available options.'
    bot.send_message(message.chat.id, text, parse_mode='html')

# Handler for the /help command
@bot.message_handler(commands=['help'])
def help(message):
    text = 'This bot will help you find past papers for Cambridge A-level exams.\n\n' + \
           'To get started, choose a subject from the list below:\n'
    markup = create_subjects_markup()
    bot.send_message(message.chat.id, text, reply_markup=markup)

# Handler for text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text

    # Handle back button
    if text[:4] == 'Back':
        markup, to_user = create_back_function(text)

    # Handle paper_file selection
    elif text.split('_',1)[0] in ['Question', 'Marking']:
        url, name = create_url(text)

        # Send the file
        file_name = f'D:/Telegram_bot/{name}'
        response = requests.get(url)
        print(url)
        if response.status_code == 200:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="Website", url=url))
            try:
                file = open(file_name, 'rb')
                bot.send_document(message.chat.id, file, reply_markup = markup)
            except:
                with open(file_name, 'wb') as file:
                    file.write(response.content)
                file = open(file_name, 'rb')
                bot.send_document(message.chat.id, file, reply_markup = markup)
        else:
            try:
                file = open(file_name, 'rb')
                bot.send_document(message.chat.id, file)
            except:
                bot.send_message(message.chat.id, "We don't have this file yet")
        to_user = 0

    # Handle subject selection
    elif text in subjects:
        markup = create_years_markup(text)
        to_user = 'Choose a year:'

    # Handle year selection
    elif text[:4].isdigit():
        markup = create_months_markup(text)
        to_user = 'Choose a month:'

    # Handle month selection
    elif text[:6] in ['Spring', 'Summer', 'Winter']:
        markup = create_papers_markup(text)
        to_user = 'Choose a paper:'

    # Handle paper_number selection
    elif text.split('-',1)[0].count('.') < 1:
        markup, to_user = create_variants_markup(text)

    # Handle variant selection
    elif text.split('-',1)[0].count('.'):
        markup = create_qp_ms_markup(text)
        to_user = 'Question paper or marking scheme'

    if to_user: bot.send_message(message.chat.id, to_user, reply_markup=markup)

# Helper function to create the subjects markup
def create_subjects_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for subject in subjects: markup.add(subject)
    return markup

# Helper function to create the years markup
def create_years_markup(name):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # Condition to define years of past paper
    end = 2023
    if time.localtime().tm_mon in [2, 5, 10]:
        url = f"https://papers.gceguide.com/A%20Levels/{dic_name[name.rsplit(' ',1)[1]]}/"
        text = requests.get(url).text
        index = text.index('</a></li><li class="dir"><a href="Other Resources"')
        end = int(text[index-4:index]) + 1
    if name == 'Computer Science (9608)': start, end = 2015, 2022
    elif name == 'Computer Science (9618)': start = 2021
    elif name == 'Mathematics (9709)': start = 2001
    elif name == 'Physics (9702)': start = 2002
    elif name == 'Chemistry (9701)': start = 2001
    elif name == 'Biology (9700)': start = 2001
    elif name == 'Business (9609)': start = 2016

    for year in range(start, end): markup.add(f'{year} {name}')
    markup.add('Back to subjects')
    return markup

# Helper function to create the months markup
def create_months_markup(text):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    dic_month = {'March' : 'Spring', 'June' : 'Summer', 'November' : 'Winter'}
    year = text.split(' ',1)[0]
    name = text.rsplit(' ',1)[1]
    url = f"https://papers.gceguide.com/A%20Levels/{dic_name[name]}/{year}/"
    web = requests.get(url).text
    for month in web.split('listtitle')[1:]:
        item = month[2:6]
        if item not in dic_month: item = month[2:7]
        if item not in dic_month: item = month[2:10]
        markup.add(f"{dic_month[item]} {year} {name}")
    back = dic_subjects[text[6:10]] if text[6:10] in dic_subjects else text[5:]
    markup.add(f'Back to {back}')
    return markup

# Helper function to create the papers markup
def create_papers_markup(month):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    year = int(month[7:11])
    dic = {'(9709)' : 6 if year > 2019 else 7, '(9608)' : 4, '(9618)' : 4, '(9702)' : 5, '(9701)' : 5, '(9700)' : 5, '(9609)' : 3}
    number = dic[month.rsplit(' ',1)[1]]

    for paper in range(1, number + 1): markup.add(f'Paper {paper} - {month}')
    markup.add(f'Back to {month[7:]}')

    return markup

# Helper function to create the variant markup
def create_variants_markup(text):
    paper = text[:7]
    month = text.rsplit('- ',1)[1]
    if int(month[7:11]) == 2009 and month[:6] != 'Winter': markup = create_qp_ms_markup(text)
    elif int(month[7:11]) < 2010: markup = create_qp_ms_markup(text)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        if month[:6] == 'Spring': markup.add(f'{paper}.2 - {month}')
        else:
            for variant in range(1,4): markup.add(f'{paper}.{variant} - {month}')
        markup.add(f'Back to {text}')
    to_user = 'Choose paper' if int(month[7:11]) < 2010 else 'Choose variant'
    return markup, to_user

# Helper function to create type of paper markup
def create_qp_ms_markup(text):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(f'Question_{text}')
    markup.add(f'Marking_Scheme{text[5:]}')
    markup.add(f'Back to {text}')
    return markup

# Helper function to create url
def create_url(text):
    dic_date = {'Spring' : 'm', 'Summer' : 's', 'Winter' : 'w'}
    dic_tip = {'Question_Paper' : 'qp', 'Marking_Scheme' : 'ms'}
    dic_code = {'(9709)' : 7, '(9608)' : 4, '(9618)' : 4, '(9702)' : 5, '(9701)' : 5, '(9700)' : 5, '(9609)' : 3}

    for word in list(text.split()):
        if word in ['Question_Paper', 'Marking_Scheme']: tip = dic_tip[word]
        elif word.count('.'): variant = '_' + word.replace('.','')
        elif word in dic_date: date = dic_date[word]
        elif word.isdigit():
            if int(word) in range(1,8): variant = word
            else:year = word[2:]
        elif word.count('('):
            code = word[1:5]
            subject = f'{dic_name[word]}'
    if year == '03':
        if date != 'w':
            variant = '_1'
            for i in range(2,dic_code[f'({code})'] + 1): variant += f'+{i}'
        else: variant = ''
    name = f'/{code}_{date}{year}_{tip}{variant}.pdf'
    link = f'https://papers.gceguide.com/A%20Levels/{subject}/20{year}{name}'
    url = link.replace(' ','%20')

    return url, name

# Helper function to pass back
def create_back_function(text):
    text = text[8:]

    if text == 'subjects': markup = create_subjects_markup()
    elif text in subjects: markup = create_years_markup(text)
    elif text[:4].isdigit(): markup = create_months_markup(text)
    elif text.split('-',1)[0].count('.') < 1:
        markup = create_papers_markup(text[10:])
        text = f'paper for {text[10:]}'
    elif text.split('-',1)[0].count('.'):
        markup = create_variants_markup(text)
        text = f'variant for {text[:7]}{text[9:]}'

    to_user = 'Choose ' + text
    return markup, to_user

# Start polling for updates
bot.polling(none_stop=True)
