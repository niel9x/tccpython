from flask import request
from .models import get_db_connection

# Função para salvar informações da compra no banco de dados
def salvar_compra(id_usuario, id_compra, valor, plano):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insira os dados da compra na tabela de compras
        cursor.execute("INSERT INTO compras (id_usuario, id_compra, valor, plano) VALUES (%s, %s, %s, %s)", (id_usuario, id_compra, valor, plano))
        
        # Obtenha os parâmetros da URL de retorno do MercadoPago
        collection_id = request.args.get('collection_id')
        payment_id = request.args.get('payment_id')
        status = request.args.get('status')
        payment_type = request.args.get('payment_type')
        # Adicione outros campos conforme necessário

        # Insira os dados na tabela de pagamentos
        cursor.execute("INSERT INTO pagamentos (id_usuario, collection_id, payment_id, status, payment_type, nome_produto) VALUES (%s, %s, %s, %s, %s, %s)",
                       (id_usuario, collection_id, payment_id, status, payment_type, plano))

        # Atualize o campo 'assinante' na tabela de usuários se o pagamento for aprovado
        if status == 'approved':
            cursor.execute("UPDATE usuarios SET assinante = 1 WHERE id = %s", (id_usuario,))
        
        conn.commit()
        conn.close()
        return True  # Retorne True se a inserção for bem-sucedida
    except Exception as e:
        print(f"Erro ao salvar compra: {str(e)}")
        conn.rollback()
        conn.close()
        return False  # Retorne False em caso de erro
