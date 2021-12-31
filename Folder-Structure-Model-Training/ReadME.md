# Folder Structure for model training
    .
    ├── workspace                           # In which all your projects are listed 
    │   ├── Project-Name                    # Your Project Name
    │   │   ├── dataset                     # Dataset folder in which you store all the images
    │   │   │   ├── data_v1                 # Intial dataset used for first model trainig
    │   │   │   │   ├── train               # trin set
    │   │   │   │   ├── validation          # validation set
    │   │   │   │   └── test                # test set
    │   │   │   └── data_v2                 # Modified dataset for second time trained
    │   │   │       └── ...
    │   │   │ 
    │   │   ├── scripts                     # Folder in which all python scripted are listed
    │   │   │   ├── preprocessing           # folder contains the data pre-preocessing scripts
    │   │   │   │   ├── partition_dataset.py # 
    │   │   │   │   ├── generate_tfrecord.py # 
    │   │   │   │   └── ...
    │   │   │   ├── model.py                # model architecture file 
    │   │   │   ├── inference.py            # inference file to evalute model
    │   │   │   ├── inference_on_video.py   # infernce on video to model result on the video file or camera input
    │   │   │   ├── train.py                # model training file 
    │   │   │   └── test.py                 # extra file
    │   │   │
    │   │   ├── training_1                  # This folder contains first time training related data and model
    │   │   │   ├── annotations             # annotations folder 
    │   │   │   │   ├── label_map.pbtxt     # label map file to list out all clasess
    │   │   │   │   ├── annotations.csv     # label map file to list out all clasess
    │   │   │   │   ├── train.tfrecord      # label map file to list out all clasess
    │   │   │   │   ├── test.tfrecord       # label map file to list out all clasess
    │   │   │   ├── exported-models         # save exported model in this folder 
    │   │   │   │   ├── exported_model_file # exported model file
    │   │   │   ├── models                  # save all model checkpoint while training
    │   │   │   │   ├── model_file          # model checkpoint file                    
    │   │   │   ├── pre_trained_models      # Pre-trained model diretory
    │   │   │   │   ├── model_file          # pre-trained model file
    │   │   ├── training_2                  # same as training_1 for second time training
    │   └── ...                 
    └── ...
    │   │   ├── .gitignore                  # gitignore file
    │   │   ├── requirements.txt            # All python requirements 
    │   │   ├── ReadME.md                   # Read me file for description, installations and how to run, etc...
    │   │   ├── training_changelog.md       # Training changelog file to maintain the training details and what changes for second time training  


## Project Setup

#### Install system dependancies
```
write here
```


#### Create Environment
```
conda create -n env_name python=3.8
```

#### Install project dependancies
```
pip install -r requirements.txt
```


#### How to Run?
Mention file name to run 
```
python train.py 
    or
python inference.py
```

### Mention Latest and Best model to inference
Path of the latest and best accurate model we are currently using
```
Model Name or Path of the model
```

Testing the Git Auto Push 90

