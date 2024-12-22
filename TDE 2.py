from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit, QMessageBox, QInputDialog, QComboBox, QDateEdit
from PyQt5.QtCore import QDate
from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, create_engine, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime


engine = create_engine('sqlite:///clinica_vet.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

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
    nome = Column(String, nullable=False)
    tratamentos_realizados = Column(String)
    historico_consultas = Column(String)
    data_nasc = Column(Date, nullable=True)


    dono_id = Column(Integer, ForeignKey("Dono.id"))
    dono = relationship('Dono', back_populates='animais')

    especie_id = Column(Integer, ForeignKey('Especie.id'))
    especie = relationship('Especie', back_populates='animais')

    consultas = relationship("Consulta", back_populates="animal", cascade="all, delete-orphan")

    veterinarios = relationship('Veterinario', secondary=veterinario_Animais, back_populates='animais')

    vacinas = relationship("Vacina", back_populates="animal", cascade="all, delete-orphan")

class Vacina(Base):
    __tablename__ = "Vacinas"
    
    
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)  
    nome = Column(String, nullable=False)  
    data_aplicacao = Column(Date, nullable=False)  
    prox_aplicacao = Column(Date, nullable=True)  

    
    animal_id = Column(Integer, ForeignKey("Animal.id"), nullable=False)
    animal = relationship("Animal", back_populates="vacinas")

class Consulta(Base):
    __tablename__ = "Consulta"

    id = Column(Integer, primary_key=True)
    data_consulta = Column(Date, nullable=False)
    descricao = Column(Text, nullable=True)  

    animal_id = Column(Integer, ForeignKey("Animal.id"), nullable=False)
    animal = relationship("Animal", back_populates="consultas")

    
    veterinario_id = Column(Integer, ForeignKey("Veterinario.id"), nullable=False)
    veterinario = relationship("Veterinario", back_populates="consultas")


class Veterinario(Base):
    __tablename__ = "Veterinario"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False) 
    especializacao = Column(String)
    numero_reg_prof = Column(Integer, nullable=False)

    animais = relationship('Animal', secondary=veterinario_Animais, back_populates='veterinarios')
    consultas = relationship("Consulta", back_populates="veterinario", cascade="all, delete-orphan")



class Especie(Base):
    __tablename__ = "Especie"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    subespecie = Column(String, nullable=False)

    animais = relationship('Animal', back_populates='especie')


Base.metadata.create_all(engine)

# INTERFACE GRÀFICA

class MenuPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu Principal")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        self.btn_pessoa_fisica = QPushButton("Pessoa Física")
        self.btn_ong = QPushButton("ONG")
        self.btn_animal = QPushButton("Animal")
        self.btn_especie = QPushButton("Espécie")
        self.btn_consulta = QPushButton("Consulta")
        self.btn_veterinario = QPushButton("Veterinário")
        self.btn_vacinas = QPushButton("Vacinas")
        self.btn_sair = QPushButton("Sair")

        layout.addWidget(self.btn_pessoa_fisica)
        layout.addWidget(self.btn_ong)
        layout.addWidget(self.btn_animal)
        layout.addWidget(self.btn_especie)
        layout.addWidget(self.btn_consulta)
        layout.addWidget(self.btn_veterinario)
        layout.addWidget(self.btn_vacinas)
        layout.addWidget(self.btn_sair)

        self.setLayout(layout)

        self.btn_pessoa_fisica.clicked.connect(self.open_menu_pessoa_fisica)
        self.btn_ong.clicked.connect(self.open_menu_ong)
        self.btn_animal.clicked.connect(self.open_menu_animal)  
        self.btn_especie.clicked.connect(self.open_menu_especie)
        self.btn_consulta.clicked.connect(self.open_menu_consulta)
        self.btn_veterinario.clicked.connect(self.open_menu_veterinario)
        self.btn_vacinas.clicked.connect(self.open_menu_vacinas)
        self.btn_sair.clicked.connect(self.close)

    def open_menu_pessoa_fisica(self):
        self.open_menu("Pessoa Física", self.create_pessoa_fisica, self.read_pessoa_fisica, self.update_pessoa_fisica, self.delete_pessoa_fisica)

    def open_menu_ong(self):
        self.open_menu("ONG", self.create_ong, self.read_ong, self.update_ong, self.delete_ong)

    def open_menu_animal(self):  
        self.open_menu("Animal", self.create_animal, self.read_animal, self.update_animal, self.delete_animal)
    
    def open_menu_especie(self):
        self.open_menu("Espécie", self.create_especie, self.read_especie, self.update_especie, self.delete_especie)

    def open_menu_consulta(self):
        self.open_menu("Consulta", self.create_consulta, self.read_consulta, self.update_consulta, self.delete_consulta)

    def open_menu_veterinario(self):
        self.open_menu("Veterinário", self.create_veterinario, self.read_veterinario, self.update_veterinario, self.delete_veterinario)

    def open_menu_vacinas(self):
        self.open_menu("Vacinas", self.create_vacina, self.read_vacina, self.update_vacina, self.delete_vacina)


    def open_menu(self, title, create_func, read_func, update_func, delete_func):
        menu_window = QDialog(self)
        menu_window.setWindowTitle(f"Menu CRUD - {title}")
        menu_window.setGeometry(150, 150, 250, 300)

        layout = QVBoxLayout()

        btn_create = QPushButton(f"Adicionar {title}")
        btn_read = QPushButton(f"Buscar {title}")
        btn_update = QPushButton(f"Atualizar {title}")
        btn_delete = QPushButton(f"Deletar {title}")
        btn_back = QPushButton("Voltar")

        layout.addWidget(btn_create)
        layout.addWidget(btn_read)
        layout.addWidget(btn_update)
        layout.addWidget(btn_delete)
        layout.addWidget(btn_back)

        menu_window.setLayout(layout)

        btn_create.clicked.connect(lambda: self.handle_create(create_func, menu_window))
        btn_read.clicked.connect(lambda: self.handle_read(read_func, menu_window))
        btn_update.clicked.connect(lambda: self.handle_update(update_func, menu_window))  
        btn_delete.clicked.connect(lambda: self.handle_delete(delete_func, menu_window))  
        btn_back.clicked.connect(menu_window.close)

        menu_window.exec_()

    def handle_create(self, create_func, menu_window):
        try:
            create_func(menu_window)  
            QMessageBox.information(menu_window, "Sucesso", f"{create_func.__name__.replace('_', ' ').title()} criado com sucesso!")
            menu_window.close()  
        except Exception as e:
            QMessageBox.critical(menu_window, "Erro", f"Ocorreu um erro: {e}")

    def handle_read(self, read_func, menu_window):
        try:
            read_func(menu_window)
        except Exception as e:
            QMessageBox.critical(menu_window, "Erro", f"Ocorreu um erro ao buscar: {e}")

    def handle_update(self, update_func, menu_window):
        try:
            update_func()
            QMessageBox.information(self, "Sucesso", f"{update_func.__name__.replace('_', ' ').title()} atualizado com sucesso!")
            menu_window.close() 
        except Exception as e:
            QMessageBox.critical(menu_window, "Erro", f"Ocorreu um erro: {e}")

    def handle_delete(self, delete_func, menu_window):
        try:
            delete_func()
            QMessageBox.information(self, "Sucesso", "Registro deletado com sucesso.")
            menu_window.close() 
        except Exception as e:
            QMessageBox.critical(menu_window, "Erro", f"Ocorreu um erro: {e}")


