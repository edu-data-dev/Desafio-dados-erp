import sqlite3
import json
import os

# --- Configuração dos Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, 'case_eng.db')
JSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'ERP.json')
SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'sql', 'schema.sql')

def create_database(conn):
    """Lê o arquivo .sql e cria as tabelas no banco de dados."""
    print("Criando tabelas a partir de sql/schema.sql...")
    try:
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        print("Tabelas criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        raise

def insert_data(conn, data):
    """Insere os dados do JSON nas tabelas do banco de dados."""
    cursor = conn.cursor()
    print("Iniciando a inserção de dados...")

    for guest_check in data['guestChecks']:
        # 1. Inserir na tabela principal 'guest_checks'
        try:
            cursor.execute("""
                INSERT INTO guest_checks (
                    guest_check_id, location_ref, check_number, is_closed, guest_count,
                    subtotal, check_total, discount_total, payment_total, table_number,
                    employee_number, opened_at_utc, closed_at_utc, last_transaction_at_utc,
                    last_updated_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                guest_check['guestCheckId'], data['locRef'], guest_check['chkNum'],
                guest_check['clsdFlag'], guest_check['gstCnt'], guest_check['subTtl'],
                guest_check['chkTtl'], guest_check['dscTtl'], guest_check['payTtl'],
                guest_check['tblNum'], guest_check['empNum'], guest_check['opnUTC'],
                guest_check['clsdUTC'], guest_check['lastTransUTC'], guest_check['lastUpdatedUTC']
            ))
            print(f"Pedido {guest_check['guestCheckId']} inserido em 'guest_checks'.")
        except sqlite3.IntegrityError:
            print(f"Pedido {guest_check['guestCheckId']} já existe. Pulando inserção principal.")
            continue 

        # 2. Inserir na tabela 'guest_check_taxes'
        if guest_check.get('taxes'):
            for tax in guest_check['taxes']:
                cursor.execute("""
                    INSERT INTO guest_check_taxes (
                        guest_check_id, tax_number, taxable_sales_total,
                        tax_collected_total, tax_rate, tax_type
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    guest_check['guestCheckId'], tax['taxNum'], tax['txblSlsTtl'],
                    tax['taxCollTtl'], tax['taxRate'], tax['type']
                ))
            print(f"  - {len(guest_check['taxes'])} imposto(s) inserido(s) para o pedido {guest_check['guestCheckId']}.")

        # 3. Inserir na tabela 'detail_lines'
        if guest_check.get('detailLines'):
            for line in guest_check['detailLines']:
                line_type = 'UNKNOWN'
                menu_item_number = None
                if 'menuItem' in line:
                    line_type = 'MENU_ITEM'
                    menu_item_number = line['menuItem']['miNum']

                cursor.execute("""
                    INSERT INTO detail_lines (
                        guest_check_line_item_id, guest_check_id, line_number,
                        line_type, display_total, display_quantity, menu_item_number,
                        detail_at_utc, last_updated_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    line['guestCheckLineItemId'], guest_check['guestCheckId'], line['lineNum'],
                    line_type, line['dspTtl'], line['dspQty'], menu_item_number,
                    line['detailUTC'], line['lastUpdateUTC']
                ))
            print(f"  - {len(guest_check['detailLines'])} linha(s) de detalhe inserida(s) para o pedido {guest_check['guestCheckId']}.")

    conn.commit()
    print("Inserção de dados concluída.")

def main():
    """Função principal que orquestra a criação e população do banco de dados."""
    
    # Apaga o banco de dados antigo, se existir, para garantir uma execução limpa
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Banco de dados antigo '{DB_PATH}' removido.")

    conn = None
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(DB_PATH)

        # Cria a estrutura de tabelas
        create_database(conn)

        # Carrega os dados do arquivo JSON
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            erp_data = json.load(f)

        # Insere os dados no banco de dados
        insert_data(conn, erp_data)

        print("\nProcesso finalizado com sucesso!")
        print(f"Você pode inspecionar o resultado no arquivo: {DB_PATH}")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()