# 🧠 subvocalization-emg
![image](https://user-images.githubusercontent.com/16140783/210358309-0f4abe70-c86a-4b87-aaa1-741f55dbb9a5.png)

## Hardware
Setup [Cyton Biosensing Board (8-Channels)](https://shop.openbci.com/products/cyton-biosensing-board-8-channel):

![image](https://user-images.githubusercontent.com/16140783/210357774-0cc2cb56-8e68-4f8a-9d3e-177a469efefe.png)

- [Getting Starter Guide](https://docs.openbci.com/GettingStarted/Boards/CytonGS/)

## Setup
```py
pip install -r requirements.txt
```

## Running
```py
python ./start.py
```
You might use `Synthetic` board for testing but in case the Cyton dongle/board is not found you might need to run with sudo (linux).
