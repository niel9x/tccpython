from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import bcrypt
import mysql.connector
from .models import gerar_link_pagamento, salvar_compra, get_db_connection

routes = Blueprint('routes', __name__)

# Função auxiliar para conexão ao banco de dados
def get_db_connection():
    db_config = {
        'user': 'root',
        'password': '',  # Coloque sua senha do MySQL aqui, se houver
        'host': 'localhost',
        'database': 'tcc'
    }
    conn = mysql.connector.connect(**db_config)
    return conn

# Dicionário com os valores dos planos
plan_values = {
    'LifeGuard': 49.90,
    'SecureShield': 99.90,
    'SafeGuard': 199.90
}

# Rota inicial
@routes.route('/')
def home():
    return render_template('home.html')

# Rota para login
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password').encode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password, user['senha_hash'].encode('utf-8')):
            session['email'] = user['email']
            return redirect(url_for('routes.choose_plan'))  # Redireciona para a página de escolha de plano
        else:
            return render_template('login.html', message='Email ou senha inválidos')
    return render_template('login.html')

# Rota para cadastro de usuário
@routes.route('/signup', methods=['POST'])
def signup():
    data = request.form
    phone = data.get('number')
    name = data.get('nome')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if len(phone) != 11:
        return jsonify({'success': False, 'message': 'Número de telefone deve ter exatamente 11 dígitos'})
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Senhas não são idênticas'})
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se o email já está cadastrado
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Email já cadastrado'})
        
        # Verificar se o número de telefone já está cadastrado
        cursor.execute("SELECT * FROM usuarios WHERE numero_telefone = %s", (phone,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Número de telefone já cadastrado'})
        
        # Hash da senha
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Inserir novo usuário se tudo estiver válido
        cursor.execute("INSERT INTO usuarios (nome, email, numero_telefone, senha_hash, assinante) VALUES (%s, %s, %s, %s, %s)", (name, email, phone, hashed_password.decode('utf-8'), False))
        conn.commit()
        conn.close()
        
        session['email'] = email  # Loga automaticamente o usuário após o cadastro
        return redirect(url_for('routes.choose_plan'))  # Redireciona para a página de escolha de plano
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao cadastrar usuário: {str(e)}'})

# Rota para escolher o plano
@routes.route('/choose_plan', methods=['GET', 'POST'])
def choose_plan():
    if 'email' in session:
        email = session['email']
        if request.method == 'POST':
            selected_plan = request.form.get('plan')
            
            # Gerar link de pagamento com plano incluído nas back_urls
            link_pagamento = gerar_link_pagamento(selected_plan)
            
            # Redirecionar para o link de pagamento
            return redirect(link_pagamento)
        
        return render_template('planos.html')
    else:
        return redirect(url_for('routes.login'))

# Rota para processar pagamento aprovado
@routes.route('/compracerta', methods=['GET'])
def processar_pagamento_aprovado():
    collection_id = request.args.get('collection_id')
    payment_id = request.args.get('payment_id')
    preference_id = request.args.get('preference_id')
    status = request.args.get('status')
    payment_type = request.args.get('payment_type')
    plan = request.args.get('plan')
    
    # Obter email do usuário logado
    email = session.get('email')

    # Salvar informações do pagamento no banco de dados
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obter informações do usuário
        cursor.execute("SELECT id, nome FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            # Insira os dados do pagamento na tabela de pagamentos se status for approved
            if status == 'approved':
                valor = plan_values.get(plan)
                cursor.execute(
                    "INSERT INTO pagamentos (id_usuario, nome_usuario, collection_id, payment_id, preference_id, status, payment_type, nome_produto, valor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                    (user['id'], user['nome'], collection_id, payment_id, preference_id, status, payment_type, plan, valor)
                )
                conn.commit()

                # Atualizar o status de assinante do usuário se o pagamento foi aprovado
                cursor.execute("UPDATE usuarios SET assinante = TRUE WHERE id = %s", (user['id'],))
                conn.commit()

        conn.close()

        # Redirecionar para uma página de confirmação de pagamento ou outra página desejada
        return redirect(url_for('routes.confirmacao_pagamento'))

    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Erro ao processar pagamento: {str(e)}"

# Rota para página de confirmação de pagamento
@routes.route('/confirmacao_pagamento')
def confirmacao_pagamento():
    return "Pagamento aprovado com sucesso. Obrigado!"

# Rota para logout
@routes.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('routes.login'))
