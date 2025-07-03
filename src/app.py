# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from user_authentication import services

app = Flask(__name__)
# flash 메시지를 사용하려면 secret_key가 필요합니다.
app.secret_key = 'supersecretkey'

@app.route('/')
def index():
    """
    메인 페이지, 로그인 페이지로 리디렉션합니다.
    """
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    회원가입 페이지 및 양식 처리
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            services.create_user(username, email, password)
            flash('회원가입이 성공적으로 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    로그인 페이지 및 양식 처리
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = services.get_user_by_email(email)
        
        if user and services.verify_password(password, user.hashed_password):
            flash(f'로그인 성공! {user.username}님 환영합니다.', 'success')
            # 실제 애플리케이션에서는 여기서 세션 관리를 시작합니다.
            return redirect(url_for('login'))
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/grid')
def grid_view():
    """
    GridFile 시스템을 시각화하여 보여줍니다.
    """
    layout_path = os.path.join(os.path.dirname(__file__), '..', '.gridfile', 'layouts', 'current.json')
    
    if not os.path.exists(layout_path):
        # current.json이 없으면 initial.json을 사용
        layout_path = os.path.join(os.path.dirname(__file__), '..', '.gridfile', 'layouts', 'initial.json')

    if os.path.exists(layout_path):
        with open(layout_path, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
        # Pass the layout data as a JSON string for easy use in JavaScript
        return render_template('grid.html', layout_json=json.dumps(layout_data))
    else:
        flash('Grid layout 파일을 찾을 수 없습니다.', 'error')
        return redirect(url_for('login'))

if __name__ == '__main__':
    # 디버그 모드로 실행
    app.run(debug=True, port=5000)
