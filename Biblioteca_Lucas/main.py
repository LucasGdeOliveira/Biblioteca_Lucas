import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime
import shutil

# Configurando os diretórios
BASE_DIR = Path('Livrarias Curitiba')
BACKUP_DIR = BASE_DIR / 'backups'
DATA_DIR = BASE_DIR / 'data'
EXPORT_DIR = BASE_DIR / 'exports'

# Criando o diretrório base para caso nao exista
BASE_DIR.mkdir(exist_ok=True)

# Criação de diretórios se não existirem
BACKUP_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# Conectando ao banco de dados SQLite
def connect_db():
    try:
        return sqlite3.connect(DATA_DIR / 'livraria.db')
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Criando tabela de livros
def create_table():
    with connect_db() as conn:
        if conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                ano_publicacao INTEGER NOT NULL,
                preco REAL NOT NULL
            )
            ''')
            conn.commit()

# Função para fazer backup do banco de dados
def backup_db():
    # Limpar backups antigos se houver mais de 5 antes de criar o novo
    clean_old_backups()
    
    # Cria backup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = BACKUP_DIR / f'backup_livraria_{timestamp}.db'
    shutil.copy(DATA_DIR / 'livraria.db', backup_file)

# Função para manter apenas os 5 backups mais recentes
def clean_old_backups():
    backups = sorted(BACKUP_DIR.glob('*.db'), key=os.path.getmtime)
    if len(backups) >= 5:
        os.remove(backups[0])  # Remove o backup mais antigo

# Função para adicionar um novo livro
def add_book(titulo, autor, ano_publicacao, preco):
    backup_db()  # Fazer backup antes de modificar
    with connect_db() as conn:
        if conn:
            conn.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                         (titulo, autor, ano_publicacao, preco))
            conn.commit()

# Função para exibir todos os livros
def display_books():
    with connect_db() as conn:
        if conn:
            cursor = conn.execute('SELECT * FROM livros')
            for row in cursor.fetchall():
                print(row)

# Função para atualizar preço de um livro
def update_price(book_id, new_price):
    backup_db()  # Fazer backup antes de modificar
    with connect_db() as conn:
        if conn:
            conn.execute('UPDATE livros SET preco = ? WHERE id = ?', (new_price, book_id))
            conn.commit()

# Função para remover um livro
def remove_book(book_id):
    backup_db()  # Fazer backup antes de modificar
    with connect_db() as conn:
        if conn:
            conn.execute('DELETE FROM livros WHERE id = ?', (book_id,))
            conn.commit()

# Função para buscar livros por autor
def search_by_author(author):
    with connect_db() as conn:
        if conn:
            cursor = conn.execute('SELECT * FROM livros WHERE autor = ?', (author,))
            for row in cursor.fetchall():
                print(row)

# Função para exportar dados para CSV
def export_to_csv():
    with connect_db() as conn:
        if conn:
            cursor = conn.execute('SELECT * FROM livros')
            with open(EXPORT_DIR / 'livros_exportados.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
                writer.writerows(cursor.fetchall())

# Função para importar dados de CSV
# caminho a ser digitado no menu para importar os dados CSV 'Livrarias Curitiba/exports/livros_exportados.csv'
def import_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Pular cabeçalho
        for row in reader:
            add_book(row[1], row[2], int(row[3]), float(row[4]))

# Menu principal
def main_menu():
    create_table()
    while True:
        print("\nMenu:")
        print("-----------------------")
        print("1. Adicionar novo livro")
        print("-------------------------")
        print("2. Exibir todos os livros")
        print("------------------------------")
        print("3. Atualizar preço de um livro")
        print("------------------------------")
        print("4. Remover um livro")
        print("-----------------------")
        print("5. Buscar livros por autor")
        print("--------------------------")
        print("6. Exportar dados para CSV")
        print("--------------------------")
        print("7. Importar dados de CSV")
        print("---------------------------------")
        print("8. Fazer backup do banco de dados")
        print("---------------------------------")
        print("9. Sair")
        print("-------")
        
        choice = input("Escolha uma opção: ")
        if choice == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de Publicação: "))
            preco = float(input("Preço: "))
            add_book(titulo, autor, ano_publicacao, preco)
        elif choice == '2':
            display_books()
        elif choice == '3':
            book_id = int(input("ID do livro: "))
            new_price = float(input("Novo Preço: "))
            update_price(book_id, new_price)
        elif choice == '4':
            book_id = int(input("ID do livro: "))
            remove_book(book_id)
        elif choice == '5':
            autor = input("Nome do autor: ")
            search_by_author(autor)
        elif choice == '6':
            export_to_csv()
            print("Dados exportados com sucesso!")
        elif choice == '7':
            csv_file = input("Caminho do arquivo CSV: ")
            import_from_csv(csv_file)
            print("Dados importados com sucesso!")
        elif choice == '8':
            backup_db()
            print("Backup realizado com sucesso!")
        elif choice == '9':
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main_menu()
