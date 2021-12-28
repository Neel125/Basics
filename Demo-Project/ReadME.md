# Pallet and Forklift Mate/Unmate event detection.

## How to run

### create and activate environment
#### for windows
```
python3 -m venv venv
venv\Scripts\activate
```
#### for ubuntu
```
virtualenv venv --python=python3
. venv/bin/activate
```
  
### Install requirements
```
pip install -r requirements.txt
```

Keep video and json file in videos folder 
If it has 2K resolution then put in 2k folder otherwise put in 4k folder

In PalletAndForklift.py give video path with same prefix of the json file which contains the data points
```
video_path = "./videos/4k/perfect_high4_0_00093_20210611-165430_15593.mp4"
```

For this video file json filename should be 
```
perfect_high4_0_00093_20210611-165430_15593.mp4.json
```

### Run python file
```
python pallet_moves.py
```
