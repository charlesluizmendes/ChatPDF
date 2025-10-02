## Criando Ambiente

Acesse a pasta do projeto e cria uma Virtualenv:

```
$ python -m venv venv
```

Após isso, inicie a Virtualenv criada anteriormente:

* Para Sistemas baseados em Unix
```
$ source venv/bin/active
```
* Para Windows
```
$ venv/Scripts/activate
```

## Dependências do Projeto

### Instalação dos Pacotes

Se preferir instalar todas as dependências do projeto, execute os comandos abaixo:

```
pip install "fastapi[standard]"
pip install pymongo
pip install pypdf
pip install langchain
pip install langchain-community
pip install langchain-openai
pip install langchain-mongodb 
```