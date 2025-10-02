# ChatPDF

API de RAG utilizando LLM do OpenAI e MongoDB Atlas.

## Ambiente

### Virtualenv

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

### Dependências do Projeto

Para instalar todas as dependências do projeto basta executar o comando abaixo:

```
$ pip install -r requirements.txt
```

Ou se preferir, instalar cada dependencia do projeto manualmente execute os comandos abaixo:

```
pip install "fastapi[standard]"
pip install pymongo
pip install pypdf
pip install langchain
pip install langchain-community
pip install langchain-openai
pip install langchain-mongodb 
```

### MongoDB Atlas

Para realizar o armazenamento e recuperação dos embeddings do projeto, será utilizado o MongoDB Atlas, pois o mesmo possui o mecanimsto de busca vetorizada, que é crucial e obrigatorio para este.

Primeiramente crie um container do MongoDB Atlas:

```
docker run -p 27017:27017 --name atlas-local mongodb/mongodb-atlas-local
```

Após isso crie o dataset e as collection no MongoDB Atlas, da mesma maneira que esta no arquivo .env:

```
MONGO_DB=chatpdf
MONGO_COLLECTION_VECTORS=pdf_vectors
MONGO_COLLECTION_DOCS=pdf_documents
```

Com isso teremos o dataset 'chatpdf' e duas collections dentro dele 'pdf_vectors' e 'pdf_documents'.

Agora podemos agora criar o Indexes para o 'source_id' dos chunks e os embeddings da collection 'pdf_vectors', esses serão utilizados no 'pre_filter' do retriever. Basta acessar terminal do container e o MongoDB Atlas, execute os comandos abaixo:

```
docker exec -it [ID do Container Docker do Mongo] bash  
```
```
mongosh
```

E logo após os comandos acima criar o Indexes*:

* Indexes para utilização do OpenAI.

```
use chatpdf
```
```
db.pdf_vectors.createSearchIndex({
  name: "vector_index",
  type: "vectorSearch",
  definition: {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "source_id"
      }
    ]
  }
})
```

Para criação de Indexes no HuggingFace o comando seria:

```
use chatpdf

db.pdf_vectors.createSearchIndex({
  name: "vector_index",
  type: "vectorSearch",
  definition: {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 768,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "source_id"
      }
    ]
  }
})
```

***

Ou se preferir diretamente no Atlas Cloud o fluxo seria um pouco diferente:

Cluster > Browse Collection >
Atlas Search > Create Search Index >
Vector Search > [Selecione o Database e Collection] > JSON Editor > Next

Em seguida inseira o JSON abaixo para o OpenAI:

```
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "source_id"
    }
  ]
}
```

E para o HuggingFace:

```
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "source_id"
    }
  ]
}
```