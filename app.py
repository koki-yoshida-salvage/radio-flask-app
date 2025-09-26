from flask import Flask, render_template, request

from datetime import datetime

import csv
import os

from collections import Counter
import csv

import matplotlib.pyplot as plt

from janome.tokenizer import Tokenizer

import os


def analyze_keywords():
    contents = []
    with open('messages.csv', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contents.append(row['Content'])

    # 単語に分割（簡易版）
    words = ' '.join(contents).split()
    counter = Counter(words)
    return counter.most_common(10)  # 上位10語を返す

def plot_keywords():
    keywords = analyze_keywords()
    labels, values = zip(*keywords)
    plt.bar(labels, values, color='#ffcc66')
    plt.xticks(rotation=45)
    plt.title('人気ワードランキング')
    plt.tight_layout()
    plt.show()

def analyze_japanese_keywords():
    tokenizer = Tokenizer()
    contents = []
    with open('messages.csv', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contents.append(row['Content'])

    words = []
    for text in contents:
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            part = token.part_of_speech.split(',')[0]
            if part == '名詞':  # 名詞だけ抽出
                words.append(token.surface)

    counter = Counter(words)
    return counter.most_common(10)


def save_message(name, content, theme):
    file_path = 'messages.csv'
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Name', 'Content', 'Theme', 'Timestamp'])  # ヘッダー行
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        writer.writerow([name, content, theme, timestamp])


app = Flask(__name__)
messages = []

current_theme = "ラジオの作り方"  #ラジオテーマを設定

@app.route('/')
def home():
    return render_template('home.html', theme=current_theme)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        save_message(name, content, current_theme)
        return render_template('thanks.html', name=name)
    return render_template('submit.html', theme=current_theme)


@app.route('/messages')
def show_messages():
    messages = []
    try:
        with open('messages.csv', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                messages.append({
                'name': row['Name'],
                'content': row['Content'],
                'theme': row.get('Theme', '未分類'),
                'timestamp': row.get('Timestamp', '日時なし')
        })
    except FileNotFoundError:
        pass
    return render_template('messages.html', messages=messages)

@app.route('/keywords')
def keywords():
    top_words = analyze_japanese_keywords()
    return render_template('keywords.html', keywords=top_words)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)