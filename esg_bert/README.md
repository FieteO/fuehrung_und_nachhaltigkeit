# [ESG BERT](https://github.com/mukut03/ESG-BERT)

## Directory structure
``` bash
(bert_env) fiete@ubu:~/Documents/studium/fuehrung_und_nachhaltigkeit/esg_bert$ tree -L 2
.
├── bert_env
│   ├── bin
│   ├── lib
│   └── pyvenv.cfg
├── bert_handler.py
├── bert_model
│   ├── config.json
│   ├── pytorch_model.bin
│   └── vocab.txt
├── model_store
│   └── bert.mar
├── README.md
└── requirements

5 directories, 8 files
```

## Create a virtual environment
`virtualenv bert_env`

## Activate
`source bert_env/bin/activate`

## Install packages
`pip install -r requirements`

## Download the model data
Download the model data from [here](https://drive.google.com/drive/folders/1Qz4HP3xkjLfJ6DGCFNeJ7GmcPq65_HVe) and save all files in the `bert_model` directory.

## Generate a .mar file based on the pytorch_model.bin
Create a `model_store` directory and then run
``` bash
torch-model-archiver --model-name "bert" --version 1.0 --serialized-file ./bert_model/pytorch_model.bin --extra-files "./bert_model/config.json,./bert_model/vocab.txt,./bert_model/index_to_name.json" --handler "./bert_handler.py" --export-path "model_store/"
```

## Start the torchserve server
`torchserve --start --model-store model_store --models bert=bert.mar`

## Try it out
``` bash
(nlp_env) fiete@ubu:~/Documents/studium/fuehrung_und_nachhaltigkeit/esg_bert$ curl -X POST http://127.0.0.1:8080/predictions/bert -T input_files/deutsche-boerse.txt
{
  "code": 503,
  "type": "InternalServerException",
  "message": "Prediction failed"
}
```
This can be mapped to the following labels
```
__label__Business_Ethics :  0
__label__Data_Security :  1
__label__Access_And_Affordability :  2
__label__Business_Model_Resilience :  3
__label__Competitive_Behavior :  4
__label__Critical_Incident_Risk_Management :  5
__label__Customer_Welfare :  6
__label__Director_Removal :  7
__label__Employee_Engagement_Inclusion_And_Diversity :  8
__label__Employee_Health_And_Safety :  9
__label__Human_Rights_And_Community_Relations :  10
__label__Labor_Practices :  11
__label__Management_Of_Legal_And_Regulatory_Framework :  12
__label__Physical_Impacts_Of_Climate_Change :  13
__label__Product_Quality_And_Safety :  14
__label__Product_Design_And_Lifecycle_Management :  15
__label__Selling_Practices_And_Product_Labeling :  16
__label__Supply_Chain_Management :  17
__label__Systemic_Risk_Management :  18
__label__Waste_And_Hazardous_Materials_Management :  19
__label__Water_And_Wastewater_Management :  20
__label__Air_Quality :  21
__label__Customer_Privacy :  22
__label__Ecological_Impacts :  23
__label__Energy_Management :  24
__label__GHG_Emissions :  25
```

## Stop torchserve
`torchserve --stop`