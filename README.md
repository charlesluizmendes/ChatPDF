# Introduction 

## Used python 3.10.11 for created system:

- install https://rustup.rs/

## Install packages

(enter in directory '/')

```
$ pip install -r requirements.txt
```

### Packages installed:

```
$ pip install flask-restx
$ pip install flask-sqlalchemy
$ pip install flask-marshmallow
$ pip install flask-migrate
$ pip install SQLAlchemy
$ pip install marshmallow
$ pip install marshmallow-sqlalchemy
$ pip install python-dotenv
$ pip install langchain
$ pip install langchain-community
$ pip install langchain-huggingface
$ pip install sentence-transformers
$ pip install pypdf
$ pip install faiss-cpu
```

## Migration using SQLlite:

(enter in directory '/src')

```
$ flask db init
$ flask db migrate -m "Initial migration"
$ flask db upgrade
```

## Used CUDA:

(install)

```
$ pip install accelerate
$ pip install bitsandbytes
$ pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 # change for version CUDA
```

(in chat_util.py)

```
import torch    
quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=quantization_config)
```

(verify is CUDA active)

```
python -c "import torch; print(torch.cuda.is_available())"
```