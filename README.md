


## Install (New)

Install the dependencies with [Anaconda](https://www.anaconda.com/products/individual) and activate the environment `agent` with
```bash
conda env create --file requirements.yaml
conda activate agent
python -m spacy download en_core_web_sm
pip install BeautifulSoup4
```

## Run
```bash
python main.py
```

## Install (Old backup)

First, Python (version 3.0 or higher) needs to be installed. To do that visit https://www.python.org/downloads/.

The following installs are also needed (using "pip3 install") :

    - python-telegram-bot
    - pandas
    - sentence_transformers
    - spacy
    - -U git+https://github.com/oborchers/Fast_Sentence_Embeddings
    - gensim
    - hydra-core
    - bitarray
    - sacrebleu

Lastly, run: python3 -m spacy download en_core_web_sm

You are now able to run the chatbot. To run the chatbot, enter "python3 main.py" in the terminal. To communicate with the chatbot in Telegram, search @PersuasiveHealthBot.

