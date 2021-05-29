## Create a virtual environment
`virtualenv nlp_env`

## Activate
`source nlp_env/bin/activate`

## Install packages
`pip install -r requirements`

## Deactivate
`deactivate`

## Make sure you have enough RAM
Increase the available swap memory on Ubuntu with:
``` bash
# show current swap file
fiete@ubu:~$ swapon --show
NAME      TYPE SIZE USED PRIO
/swapfile file   2G 1,9G   -2
# turn it off
fiete@ubu:~$ sudo swapoff /swapfile
[sudo] password for fiete:
# allocate a new file 
fiete@ubu:~$ sudo fallocate -l 8G /swapfile
# make it a swapfile
fiete@ubu:~$ sudo mkswap /swapfile 
mkswap: /swapfile: warning: wiping old swap signature.
Setting up swapspace version 1, size = 8 GiB (8589930496 bytes)
no label, UUID=1ace04d1-f525-4b6f-b323-f61be87b336b
# enable the swapfile
fiete@ubu:~$ sudo swapon /swapfile
fiete@ubu:~$ 
```

# [NLP Tutorial](https://www.kaggle.com/learn/natural-language-processing)

[SpaCy Homepage](https://spacy.io/)

## Download language models for spacy (see [Trained Models & Pipelines](https://spacy.io/models))
`python -m spacy download en_core_web_sm`
`python -m spacy download de_core_news_sm`

## [Tesserocr table detection](https://stackoverflow.com/questions/59135975/need-help-in-table-detection-using-tesserocr-python)