# CRUD Pessoa Física
    def create_pessoa_fisica(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar Pessoa Física")
        create_window.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("CPF")
        self.cep_input = QLineEdit()
        self.cep_input.setPlaceholderText("CEP")
        self.rua_input = QLineEdit()
        self.rua_input.setPlaceholderText("Rua")
        self.cidade_input = QLineEdit()
        self.cidade_input.setPlaceholderText("Cidade")
        self.complemento_input = QLineEdit()
        self.complemento_input.setPlaceholderText("Complemento")
        self.telefones_input = QLineEdit()
        self.telefones_input.setPlaceholderText("Telefones (separados por vírgula)")

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(self.nome_input)
        layout.addWidget(self.cpf_input)
        layout.addWidget(self.cep_input)
        layout.addWidget(self.rua_input)
        layout.addWidget(self.cidade_input)
        layout.addWidget(self.complemento_input)
        layout.addWidget(self.telefones_input)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_pessoa_fisica(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_pessoa_fisica(self, window):
        nome = self.nome_input.text()
        cpf = self.cpf_input.text()
        cep = self.cep_input.text()
        rua = self.rua_input.text()
        cidade = self.cidade_input.text()
        complemento = self.complemento_input.text()
        telefones = self.telefones_input.text().split(',')  

        
        nova_pessoa_fisica = PessoaFisica(
            nome=nome, 
            cpf=cpf, 
            endereco_cep=cep, 
            endereco_rua=rua, 
            endereco_cidade=cidade, 
            endereco_complemento=complemento
        )
        
        session.add(nova_pessoa_fisica)
        session.commit()

        
        for numero in telefones:
            novo_telefone = Telefone(numero=numero.strip(), dono=nova_pessoa_fisica)
            session.add(novo_telefone)
        
        session.commit()

        
        QMessageBox.information(window, "Sucesso", "Pessoa Física adicionada com sucesso!")
        window.close()

    def read_pessoa_fisica(self, parent_window):
        cpf, ok = QInputDialog.getText(self, "Buscar Pessoa Física", "Digite o CPF da pessoa física:")
        
        if ok and cpf:
            pessoa = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf).first()
            read_window = QDialog(parent_window)
            read_window.setWindowTitle("Pessoa Física")
            layout = QVBoxLayout()

            if pessoa:
                layout.addWidget(QLabel(f"Nome: {pessoa.nome}"))
                layout.addWidget(QLabel(f"CPF: {pessoa.cpf}"))
                layout.addWidget(QLabel(f"CEP: {pessoa.endereco_cep}"))
                layout.addWidget(QLabel(f"Rua: {pessoa.endereco_rua}"))
                layout.addWidget(QLabel(f"Cidade: {pessoa.endereco_cidade}"))
                layout.addWidget(QLabel(f"Complemento: {pessoa.endereco_complemento}"))
                telefones_str = ', '.join([t.numero for t in pessoa.telefones]) if pessoa.telefones else 'Nenhum telefone'
                layout.addWidget(QLabel(f"Telefones: {telefones_str}"))
            else:
                layout.addWidget(QLabel("Pessoa Física não encontrada."))

            read_window.setLayout(layout)
            read_window.exec_()

    def update_pessoa_fisica(self):
        cpf, ok = QInputDialog.getText(self, "Atualizar Pessoa Física", "Digite o CPF da pessoa física a ser atualizada:")
        if ok and cpf:
            pessoa_fisica = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf).first()

            if pessoa_fisica:
                atributos = [
                    "Nome",
                    "CEP",
                    "Rua",
                    "Cidade",
                    "Complemento",
                    "Telefones"
                ]
                
                atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                if ok_atributo and atributo:
                    if atributo == "Nome":
                        novo_nome, ok_nome = QInputDialog.getText(self, "Atualizar Nome", "Nome atual: {}. Digite o novo nome (ou deixe em branco para manter):".format(pessoa_fisica.nome))
                        if ok_nome and novo_nome:
                            pessoa_fisica.nome = novo_nome

                    elif atributo == "CEP":
                        novo_cep, ok_cep = QInputDialog.getText(self, "Atualizar CEP", "CEP atual: {}. Digite o novo CEP (ou deixe em branco para manter):".format(pessoa_fisica.endereco_cep))
                        if ok_cep and novo_cep:
                            pessoa_fisica.endereco_cep = novo_cep

                    elif atributo == "Rua":
                        nova_rua, ok_rua = QInputDialog.getText(self, "Atualizar Rua", "Rua atual: {}. Digite a nova rua (ou deixe em branco para manter):".format(pessoa_fisica.endereco_rua))
                        if ok_rua and nova_rua:
                            pessoa_fisica.endereco_rua = nova_rua

                    elif atributo == "Cidade":
                        nova_cidade, ok_cidade = QInputDialog.getText(self, "Atualizar Cidade", "Cidade atual: {}. Digite a nova cidade (ou deixe em branco para manter):".format(pessoa_fisica.endereco_cidade))
                        if ok_cidade and nova_cidade:
                            pessoa_fisica.endereco_cidade = nova_cidade

                    elif atributo == "Complemento":
                        novo_complemento, ok_complemento = QInputDialog.getText(self, "Atualizar Complemento", "Complemento atual: {}. Digite o novo complemento (ou deixe em branco para manter):".format(pessoa_fisica.endereco_complemento))
                        if ok_complemento and novo_complemento:
                            pessoa_fisica.endereco_complemento = novo_complemento

                    elif atributo == "Telefones":
                        novos_telefones, ok_telefones = QInputDialog.getText(self, "Atualizar Telefones", "Telefones atuais: {}. Digite os novos telefones (separados por vírgula) (ou deixe em branco para manter):".format(', '.join([t.numero for t in pessoa_fisica.telefones])))
                        if ok_telefones and novos_telefones:
                            pessoa_fisica.telefones.clear()
                            for telefone in novos_telefones.split(','):
                                novo_telefone = Telefone(numero=telefone.strip())
                                pessoa_fisica.telefones.append(novo_telefone)
                session.commit()
                QMessageBox.information(self, "Sucesso", "Informação atualizada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Pessoa Física não encontrada.")

    def delete_pessoa_fisica(self):
        cpf, ok = QInputDialog.getText(self, "Deletar Pessoa Física", "Digite o CPF da pessoa física a ser deletada:")
        if ok and cpf:
            pessoa_fisica = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf).first()

            if pessoa_fisica:
                session.delete(pessoa_fisica)
                session.commit()
                QMessageBox.information(self, "Sucesso", "Pessoa Física deletada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Pessoa Física não encontrada.")

