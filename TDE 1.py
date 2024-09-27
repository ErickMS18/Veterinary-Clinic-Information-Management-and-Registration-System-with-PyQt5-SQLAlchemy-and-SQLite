from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
import os

engine = create_engine('sqlite:///banco_TDE1.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
db_file = 'banco_TDE1.db'

if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Arquivo {db_file} excluído com sucesso.")
else:
    print(f"Arquivo {db_file} não encontrado.")


veterinario_Animais = Table("veterinario_Animais", Base.metadata,
    Column("veterinario_id", Integer, ForeignKey("Veterinario.id")),
    Column("animal_id", Integer, ForeignKey("Animal.id"))
)

class Dono(Base):
    __tablename__ = "Dono"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    endereco_cep = Column(String, nullable=False)
    endereco_rua = Column(String)
    endereco_cidade = Column(String)
    endereco_complemento = Column(String)
    animais = relationship("Animal", back_populates="dono")
    telefones = relationship("Telefone", back_populates="dono", cascade="all, delete-orphan")
    tipo = Column(String(50))  

    __mapper_args__ = {
        'polymorphic_identity': 'dono',
        'polymorphic_on': tipo
    }

class PessoaFisica(Dono):
    __tablename__ = "Pessoa_Fisica"
    id = Column(Integer, ForeignKey('Dono.id'), primary_key=True)
    cpf = Column(String, nullable=False)  

    __mapper_args__ = {
        'polymorphic_identity': 'pessoa_fisica',
    }

class ONG(Dono):
    __tablename__ = "ONG"
    id = Column(Integer, ForeignKey("Dono.id"), primary_key=True)
    cnpj = Column(String, nullable=False) 

    __mapper_args__ = {
        'polymorphic_identity': 'ong',
    }

class Telefone(Base):
    __tablename__ = "Telefone"
    id = Column(Integer, primary_key=True)
    numero = Column(String)
    dono_id = Column(Integer, ForeignKey("Dono.id"), nullable=False)
    dono = relationship("Dono", back_populates="telefones")

class Animal(Base):
    __tablename__ = "Animal"
    id = Column(Integer, primary_key=True)
    tratamentos_realizados = Column(String)
    historico_consultas = Column(String)
    dono_id = Column(Integer, ForeignKey("Dono.id"))
    dono = relationship('Dono', back_populates='animais')
    especie_id = Column(Integer, ForeignKey('Especie.id'))
    especie = relationship('Especie', back_populates='animais')
    veterinarios = relationship('Veterinario', secondary=veterinario_Animais, back_populates='animais')
    vacinas = relationship("Vacina", back_populates="animal", cascade="all, delete-orphan")

class Vacina(Base):
    __tablename__ = "Vacinas"
    id = Column(Integer, primary_key=True)
    doença = Column(String)
    prox_aplicacao = Column(String)
    animal_id = Column(Integer, ForeignKey("Animal.id"), nullable=False)
    animal = relationship("Animal", back_populates="vacinas")

class Veterinario(Base):
    __tablename__ = "Veterinario"
    id = Column(Integer, primary_key=True)
    especializacao = Column(String)
    numero_registro_profissional = Column(Integer, nullable=False)
    animais = relationship('Animal', secondary=veterinario_Animais, back_populates='veterinarios')

class Especie(Base):
    __tablename__ = "Especie"
    id = Column(Integer, primary_key=True)
    animais = relationship('Animal', back_populates='especie')


Base.metadata.create_all(engine)

# Menu CRUD
def menu():
    while True:
        print("\n===== MENU =====")
        print("1. Create (Adicionar nova pessoa física)")
        print("2. Read (Buscar pessoa física por CPF)")
        print("3. Update (Atualizar nome da pessoa física)")
        print("4. Delete (Deletar pessoa física)")
        print("5. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            create_pessoa_fisica()
        elif opcao == "2":
            read_pessoa_fisica()
        elif opcao == "3":
            update_pessoa_fisica()
        elif opcao == "4":
            delete_pessoa_fisica()
        elif opcao == "5":
            print("Encerrando o programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Funções CRUD

def create_pessoa_fisica():
    nome = input("Nome: ")
    
    endereco_cep = input("CEP: ")
    endereco_rua = input("Rua: ")
    endereco_cidade = input("Cidade: ")
    endereco_complemento = input("Complemento: ")
    cpf = input("CPF: ")

    telefones = []
    while True:
        telefone = input("Digite um número de telefone (ou pressione Enter para terminar): ")
        if telefone == "":
            break
        telefones.append(telefone)
    
    nova_pessoa_fisica = PessoaFisica(nome=nome, endereco_cep=endereco_cep, endereco_rua=endereco_rua,
                                      endereco_cidade=endereco_cidade, endereco_complemento=endereco_complemento, cpf=cpf)
    
    
    session.add(nova_pessoa_fisica)
    session.commit()

    
    for numero in telefones:
        novo_telefone = Telefone(numero=numero, dono=nova_pessoa_fisica)
        session.add(novo_telefone)
    
    
    session.commit()
    
    print("Pessoa Física e telefones adicionados com sucesso!")


def read_pessoa_fisica():
    cpf = input("Digite o CPF da pessoa física a ser buscada: ")
    
    pessoa_fisica = session.query(PessoaFisica)\
        .options(joinedload(PessoaFisica.telefones))\
        .filter(PessoaFisica.cpf == cpf).first()

    if pessoa_fisica:
        
        print(f"\n==o== Informações da Pessoa Física ==o==")
        print(f"Nome: {pessoa_fisica.nome}")  
        print(f"CPF: {pessoa_fisica.cpf}")
        print(f"CEP: {pessoa_fisica.endereco_cep}")  
        print(f"Rua: {pessoa_fisica.endereco_rua}") 
        print(f"Cidade: {pessoa_fisica.endereco_cidade}")  
        print(f"Complemento: {pessoa_fisica.endereco_complemento}") 

        
        if pessoa_fisica.telefones:
            print("\nTelefones:")
            for telefone in pessoa_fisica.telefones:
                print(f" - {telefone.numero}")
        else:
            print("\nNenhum telefone cadastrado.")
    else:
        print("Pessoa Física não encontrada.")

def update_pessoa_fisica():
    cpf = input("Digite o CPF da pessoa física a ser atualizada: ")
    pessoa_fisica = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf).first()

    if pessoa_fisica:
        print(f"\n==o== Informações Atuais da Pessoa Física ==o==")
        print(f"1. Nome: {pessoa_fisica.nome}")
        print(f"2. CPF: {pessoa_fisica.cpf}")
        print(f"3. CEP: {pessoa_fisica.endereco_cep}")
        print(f"4. Rua: {pessoa_fisica.endereco_rua}")
        print(f"5. Cidade: {pessoa_fisica.endereco_cidade}")
        print(f"6. Complemento: {pessoa_fisica.endereco_complemento}")
        
        # Listando telefones
        if pessoa_fisica.telefones:
            print("7. Telefone(s):")
            for i, telefone in enumerate(pessoa_fisica.telefones, 1):
                print(f"   {i}. {telefone.numero}")
        else:
            print("7. Nenhum telefone cadastrado.")

        escolha = input("\nDigite o número da informação que deseja alterar (1-7): ")

        if escolha == "1":
            novo_nome = input(f"Nome atual: {pessoa_fisica.nome}. Digite o novo nome: ")
            pessoa_fisica.nome = novo_nome
        elif escolha == "3":
            novo_cep = input(f"CEP atual: {pessoa_fisica.endereco_cep}. Digite o novo CEP: ")
            pessoa_fisica.endereco_cep = novo_cep
        elif escolha == "4":
            nova_rua = input(f"Rua atual: {pessoa_fisica.endereco_rua}. Digite a nova rua: ")
            pessoa_fisica.endereco_rua = nova_rua
        elif escolha == "5":
            nova_cidade = input(f"Cidade atual: {pessoa_fisica.endereco_cidade}. Digite a nova cidade: ")
            pessoa_fisica.endereco_cidade = nova_cidade
        elif escolha == "6":
            novo_complemento = input(f"Complemento atual: {pessoa_fisica.endereco_complemento}. Digite o novo complemento: ")
            pessoa_fisica.endereco_complemento = novo_complemento
        elif escolha == "7":
            if pessoa_fisica.telefones:
                for i, telefone in enumerate(pessoa_fisica.telefones, 1):
                    print(f"{i}. {telefone.numero}")
                telefone_escolhido = int(input("Selecione o número de telefone que deseja atualizar: ")) - 1
                novo_telefone = input(f"Telefone atual: {pessoa_fisica.telefones[telefone_escolhido].numero}. Digite o novo telefone: ")
                pessoa_fisica.telefones[telefone_escolhido].numero = novo_telefone
            else:
                print("Nenhum telefone cadastrado para atualizar.")
        else:
            print("Opção inválida. Nenhuma alteração foi feita.")
            return

        session.commit()
        print("Informação atualizada com sucesso!")
    else:
        print("Pessoa Física não encontrada.")


def delete_pessoa_fisica():
    cpf = input("Digite o CPF da pessoa física a ser deletada: ")
    pessoa_fisica = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf).first()

    if pessoa_fisica:
        session.delete(pessoa_fisica)
        session.commit()
        print("Pessoa Física deletada com sucesso.")
    else:
        print("Pessoa Física não encontrada.")


menu()

session.close()
