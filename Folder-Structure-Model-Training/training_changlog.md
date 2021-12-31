# Model Training Change Log
All notable changes for model training are listed here.

### Initial Parameters and Datasets 

## Training 1 - 20-12-2021
Below are the initial parameters and dataset used for training.

#### Dataset: 
Open Images dataset

#### Dataset Path:
dataset/data_v1

#### Classes:
- Person
- Motorcycle 
- Bus
- Car
- etc...

#### Parameters used for initial training
`Learning Rate: 1e-4`

`Epochs: 500`

`Batch size: 128`

`Optimizer: Adam`

`Activation function: Softmax`

`Metric: mean_square_error`

#### Pre-Trained Model used
faster_rcnn_resnet50_v1_640x640_coco17_tpu-8

#### Saved model Path
training_1/models

#### Exported model Path
training_1/exported-models


## Training 2 - 21-12-2021
We are re-trainig the model becuase we are not getting the good result from the last trainig.
This time we are resizing the images to train the model.
Also, we are changing the some parameters to experiments.

#### Dataset: 
Open Images dataset

#### Dataset Path:
dataset/data_v2

#### Classes:
- Person
- Motorcycle 
- Bus
- Car
- etc...

#### Parameters used for training
`Learning Rate: 1e-2`

`Epochs: 700`

`Batch size: 128`

`Optimizer: SGD`

`Activation function: Softmax`

`Metric: categorical_crossentropy`

#### Pre-Trained Model used
faster_rcnn_resnet50_v1_640x640_coco17_tpu-8

#### Saved model Path
training_2/models

#### Exported model Path
training_2/exported-models


## Training 3 - 22-12-2021
We are re-trainig the model becuase we are not getting the good result from the last trainig.
This time we are resizing the images to train the model.
This time we are changing the pre-trained model and also adding some more classes.
Alos, we are using the initial parameters

#### Dataset: 
Open Images dataset

#### Dataset Path:
dataset/data_v2

#### Classes:
- Person
- Motorcycle 
- Bus
- Car
- etc...


#### Parameters used for training
`Learning Rate: 1e-4`

`Epochs: 500`

`Batch size: 128`

`Optimizer: Adam`

`Activation function: Softmax`

`Metric: mean_square_error`


#### Pre-Trained Model used
SSD MobileNet V2 FPNLite 640x640


#### Saved model Path
training_3/models

#### Exported model Path
training_3/exported-models




