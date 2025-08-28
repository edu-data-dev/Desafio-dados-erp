import os
import shutil
from datetime import datetime
from pathlib import Path

# --- Configuração dos Caminhos ---
PROJECT_ROOT = Path(__file__).parent.parent
LAKE_BASE_PATH = PROJECT_ROOT / 'datalake'
SOURCE_DATA_PATH = PROJECT_ROOT / 'data' / 'ERP.json'

def simulate_ingestion(source_file_path, store_id, business_date_str, endpoint):
    """
    Simula a ingestão de um arquivo em uma estrutura de pastas particionada.

    Args:
        source_file_path (Path): O caminho do arquivo a ser copiado.
        store_id (str): O ID da loja para o particionamento.
        business_date_str (str): A data de negócio no formato 'YYYY-MM-DD'.
        endpoint (str): O nome do endpoint da API.
    """
    try:
        # Converter a string de data para um objeto datetime
        business_date = datetime.strptime(business_date_str, '%Y-%m-%d')
        year = business_date.year
        month = f"{business_date.month:02d}" # Formata com zero à esquerda (01, 02, ...)
        day = f"{business_date.day:02d}"

        # Monta o caminho de destino particionado
        dest_dir = (
            LAKE_BASE_PATH / 'raw' / 'erp_api' / endpoint /
            f'year={year}' / f'month={month}' / f'day={day}' / f'store_id={store_id}'
        )

        # Criar a estrutura de diretórios se ela não existir
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Definir o nome do arquivo de destino (pode incluir um timestamp para unicidade)
        timestamp = int(datetime.now().timestamp())
        dest_file_path = dest_dir / f'{timestamp}_{source_file_path.name}'

        # Copiar o arquivo de origem para o destino
        shutil.copy(source_file_path, dest_file_path)

        print(f"SUCESSO: Arquivo '{source_file_path.name}' ingerido para '{dest_file_path}'")

    except Exception as e:
        print(f"ERRO: Falha ao ingerir o arquivo para store_id={store_id}. Erro: {e}")

def main():
    """Função principal para executar a simulação."""
    print("--- Iniciando Simulação de Ingestão no Data Lake ---")

    # Dados de exemplo para a simulação
    simulations = [
        {"store_id": "99_CB_CB", "bus_dt": "2025-08-27", "endpoint": "getGuestChecks"},
        {"store_id": "101_BSB", "bus_dt": "2025-08-27", "endpoint": "getGuestChecks"},
        {"store_id": "99_CB_CB", "bus_dt": "2025-08-28", "endpoint": "getFiscalInvoice"},
        {"store_id": "102_RJ", "bus_dt": "2025-08-29", "endpoint": "getGuestChecks"},
        {"store_id": "103_SP", "bus_dt": "2025-08-30", "endpoint": "getFiscalInvoice"},
        {"store_id": "104_MG", "bus_dt": "2025-08-31", "endpoint": "getGuestChecks"},
        {"store_id": "101_BSB", "bus_dt": "2025-09-01", "endpoint": "getFiscalInvoice"},
        {"store_id": "99_CB_CB", "bus_dt": "2025-09-02", "endpoint": "getGuestChecks"}
    ]

    if not SOURCE_DATA_PATH.exists():
        print(f"ERRO: Arquivo de origem não encontrado em '{SOURCE_DATA_PATH}'. Abortando.")
        return

    for sim in simulations:
        simulate_ingestion(
            source_file_path=SOURCE_DATA_PATH,
            store_id=sim["store_id"],
            business_date_str=sim["bus_dt"],
            endpoint=sim["endpoint"]
        )

    print("\n--- Simulação Finalizada ---")
    print(f"Verifique a estrutura de pastas criada em: '{LAKE_BASE_PATH}'")

if __name__ == "__main__":
    main()