# CRUD ONG
    def create_ong(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar ONG")
        create_window.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setPlaceholderText("CNPJ")
        self.cep_input = QLineEdit()
        self.cep_input.setPlaceholderText("CEP")
        self.rua_input = QLineEdit()
        self.rua_input.setPlaceholderText("Rua")
        self.cidade_input = QLineEdit()
        self.cidade_input.setPlaceholderText("Cidade")
        self.complemento_input = QLineEdit()
        self.complemento_input.setPlaceholderText("Complemento")
        self.telefones_input = QLineEdit()
        self.telefones_input.setPlaceholderText("Telefones (separados por vírgula)")

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(self.nome_input)
        layout.addWidget(self.cnpj_input)
        layout.addWidget(self.cep_input)
        layout.addWidget(self.rua_input)
        layout.addWidget(self.cidade_input)
        layout.addWidget(self.complemento_input)
        layout.addWidget(self.telefones_input)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_ong(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_ong(self, window):
        nome = self.nome_input.text()
        cnpj = self.cnpj_input.text()
        cep = self.cep_input.text()
        rua = self.rua_input.text()
        cidade = self.cidade_input.text()
        complemento = self.complemento_input.text()
        telefones = self.telefones_input.text().split(',')  

        nova_ong = ONG(
            nome=nome, 
            cnpj=cnpj, 
            endereco_cep=cep, 
            endereco_rua=rua, 
            endereco_cidade=cidade, 
            endereco_complemento=complemento
        )
        
        session.add(nova_ong)
        session.commit()

        for numero in telefones:
            novo_telefone = Telefone(numero=numero.strip(), dono=nova_ong)
            session.add(novo_telefone)
        
        session.commit()

        QMessageBox.information(window, "Sucesso", "ONG adicionada com sucesso!")
        window.close()

    def read_ong(self, parent_window):
        cnpj, ok = QInputDialog.getText(self, "Buscar ONG", "Digite o CNPJ da ONG:")
        
        if ok and cnpj:
            ong = session.query(ONG).filter(ONG.cnpj == cnpj).first()
            read_window = QDialog(parent_window)
            read_window.setWindowTitle("ONG")
            layout = QVBoxLayout()

            if ong:
                layout.addWidget(QLabel(f"Nome: {ong.nome}"))
                layout.addWidget(QLabel(f"CNPJ: {ong.cnpj}"))
                layout.addWidget(QLabel(f"CEP: {ong.endereco_cep}"))
                layout.addWidget(QLabel(f"Rua: {ong.endereco_rua}"))
                layout.addWidget(QLabel(f"Cidade: {ong.endereco_cidade}"))
                layout.addWidget(QLabel(f"Complemento: {ong.endereco_complemento}"))
                telefones_str = ', '.join([t.numero for t in ong.telefones]) if ong.telefones else 'Nenhum telefone'
                layout.addWidget(QLabel(f"Telefones: {telefones_str}"))
            else:
                layout.addWidget(QLabel("ONG não encontrada."))

            read_window.setLayout(layout)
            read_window.exec_()

    def update_ong(self):
        cnpj, ok = QInputDialog.getText(self, "Atualizar ONG", "Digite o CNPJ da ONG a ser atualizada:")
        if ok and cnpj:
            ong = session.query(ONG).filter(ONG.cnpj == cnpj).first()

            if ong:
                atributos = [
                    "Nome",
                    "CEP",
                    "Rua",
                    "Cidade",
                    "Complemento",
                    "Telefones"
                ]
                
                atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                if ok_atributo and atributo:
                    if atributo == "Nome":
                        novo_nome, ok_nome = QInputDialog.getText(self, "Atualizar Nome", "Nome atual: {}. Digite o novo nome (ou deixe em branco para manter):".format(ong.nome))
                        if ok_nome and novo_nome:
                            ong.nome = novo_nome

                    elif atributo == "CEP":
                        novo_cep, ok_cep = QInputDialog.getText(self, "Atualizar CEP", "CEP atual: {}. Digite o novo CEP (ou deixe em branco para manter):".format(ong.endereco_cep))
                        if ok_cep and novo_cep:
                            ong.endereco_cep = novo_cep

                    elif atributo == "Rua":
                        nova_rua, ok_rua = QInputDialog.getText(self, "Atualizar Rua", "Rua atual: {}. Digite a nova rua (ou deixe em branco para manter):".format(ong.endereco_rua))
                        if ok_rua and nova_rua:
                            ong.endereco_rua = nova_rua

                    elif atributo == "Cidade":
                        nova_cidade, ok_cidade = QInputDialog.getText(self, "Atualizar Cidade", "Cidade atual: {}. Digite a nova cidade (ou deixe em branco para manter):".format(ong.endereco_cidade))
                        if ok_cidade and nova_cidade:
                            ong.endereco_cidade = nova_cidade

                    elif atributo == "Complemento":
                        novo_complemento, ok_complemento = QInputDialog.getText(self, "Atualizar Complemento", "Complemento atual: {}. Digite o novo complemento (ou deixe em branco para manter):".format(ong.endereco_complemento))
                        if ok_complemento and novo_complemento:
                            ong.endereco_complemento = novo_complemento

                    elif atributo == "Telefones":
                        novos_telefones, ok_telefones = QInputDialog.getText(self, "Atualizar Telefones", "Telefones atuais: {}. Digite os novos telefones (separados por vírgula) (ou deixe em branco para manter):".format(', '.join([t.numero for t in ong.telefones])))

                        if ok_telefones and novos_telefones:
                            ong.telefones.clear()
                            for telefone in novos_telefones.split(','):
                                novo_telefone = Telefone(numero=telefone.strip())
                                ong.telefones.append(novo_telefone)

                
                session.commit()
                QMessageBox.information(self, "Sucesso", "Informação atualizada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "ONG não encontrada.")

    def delete_ong(self):
        cnpj, ok = QInputDialog.getText(self, "Deletar ONG", "Digite o CNPJ da ONG a ser deletada:")
        if ok and cnpj:
            ong = session.query(ONG).filter(ONG.cnpj == cnpj).first()

            if ong:
                session.delete(ong)
                session.commit()
                QMessageBox.information(self, "Sucesso", "ONG deletada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "ONG não encontrada.")


# CRUD Especie
    def create_especie(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar Espécie")
        create_window.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome da Espécie")
        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Descrição")
        self.subespecie_input = QLineEdit()
        self.subespecie_input.setPlaceholderText("Subespécie")

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(self.nome_input)
        layout.addWidget(self.descricao_input)
        layout.addWidget(self.subespecie_input)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_especie(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_especie(self, window):
        nome = self.nome_input.text()
        descricao = self.descricao_input.text()
        subespecie = self.subespecie_input.text()

        nova_especie = Especie(
            nome=nome,
            descricao=descricao,
            subespecie=subespecie
        )
        
        session.add(nova_especie)
        session.commit()

        QMessageBox.information(window, "Sucesso", "Espécie adicionada com sucesso!")
        window.close()

    def read_especie(self, parent_window):
        especies = session.query(Especie).all()

        read_window = QDialog(parent_window)
        read_window.setWindowTitle("Lista de Espécies")
        layout = QVBoxLayout()

        if especies:
            for especie in especies:
                layout.addWidget(QLabel(f"Nome: {especie.nome}"))
                layout.addWidget(QLabel(f"Descrição: {especie.descricao}"))
                layout.addWidget(QLabel(f"Subespécie: {especie.subespecie}"))
                layout.addWidget(QLabel("------------------------"))
        else:
            layout.addWidget(QLabel("Nenhuma espécie encontrada."))

        read_window.setLayout(layout)
        read_window.exec_()


    def update_especie(self):
        nome, ok = QInputDialog.getText(self, "Atualizar Espécie", "Digite o nome da espécie a ser atualizada:")
        if ok and nome:
            especie = session.query(Especie).filter(Especie.nome == nome).first()

            if especie:
                atributos = [
                    "Nome",
                    "Descrição",
                    "Subespécie"
                ]
                
                atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                if ok_atributo and atributo:
                    if atributo == "Nome":
                        novo_nome, ok_nome = QInputDialog.getText(self, "Atualizar Nome", f"Nome atual: {especie.nome}. Digite o novo nome (ou deixe em branco para manter):")
                        if ok_nome and novo_nome:
                            especie.nome = novo_nome

                    elif atributo == "Descrição":
                        nova_descricao, ok_descricao = QInputDialog.getText(self, "Atualizar Descrição", f"Descrição atual: {especie.descricao}. Digite a nova descrição (ou deixe em branco para manter):")
                        if ok_descricao and nova_descricao:
                            especie.descricao = nova_descricao

                    elif atributo == "Subespécie":
                        nova_subespecie, ok_subespecie = QInputDialog.getText(self, "Atualizar Subespécie", f"Subespécie atual: {especie.subespecie}. Digite a nova subespécie (ou deixe em branco para manter):")
                        if ok_subespecie and nova_subespecie:
                            especie.subespecie = nova_subespecie

                session.commit()
                QMessageBox.information(self, "Sucesso", "Informação atualizada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Espécie não encontrada.")

    def delete_especie(self):
        nome, ok = QInputDialog.getText(self, "Deletar Espécie", "Digite o nome da espécie a ser deletada:")
        if ok and nome:
            especie = session.query(Especie).filter(Especie.nome == nome).first()

            if especie:
                session.delete(especie)
                session.commit()
                QMessageBox.information(self, "Sucesso", "Espécie deletada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Espécie não encontrada.")


# CRUD Vacina 
    def create_vacina(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar Vacina")
        create_window.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome da Vacina")
        self.status_input = QLineEdit()
        self.status_input.setPlaceholderText("Status da Vacina")
        self.data_aplicacao_input = QLineEdit()
        self.data_aplicacao_input.setPlaceholderText("Data de Aplicação (YYYY-MM-DD)")
        self.prox_aplicacao_input = QLineEdit()
        self.prox_aplicacao_input.setPlaceholderText("Próxima Aplicação (YYYY-MM-DD, opcional)")
        self.animal_nome_input = QLineEdit()
        self.animal_nome_input.setPlaceholderText("Nome do Animal")

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(self.nome_input)
        layout.addWidget(self.status_input)
        layout.addWidget(self.data_aplicacao_input)
        layout.addWidget(self.prox_aplicacao_input)
        layout.addWidget(self.animal_nome_input)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_vacina(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_vacina(self, window):
        nome = self.nome_input.text()
        status = self.status_input.text()
        data_aplicacao_input = self.data_aplicacao_input.text()
        prox_aplicacao_input = self.prox_aplicacao_input.text()
        animal_nome = self.animal_nome_input.text()

        try:
            data_aplicacao = datetime.strptime(data_aplicacao_input, '%Y-%m-%d').date() if data_aplicacao_input else None
        except ValueError:
            QMessageBox.warning(window, "Erro", "Formato de data inválido para a aplicação. Use YYYY-MM-DD.")
            return

        prox_aplicacao = None
        if prox_aplicacao_input:
            try:
                prox_aplicacao = datetime.strptime(prox_aplicacao_input, '%Y-%m-%d').date()
            except ValueError:
                QMessageBox.warning(window, "Erro", "Formato de data inválido para a próxima aplicação. Use YYYY-MM-DD.")
                return

        animal = session.query(Animal).filter(Animal.nome == animal_nome).first()
        if not animal:
            QMessageBox.warning(window, "Erro", "Animal não encontrado.")
            return

        nova_vacina = Vacina(
            nome=nome,
            status=status,
            data_aplicacao=data_aplicacao,
            prox_aplicacao=prox_aplicacao,
            animal_id=animal.id
        )

        session.add(nova_vacina)
        session.commit()

        QMessageBox.information(window, "Sucesso", "Vacina criada com sucesso!")
        window.close()

    def read_vacina(self, parent_window):
        dono_nome_cpf = QInputDialog.getText(parent_window, "Consultar Vacinas", "Digite o nome ou CPF do dono:")
        if not dono_nome_cpf[1]:  
            return

        dono = session.query(PessoaFisica).filter((PessoaFisica.nome == dono_nome_cpf[0]) | (PessoaFisica.cpf == dono_nome_cpf[0])).first()

        if not dono:
            QMessageBox.warning(parent_window, "Erro", "Dono não encontrado.")
            return
        
        animais = session.query(Animal).filter(Animal.dono_id == dono.id).all()

        if not animais:
            QMessageBox.warning(parent_window, "Erro", "Nenhum animal encontrado para este dono.")
            return

        animal_selection_window = QDialog(parent_window)
        animal_selection_window.setWindowTitle("Selecionar Animal")
        layout = QVBoxLayout()

        self.animal_combobox = QComboBox()
        self.animal_combobox.addItems([animal.nome for animal in animais])

        layout.addWidget(QLabel("Selecione o Animal:"))
        layout.addWidget(self.animal_combobox)

        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.clicked.connect(lambda: self.confirmar_animal_selection(animal_selection_window, dono))
        layout.addWidget(btn_confirmar)

        animal_selection_window.setLayout(layout)
        animal_selection_window.exec_()

    def confirmar_animal_selection(self, animal_selection_window, dono):
        animal_nome_selecionado = self.animal_combobox.currentText()
        animal = session.query(Animal).filter(Animal.nome == animal_nome_selecionado, Animal.dono_id == dono.id).first()

        if animal:
            vacinas = session.query(Vacina).filter(Vacina.animal_id == animal.id).all()

            read_window = QDialog(animal_selection_window)
            read_window.setWindowTitle("Lista de Vacinas")
            layout = QVBoxLayout()

            if vacinas:
                for vacina in vacinas:
                    layout.addWidget(QLabel(f"\n==o== Vacina ID: {vacina.id} ==o=="))
                    layout.addWidget(QLabel(f"Nome: {vacina.nome}"))
                    layout.addWidget(QLabel(f"Status: {vacina.status}"))
                    layout.addWidget(QLabel(f"Data de Aplicação: {vacina.data_aplicacao}"))
                    layout.addWidget(QLabel(f"Próxima Aplicação: {vacina.prox_aplicacao if vacina.prox_aplicacao else 'Não especificada'}"))
                    layout.addWidget(QLabel("------------------------"))
            else:
                layout.addWidget(QLabel("Nenhuma vacina encontrada para este animal."))

            read_window.setLayout(layout)
            read_window.exec_()
        else:
            QMessageBox.warning(animal_selection_window, "Erro", "Animal não encontrado.")



    def update_vacina(self):
        dono_nome_cpf, ok = QInputDialog.getText(self, "Atualizar Vacina", "Digite o nome ou CPF do dono:")
        if ok and dono_nome_cpf:
            dono = session.query(PessoaFisica).filter((PessoaFisica.nome == dono_nome_cpf) | (PessoaFisica.cpf == dono_nome_cpf)).first()

            if dono:
                animais_dono = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if not animais_dono:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para este dono.")
                    return
                animal_nomes = [animal.nome for animal in animais_dono]
                animal_nome, ok_animal = QInputDialog.getItem(self, "Escolher Animal", "Escolha o animal:", animal_nomes, 0, False)

                if ok_animal and animal_nome:
                    animal_selecionado = next(animal for animal in animais_dono if animal.nome == animal_nome)
                    vacinas = session.query(Vacina).filter(Vacina.animal_id == animal_selecionado.id).all()

                    if not vacinas:
                        QMessageBox.warning(self, "Erro", "Nenhuma vacina encontrada para este animal.")
                        return
                    vacina_ids = [str(vacina.id) for vacina in vacinas]
                    vacina_id, ok_vacina = QInputDialog.getItem(self, "Escolher Vacina", "Escolha a vacina a ser atualizada:", vacina_ids, 0, False)

                    if ok_vacina and vacina_id:
                        vacina = session.query(Vacina).filter(Vacina.id == vacina_id).first()

                        if vacina:
                            atributos = [
                                "Nome",
                                "Status",
                                "Data de Aplicação",
                                "Próxima Aplicação"
                            ]

                            atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                            if ok_atributo and atributo:
                                if atributo == "Nome":
                                    novo_nome, ok_nome = QInputDialog.getText(self, "Atualizar Nome", f"Nome atual: {vacina.nome}. Digite o novo nome (ou deixe em branco para manter):")
                                    if ok_nome:
                                        vacina.nome = novo_nome or vacina.nome

                                elif atributo == "Status":
                                    novo_status, ok_status = QInputDialog.getText(self, "Atualizar Status", f"Status atual: {vacina.status}. Digite o novo status (ou deixe em branco para manter):")
                                    if ok_status:
                                        vacina.status = novo_status or vacina.status

                                elif atributo == "Data de Aplicação":
                                    nova_data_aplicacao = QDateEdit()
                                    nova_data_aplicacao.setDisplayFormat("yyyy-MM-dd")
                                    nova_data_aplicacao.setDate(vacina.data_aplicacao)  
                                    nova_data_aplicacao_input = QInputDialog.getText(self, "Atualizar Data de Aplicação", f"Data de aplicação atual: {vacina.data_aplicacao}. Escolha uma nova data (ou deixe em branco para manter):", QLineEdit.Normal, nova_data_aplicacao.text())
                                    if nova_data_aplicacao_input[1]:  
                                        try:
                                            vacina.data_aplicacao = nova_data_aplicacao.date().toPyDate()  
                                        except ValueError:
                                            QMessageBox.warning(self, "Erro", "Formato de data inválido. Mantendo a data anterior.")

                                elif atributo == "Próxima Aplicação":
                                    nova_prox_aplicacao = QDateEdit()
                                    nova_prox_aplicacao.setDisplayFormat("yyyy-MM-dd")
                                    nova_prox_aplicacao.setDate(vacina.prox_aplicacao) 
                                    nova_prox_aplicacao_input = QInputDialog.getText(self, "Atualizar Próxima Aplicação", f"Próxima aplicação atual: {vacina.prox_aplicacao}. Escolha uma nova data (ou deixe em branco para manter):", QLineEdit.Normal, nova_prox_aplicacao.text())
                                    if nova_prox_aplicacao_input[1]:  
                                        try:
                                            vacina.prox_aplicacao = nova_prox_aplicacao.date().toPyDate()  
                                        except ValueError:
                                            QMessageBox.warning(self, "Erro", "Formato de data inválido. Mantendo a data anterior.")

                            session.commit()
                            QMessageBox.information(self, "Sucesso", "Vacina atualizada com sucesso!")
                        else:
                            QMessageBox.warning(self, "Erro", "Vacina não encontrada.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado.")



    def delete_vacina(self):
        dono_nome_cpf, ok = QInputDialog.getText(self, "Deletar Vacina", "Digite o nome ou CPF do dono:")
        if ok and dono_nome_cpf:
            dono = session.query(PessoaFisica).filter((PessoaFisica.nome == dono_nome_cpf) | (PessoaFisica.cpf == dono_nome_cpf)).first()

            if dono:
                
                animais_dono = session.query(Animal).filter(Animal.dono_id == dono.id).all()
                if not animais_dono:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para este dono.")
                    return
                animal_nomes = [animal.nome for animal in animais_dono]
                animal_nome, ok_animal = QInputDialog.getItem(self, "Escolher Animal", "Escolha o animal:", animal_nomes, 0, False)

                if ok_animal and animal_nome:
                    animal_selecionado = next(animal for animal in animais_dono if animal.nome == animal_nome)
                    vacinas = session.query(Vacina).filter(Vacina.animal_id == animal_selecionado.id).all()

                    if not vacinas:
                        QMessageBox.warning(self, "Erro", "Nenhuma vacina encontrada para este animal.")
                        return
                    vacina_ids = [str(vacina.id) for vacina in vacinas]
                    vacina_id, ok_vacina = QInputDialog.getItem(self, "Escolher Vacina", "Escolha a vacina a ser deletada:", vacina_ids, 0, False)

                    if ok_vacina and vacina_id:
                        vacina = session.query(Vacina).filter(Vacina.id == vacina_id).first()

                        if vacina:
                            session.delete(vacina)
                            session.commit()
                            QMessageBox.information(self, "Sucesso", "Vacina deletada com sucesso!")
                        else:
                            QMessageBox.warning(self, "Erro", "Vacina não encontrada.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado.")



# CRUD Animal
    def create_animal(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar Animal")
        create_window.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        
        self.data_nasc_input = QLineEdit()
        self.data_nasc_input.setPlaceholderText("Data de Nascimento (AAAA-MM-DD)")
        
        self.tratamentos_input = QLineEdit()
        self.tratamentos_input.setPlaceholderText("Tratamentos Realizados")
        
        self.especie_combobox = QComboBox()
        self.especie_combobox.addItems([e.nome for e in session.query(Especie).all()])  
        
        self.dono_combobox = QComboBox()
        self.dono_combobox.addItems([f"{d.nome} - {d.cpf}" for d in session.query(PessoaFisica).all()])  

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(self.nome_input)
        layout.addWidget(self.data_nasc_input)
        layout.addWidget(self.tratamentos_input)
        layout.addWidget(QLabel("Espécie:"))
        layout.addWidget(self.especie_combobox)
        layout.addWidget(QLabel("Dono:"))
        layout.addWidget(self.dono_combobox)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_animal(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_animal(self, window):
        nome = self.nome_input.text()
        data_nasc_str = self.data_nasc_input.text()
        tratamentos = self.tratamentos_input.text()
        
        especie_nome = self.especie_combobox.currentText()
        dono_nome = self.dono_combobox.currentText().split(" - ")[-1]  

        especie = session.query(Especie).filter(Especie.nome == especie_nome).first()
        dono = session.query(PessoaFisica).filter(PessoaFisica.cpf == dono_nome).first()
        data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date() if data_nasc_str else None

        novo_animal = Animal(
            nome=nome,
            data_nasc=data_nasc,
            tratamentos_realizados=tratamentos,
            especie=especie,
            dono=dono
        )
        
        session.add(novo_animal)
        session.commit()

        QMessageBox.information(window, "Sucesso", "Animal adicionado com sucesso!")
        window.close()

    def read_animal(self, parent_window):
        cpf_cnpj, ok = QInputDialog.getText(self, "Buscar Animal", "Digite o CPF ou CNPJ do cliente:")

        if ok and cpf_cnpj:
            if len(cpf_cnpj) == 11:  # CPF
                dono = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_cnpj).first()
            elif len(cpf_cnpj) == 14:  # CNPJ
                dono = session.query(ONG).filter(ONG.cnpj == cpf_cnpj).first()
            else:
                QMessageBox.warning(self, "Erro", "Digite um CPF (11 dígitos) ou um CNPJ (14 dígitos) válidos.")
                return

            if dono:
                animals = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if animals:
                    animal_names = [animal.nome for animal in animals]
                    selected_animal_name, ok_animal = QInputDialog.getItem(parent_window, "Selecione o Animal", "Escolha um animal:", animal_names, 0, False)

                    if ok_animal and selected_animal_name:
                        animal = session.query(Animal).filter(Animal.nome == selected_animal_name, Animal.dono_id == dono.id).first()

                        read_window = QDialog(parent_window)
                        read_window.setWindowTitle("Animal")
                        layout = QVBoxLayout()

                        layout.addWidget(QLabel(f"Nome: {animal.nome}"))
                        layout.addWidget(QLabel(f"Data de Nascimento: {animal.data_nasc.strftime('%d/%m/%Y') if animal.data_nasc else 'Não informado'}"))
                        layout.addWidget(QLabel(f"Tratamentos Realizados: {animal.tratamentos_realizados or 'Nenhum'}"))
                        layout.addWidget(QLabel(f"Espécie: {animal.especie.nome}"))
                        layout.addWidget(QLabel(f"Dono: {dono.nome} - {dono.cpf}"))

                        consultas_str = ', '.join([c.data_consulta.strftime("%d/%m/%Y") for c in animal.consultas]) if animal.consultas else 'Nenhuma consulta'
                        layout.addWidget(QLabel(f"Histórico de Consultas: {consultas_str}"))

                        vacinas_str = ', '.join([v.nome for v in animal.vacinas]) if animal.vacinas else 'Nenhuma vacina registrada'
                        layout.addWidget(QLabel(f"Vacinas: {vacinas_str}"))

                        read_window.setLayout(layout)
                        read_window.exec_()
                    else:
                        QMessageBox.warning(self, "Erro", "Nenhum animal selecionado.")
                else:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para esse dono.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado. Certifique-se de que o CPF ou CNPJ está cadastrado.")


    def update_animal(self):
        cpf_cnpj, ok = QInputDialog.getText(self, "Atualizar Animal", "Digite o CPF ou CNPJ do dono:")
        if ok and cpf_cnpj:
            pessoa_fisica = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_cnpj).first()
            ong = session.query(ONG).filter(ONG.cnpj == cpf_cnpj).first()
            dono = pessoa_fisica if pessoa_fisica else ong

            if dono:
                animais = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if animais:
                    nomes_animais = [f"{animal.id}: {animal.nome}" for animal in animais]
                    animal_selecionado, ok_animal = QInputDialog.getItem(self, "Escolher Animal", "Escolha o animal a ser atualizado:", nomes_animais, 0, False)

                    if ok_animal and animal_selecionado:
                        id_animal = animal_selecionado.split(":")[0]
                        animal = session.query(Animal).filter(Animal.id == id_animal).first()

                        if animal:
                            atributos = [
                                "Nome",
                                "Data de Nascimento",
                                "Tratamentos Realizados"
                            ]
    
                            atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                            if ok_atributo and atributo:
                                if atributo == "Nome":
                                    novo_nome, ok_nome = QInputDialog.getText(self, "Atualizar Nome", "Nome atual: {}. Digite o novo nome (ou deixe em branco para manter):".format(animal.nome))
                                    if ok_nome and novo_nome:
                                        animal.nome = novo_nome

                                elif atributo == "Data de Nascimento":
                                    nova_data_nascimento, ok_data = QInputDialog.getText(self, "Atualizar Data de Nascimento", "Data de Nascimento atual: {}. Digite a nova data de nascimento (ou deixe em branco para manter):".format(animal.data_nascimento))
                                    if ok_data and nova_data_nascimento:
                                        animal.data_nascimento = nova_data_nascimento

                                elif atributo == "Tratamentos Realizados":
                                    novos_tratamentos, ok_tratamentos = QInputDialog.getText(self, "Atualizar Tratamentos Realizados", "Tratamentos atuais: {}. Digite os novos tratamentos (ou deixe em branco para manter):".format(animal.tratamentos_realizados))
                                    if ok_tratamentos:
                                        if novos_tratamentos:
                                            animal.tratamentos_realizados = novos_tratamentos 
                            session.commit()
                            QMessageBox.information(self, "Sucesso", "Informação do animal atualizada com sucesso!")
                        else:
                            QMessageBox.warning(self, "Erro", "Animal não encontrado.")
                else:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para este dono.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado.")

    def delete_animal(self):
        cpf_cnpj, ok = QInputDialog.getText(self, "Deletar Animal", "Digite o CPF ou CNPJ do dono:")
        if ok and cpf_cnpj:
            pessoa_fisica = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_cnpj).first()
            ong = session.query(ONG).filter(ONG.cnpj == cpf_cnpj).first()
            dono = pessoa_fisica if pessoa_fisica else ong

            if dono:
                animais = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if animais:
                    nomes_animais = [f"{animal.id}: {animal.nome}" for animal in animais]
                    animal_selecionado, ok_animal = QInputDialog.getItem(self, "Escolher Animal", "Escolha o animal a ser deletado:", nomes_animais, 0, False)

                    if ok_animal and animal_selecionado:
                        id_animal = animal_selecionado.split(":")[0]
                        animal = session.query(Animal).filter(Animal.id == id_animal).first()

                        if animal:
                            session.delete(animal)
                            session.commit()
                            QMessageBox.information(self, "Sucesso", "Animal deletado com sucesso!")
                        else:
                            QMessageBox.warning(self, "Erro", "Animal não encontrado.")
                else:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para este dono.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado.")



# CRUD Consulta
    def create_consulta(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar Consulta")
        create_window.setGeometry(200, 200, 300, 400)

        layout = QVBoxLayout()

        self.data_consulta_input = QDateEdit()
        self.data_consulta_input.setCalendarPopup(True)
        self.data_consulta_input.setDate(QDate.currentDate())

        self.animal_combobox = QComboBox()
        self.animal_combobox.addItems([f"{a.nome} ({a.id})" for a in session.query(Animal).all()])  

        self.veterinario_combobox = QComboBox()
        self.veterinario_combobox.addItems([f"{v.nome}" for v in session.query(Veterinario).all()])  

        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Descrição")

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(QLabel("Data da Consulta:"))
        layout.addWidget(self.data_consulta_input)
        layout.addWidget(QLabel("Animal:"))
        layout.addWidget(self.animal_combobox)
        layout.addWidget(QLabel("Veterinário:"))
        layout.addWidget(self.veterinario_combobox)
        layout.addWidget(QLabel("Descrição:"))
        layout.addWidget(self.descricao_input)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_consulta(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_consulta(self, window):
        data_consulta = self.data_consulta_input.date().toPyDate()
        animal_id = self.animal_combobox.currentText().split("(")[-1].strip(")")
        veterinario_nome = self.veterinario_combobox.currentText()

        animal = session.query(Animal).filter(Animal.id == animal_id).first()
        veterinario = session.query(Veterinario).filter(Veterinario.nome == veterinario_nome).first()

        nova_consulta = Consulta(
            data_consulta=data_consulta,  
            animal=animal,
            veterinario=veterinario,
            descricao=self.descricao_input.text()
        )

        session.add(nova_consulta)
        session.commit()

        QMessageBox.information(window, "Sucesso", "Consulta adicionada com sucesso!")
        window.close()

    def read_consulta(self, parent_window):
        cpf_cnpj, ok = QInputDialog.getText(self, "Buscar Consulta", "Digite o CPF ou CNPJ do cliente:")

        if ok and cpf_cnpj:
            if len(cpf_cnpj) == 11:  
                dono = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_cnpj).first()
            elif len(cpf_cnpj) == 14:  
                dono = session.query(ONG).filter(ONG.cnpj == cpf_cnpj).first()
            else:
                QMessageBox.warning(self, "Erro", "Digite um CPF (11 dígitos) ou um CNPJ (14 dígitos) válidos.")
                return

            if dono:
                animals = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if animals:
                    animal_names = [animal.nome for animal in animals]
                    selected_animal_name, ok_animal = QInputDialog.getItem(parent_window, "Selecione o Animal", "Escolha um animal:", animal_names, 0, False)

                    if ok_animal and selected_animal_name:
                        animal = session.query(Animal).filter(Animal.nome == selected_animal_name, Animal.dono_id == dono.id).first()

                        consultas = session.query(Consulta).filter(Consulta.animal_id == animal.id).all()

                        if consultas:
                            consultas_str = [f"ID: {consulta.id} - Data: {consulta.data_consulta.strftime('%d/%m/%Y')}" for consulta in consultas]
                            selected_consulta_str, ok_consulta = QInputDialog.getItem(parent_window, "Selecione a Consulta", "Escolha uma consulta:", consultas_str, 0, False)

                            if ok_consulta and selected_consulta_str:
                                consulta_id = int(selected_consulta_str.split(" - ")[0].split(": ")[1])

                                consulta = session.query(Consulta).filter(
                                    Consulta.id == consulta_id
                                ).first()

                                if consulta:
                                    read_window = QDialog(parent_window)
                                    read_window.setWindowTitle("Consulta")
                                    layout = QVBoxLayout()

                                    layout.addWidget(QLabel(f"Data da Consulta: {consulta.data_consulta.strftime('%d/%m/%Y')}"))
                                    layout.addWidget(QLabel(f"Descrição: {consulta.descricao}"))
                                    layout.addWidget(QLabel(f"Veterinário: {consulta.veterinario.especializacao} - Registro: {consulta.veterinario.numero_reg_prof}"))

                                    read_window.setLayout(layout)
                                    read_window.exec_()
                                else:
                                    QMessageBox.warning(self, "Erro", "Consulta não encontrada para o ID selecionado.")
                            else:
                                QMessageBox.warning(self, "Erro", "Nenhuma consulta selecionada.")
                        else:
                            QMessageBox.warning(self, "Erro", "Nenhuma consulta registrada para esse animal.")
                    else:
                        QMessageBox.warning(self, "Erro", "Nenhum animal selecionado.")
                else:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para esse dono.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado. Certifique-se de que o CPF ou CNPJ está cadastrado.")



    def update_consulta(self):
        cpf_cnpj, ok = QInputDialog.getText(self, "Atualizar Consulta", "Digite o CPF ou CNPJ do cliente:")

        if ok and cpf_cnpj:
            if len(cpf_cnpj) == 11:  
                dono = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_cnpj).first()
            elif len(cpf_cnpj) == 14:  
                dono = session.query(ONG).filter(ONG.cnpj == cpf_cnpj).first()
            else:
                QMessageBox.warning(self, "Erro", "Digite um CPF (11 dígitos) ou um CNPJ (14 dígitos) válidos.")
                return

            if dono:
                animals = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if animals:
                    animal_names = [animal.nome for animal in animals]
                    selected_animal_name, ok_animal = QInputDialog.getItem(self, "Selecione o Animal", "Escolha um animal:", animal_names, 0, False)

                    if ok_animal and selected_animal_name:
                        animal = session.query(Animal).filter(Animal.nome == selected_animal_name, Animal.dono_id == dono.id).first()

                        consultas = session.query(Consulta).filter(Consulta.animal_id == animal.id).all()

                        if consultas:
                            consultas_str = [f"ID: {consulta.id} - Data: {consulta.data_consulta.strftime('%d/%m/%Y')}" for consulta in consultas]
                            selected_consulta_str, ok_consulta = QInputDialog.getItem(self, "Selecione a Consulta", "Escolha uma consulta:", consultas_str, 0, False)

                            if ok_consulta and selected_consulta_str:
                                consulta_id = int(selected_consulta_str.split(" - ")[0].split(": ")[1])

                                consulta = session.query(Consulta).filter(Consulta.id == consulta_id).first()

                                if consulta:
                                    atributos = [
                                        "Data",
                                        "Veterinário",
                                        "Descrição"
                                    ]

                                    atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                                    if ok_atributo and atributo:
                                        if atributo == "Data":
                                            nova_data, ok_data = QInputDialog.getText(self, "Atualizar Data", f"Data atual: {consulta.data_consulta.strftime('%d/%m/%Y')}. Digite a nova data (ou deixe em branco para manter):")
                                            if ok_data and nova_data:
                                                consulta.data_consulta = datetime.strptime(nova_data, "%Y-%m-%d").date()  

                                        elif atributo == "Veterinário":
                                            novo_veterinario_nome, ok_vet = QInputDialog.getItem(self, "Escolher Veterinário", "Escolha um novo veterinário:", [f"{v.nome}" for v in session.query(Veterinario).all()])
                                            if ok_vet:
                                                consulta.veterinario = session.query(Veterinario).filter(Veterinario.nome == novo_veterinario_nome).first()

                                        elif atributo == "Descrição":
                                            nova_descricao, ok_desc = QInputDialog.getText(self, "Atualizar Descrição", f"Descrição atual: {consulta.descricao}. Digite a nova descrição (ou deixe em branco para manter):")
                                            if ok_desc:
                                                consulta.descricao = nova_descricao or consulta.descricao

                                    session.commit()
                                    QMessageBox.information(self, "Sucesso", "Informação da consulta atualizada com sucesso!")
                                else:
                                    QMessageBox.warning(self, "Erro", "Consulta não encontrada.")
                            else:
                                QMessageBox.warning(self, "Erro", "Nenhuma consulta selecionada.")
                        else:
                            QMessageBox.warning(self, "Erro", "Nenhuma consulta registrada para esse animal.")
                    else:
                        QMessageBox.warning(self, "Erro", "Nenhum animal selecionado.")
                else:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para esse dono.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado. Certifique-se de que o CPF ou CNPJ está cadastrado.")


    def delete_consulta(self):
        cpf_cnpj, ok = QInputDialog.getText(self, "Deletar Consulta", "Digite o CPF ou CNPJ do cliente:")

        if ok and cpf_cnpj:
            if len(cpf_cnpj) == 11:  
                dono = session.query(PessoaFisica).filter(PessoaFisica.cpf == cpf_cnpj).first()
            elif len(cpf_cnpj) == 14:  
                dono = session.query(ONG).filter(ONG.cnpj == cpf_cnpj).first()
            else:
                QMessageBox.warning(self, "Erro", "Digite um CPF (11 dígitos) ou um CNPJ (14 dígitos) válidos.")
                return

            if dono:
                animals = session.query(Animal).filter(Animal.dono_id == dono.id).all()

                if animals:
                    animal_names = [animal.nome for animal in animals]
                    selected_animal_name, ok_animal = QInputDialog.getItem(self, "Selecione o Animal", "Escolha um animal:", animal_names, 0, False)

                    if ok_animal and selected_animal_name:
                        animal = session.query(Animal).filter(Animal.nome == selected_animal_name, Animal.dono_id == dono.id).first()

                        consultas = session.query(Consulta).filter(Consulta.animal_id == animal.id).all()

                        if consultas:
                            consultas_str = [f"ID: {consulta.id} - Data: {consulta.data_consulta.strftime('%d/%m/%Y')}" for consulta in consultas]
                            selected_consulta_str, ok_consulta = QInputDialog.getItem(self, "Selecione a Consulta", "Escolha uma consulta:", consultas_str, 0, False)

                            if ok_consulta and selected_consulta_str:
                                consulta_id = int(selected_consulta_str.split(" - ")[0].split(": ")[1])

                                consulta = session.query(Consulta).filter(Consulta.id == consulta_id).first()

                                if consulta:
                                    session.delete(consulta)
                                    session.commit()
                                    QMessageBox.information(self, "Sucesso", "Consulta deletada com sucesso!")
                                else:
                                    QMessageBox.warning(self, "Erro", "Consulta não encontrada.")
                            else:
                                QMessageBox.warning(self, "Erro", "Nenhuma consulta selecionada.")
                        else:
                            QMessageBox.warning(self, "Erro", "Nenhuma consulta registrada para esse animal.")
                    else:
                        QMessageBox.warning(self, "Erro", "Nenhum animal selecionado.")
                else:
                    QMessageBox.warning(self, "Erro", "Nenhum animal encontrado para esse dono.")
            else:
                QMessageBox.warning(self, "Erro", "Dono não encontrado. Certifique-se de que o CPF ou CNPJ está cadastrado.")


# CRUD Veterinario
    def create_veterinario(self, parent_window):
        create_window = QDialog(parent_window)
        create_window.setWindowTitle("Adicionar Veterinário")
        create_window.setGeometry(200, 200, 300, 250)

        layout = QVBoxLayout()

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome do Veterinário")

        self.especializacao_input = QLineEdit()
        self.especializacao_input.setPlaceholderText("Especialização do Veterinário")

        self.numero_reg_prof_input = QLineEdit()
        self.numero_reg_prof_input.setPlaceholderText("Número de Registro Profissional")

        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")

        layout.addWidget(self.nome_input)
        layout.addWidget(self.especializacao_input)
        layout.addWidget(self.numero_reg_prof_input)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_cancelar)

        create_window.setLayout(layout)

        btn_salvar.clicked.connect(lambda: self.salvar_veterinario(create_window))
        btn_cancelar.clicked.connect(create_window.close)

        create_window.exec_()

    def salvar_veterinario(self, window):
        nome = self.nome_input.text()
        especializacao = self.especializacao_input.text()
        numero_reg_prof = self.numero_reg_prof_input.text()

        novo_veterinario = Veterinario(
            nome=nome,
            especializacao=especializacao,
            numero_reg_prof=numero_reg_prof
        )

        session.add(novo_veterinario)
        session.commit()

        QMessageBox.information(window, "Sucesso", f"Veterinário adicionado com sucesso! ID: {novo_veterinario.id}")
        window.close()

    def read_veterinario(self, parent_window):
        numero_reg_prof = QInputDialog.getText(self, "Buscar Veterinário", "Digite o número de registro profissional:")

        if numero_reg_prof[1]:
            veterinario = session.query(Veterinario).filter(Veterinario.numero_reg_prof == numero_reg_prof[0]).first()

            if veterinario:
                read_window = QDialog(parent_window)
                read_window.setWindowTitle("Informações do Veterinário")
                layout = QVBoxLayout()

                layout.addWidget(QLabel(f"ID: {veterinario.id}"))
                layout.addWidget(QLabel(f"Nome: {veterinario.nome}"))
                layout.addWidget(QLabel(f"Especialização: {veterinario.especializacao}"))
                layout.addWidget(QLabel(f"Número de Registro Profissional: {veterinario.numero_reg_prof}"))

                read_window.setLayout(layout)
                read_window.exec_()
            else:
                QMessageBox.warning(self, "Erro", "Veterinário não encontrado.")


    def update_veterinario(self):
        numero_reg_prof = QInputDialog.getText(self, "Atualizar Veterinário", "Digite o número de registro profissional:")

        if numero_reg_prof[1]:  
            veterinario = session.query(Veterinario).filter(Veterinario.numero_reg_prof == numero_reg_prof[0]).first()

            if veterinario:
                
                atributos = [
                    "Nome",
                    "Especialização",
                    "Número de Registro Profissional"
                ]

                atributo, ok_atributo = QInputDialog.getItem(self, "Escolher Atributo", "Escolha o atributo a ser atualizado:", atributos, 0, False)
                if ok_atributo and atributo:
                    if atributo == "Nome":
                        novo_nome = QInputDialog.getText(self, "Atualizar Nome", f"Novo nome (atual: {veterinario.nome}):")[0]
                        veterinario.nome = novo_nome or veterinario.nome

                    elif atributo == "Especialização":
                        nova_especializacao = QInputDialog.getText(self, "Atualizar Especialização", f"Nova especialização (atual: {veterinario.especializacao}):")[0]
                        veterinario.especializacao = nova_especializacao or veterinario.especializacao

                    elif atributo == "Número de Registro Profissional":
                        novo_numero_reg_prof = QInputDialog.getText(self, "Atualizar Registro Profissional", f"Novo número de registro (atual: {veterinario.numero_reg_prof}):")[0]
                        veterinario.numero_reg_prof = novo_numero_reg_prof or veterinario.numero_reg_prof

                session.commit()
                QMessageBox.information(self, "Sucesso", "Veterinário atualizado com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Veterinário não encontrado.")


    def delete_veterinario(self):
        numero_reg_prof = QInputDialog.getText(self, "Deletar Veterinário", "Digite o número de registro profissional:")

        if numero_reg_prof[1]: 
            veterinario = session.query(Veterinario).filter(Veterinario.numero_reg_prof == numero_reg_prof[0]).first()

            if veterinario:
                session.delete(veterinario)
                session.commit()
                QMessageBox.information(self, "Sucesso", "Veterinário removido com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Veterinário não encontrado.")

app = QApplication([])
window = MenuPrincipal()
window.show()
app.exec_()