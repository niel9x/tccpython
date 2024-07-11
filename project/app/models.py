import mysql.connector
import mercadopago

# Função para obter conexão com o banco de dados
def get_db_connection():
    db_config = {
        'user': 'root',
        'password': '',  # Coloque sua senha do MySQL aqui, se houver
        'host': 'localhost',
        'database': 'tcc'
    }
    conn = mysql.connector.connect(**db_config)
    return conn

def gerar_link_pagamento(plano):
    sdk = mercadopago.SDK("TEST-2401665175791924-060608-ebb16ebaa134b1ab24f158bcc6a86daa-1107030610")
    
    planos = {
        "LifeGuard": 49.90,
        "SecureShield": 99.90,
        "SafeGuard": 199.90
    }

    if plano not in planos:
        raise ValueError("Plano inválido")

    payment_data = {
        "items": [
            {"id": "1", "title": f"[Plano] {plano}", "quantity": 1, "currency_id": "BRL", "unit_price": planos[plano]}
        ],
        "back_urls": {
            "success": f"http://127.0.0.1:5000/compracerta?plan={plano}",
            "failure": "http://127.0.0.1:5000/compraerrada",
            "pending": "http://127.0.0.1:5000/compraerrada",
        },
        "auto_return": "all"
    }
    result = sdk.preference().create(payment_data)
    payment = result["response"]
    return payment["init_point"]

def salvar_compra(id_usuario, id_compra, valor, plano):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO pagamentos (id_usuario, id_compra, valor, nome_produto) VALUES (%s, %s, %s, %s)", (id_usuario, id_compra, valor, plano))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar compra no banco de dados: {str(e)}")
        conn.rollback()
        conn.close()
        return False
