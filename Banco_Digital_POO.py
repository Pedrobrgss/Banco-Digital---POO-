import os
import time
import textwrap
from datetime import datetime
from abc import ABC,abstractclassmethod,abstractproperty

class Cliente:
    def __init__(self,endereco):
        self._endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao ):
        transacao.registrar(conta)

    def adicionar_conta(self,conta):
        self.contas.append(conta)


class Pessoa_Fisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
        
    def saldo(self):
        return self._saldo

    @classmethod
    def criar_conta(cls, cliente, numero):
        return cls(numero,cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def historico(self):
        return self._historico
    
    @property
    def cliente(self):
        return self._cliente
    
    def sacar(self, valor):
        saldo = self._saldo
        excedeu_saldo = valor > saldo
        
        if excedeu_saldo:
            print("Não será possivel sacar por falta de saldo!")

        elif valor > 0:
            self._saldo -= valor
            print("Valor sacado com sucesso!")
            return True
        
        else:
            print("Operação falhou! o valor informado é inválido.")

        return False 
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito concluido com sucesso! seu saldo foi atualizado.")
            return True

        else:
            print("Não é possivel depositar este valor! tente novamente.")
            return False


class Conta_Corrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao ["tipo"]== Saque.__name__]
                            )
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("Operação falhou! o valor do saque excede o limite")  

        elif excedeu_saques:
            print("Você ultrapassou o limite de saques diários!")

        else:
            return super().sacar(valor)
        
        return False
    def __str__(self):
        return f'''\
            Agência: \t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        '''


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self,transacao):
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu =  """
                   
                          BANCO DIGITAL
  
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nu]\tNovo usuario
    [nc]\tNova conta
    [lc]\tListar contas
    [q]\tSair
    
    => """
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui uma conta!")
        return


    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    valor = float(input("Informe o valor de depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return

    valor= float(input("Informe o valor de saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    transacoes = conta.historico.transacoes
        
    extrato = ""
    if not transacoes:
        print("Não foram realizadas movimentações! ")

    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}: \n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f} ")

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("Já existe um cliente com este CPF!")
        return
    
    nome = input("Informe o nome completo: ")
    data_nascimento = ("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = Pessoa_Fisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf,endereco=endereco)

    clientes.append(cliente)

    print("Usuario criado com sucesso!")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    conta = Conta_Corrente.criar_conta(cliente=cliente,numero = numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n Conta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 68)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        print("========".center(60,"="),end=" ")
        opcao = menu()
        if opcao == "d":
            os.system("cls")
            print("Depósito".center(60,"="))
            print()

            depositar(clientes) 

            print()
            print("========".center(60,"="))
            print("Voltando para o menu...")
            time.sleep(3)
            os.system("cls")

        elif opcao == "s":
            os.system("cls")
            print("Saque".center(60,"="))

            sacar(clientes)

            print("========".center(60,"="))
            print("Voltando para o menu...")
            time.sleep(3)
            os.system("cls")

        elif opcao == "e":
            os.system("cls")
            print("Extrato".center(60,"="))
            print()

            exibir_extrato(clientes)

            print("========".center(60,"="))
            print("Voltando para o menu...")
            time.sleep(5)
            os.system("cls")

        elif opcao == "nu":
            os.system("cls")
            print("Novo usuario".center(60,"="))
            print()
             
            criar_cliente(clientes)

            print("========".center(60,"="))
            print("Voltando para o menu...")
            time.sleep(5)
            os.system("cls")

        elif opcao == "nc":
            os.system("cls")
            print("Novo usuario".center(60,"="))
            print()

            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

            print("========".center(60,"="))
            print("Voltando para o menu...")
            time.sleep(5)
            os.system("cls")

        elif opcao == "lc":
            listar_contas(contas)

            print("========".center(60,"="))
            print("Voltando para o menu...")
            time.sleep(5)
            os.system("cls")

        elif opcao == "q":
            break
            
        else:
            print("Operação inválida! selecione uma opção válida.")

main()