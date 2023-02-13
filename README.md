<h1 align="center">
    <img width="300" src="https://user-images.githubusercontent.com/16140783/218357099-29d4848f-89ee-463e-9ead-40f27c976f61.png" align="center"></img>
    <br/>Subvocalization EMG
</h1>
<p align="center">Project for recording and training subvocalization <strong>EMG</strong> data with the Cyton Board.
<br/>by <strong>Mateus de Aquino Batista</strong> for the Bachelor's Degree Final Project.</p>

<p align="center">
  <a aria-label="Python version" href="https://www.python.org/downloads/release/python-3109/">
    <img src="https://img.shields.io/badge/python-3.10.9-informational?logo=Python"></img>
  </a>
  <a aria-label="Tensorflow (keras) version" href="https://www.tensorflow.org/api_docs/python/tf/keras">
    <img src="https://img.shields.io/badge/tensorflow-2.11.0-informational?logo=Tensorflow"></img>
  </a>
  <a aria-label="Papers (coming soon)" href="#">
    <img src="https://img.shields.io/badge/dissertation-coming%20soon-yellow"></img>
  </a>
</p>

## 📄 Abstract
> Dysarthria is a change in the normal pronunciation of words, usually caused by neurological disturbances. In advanced cases, when speech therapy is not enough to enable communication in a practical way, a silent speech interface can be used to carry out a conversation with a smaller vocabulary, through the identification of subtle movements in speech captured by an electromyography device of surface.

> The present study deals with an instrumentation project of a low-cost silent speech interface and the development of a neural network to identify subvocalized words together plus an experimental case study for the equipment validation. An OpenBCI electromyography modular board will be used to read muscle activity data from the face, and these data will be later on processed, and classified by a convolutional neural network for the identification of subvocalized words.

> Regarding the validation, the success rates of the neural network of the silent speech interface will be used to evaluate the general and individual performance for each participant. A hit rate between 90 and 95% is expected from the general validation.

> Henceforth, with positive results coming from the interface, more words can be added in the advance, in order to guarantee greater usefulness in the daily lives of patients with communication difficulties.


## 🔧 Hardware Requirements
<a target="_blank" href="https://shop.openbci.com/products/cyton-biosensing-board-8-channel"><img width="270px" alt="Cyton Biosensing Board" title="Cyton Biosensing Board" align="right" src="https://user-images.githubusercontent.com/16140783/210357774-0cc2cb56-8e68-4f8a-9d3e-177a469efefe.png"/></a>

This project requires setting up a [Cyton Biosensing Board (8-Channels)](https://shop.openbci.com/products/cyton-biosensing-board-8-channel), which is a neural interface board developed by OpenBCI with a 32-bit processor that can be used to sample EEG, EMG, and ECG activity. Follow the starter guide to make sure you get it right.


- [Getting Starter Guide](https://docs.openbci.com/GettingStarted/Boards/CytonGS/)

This project also allows using the Synthetic board as a mock to the Cyton board. However, as it generates random data, training and validation of the Neural Networks with the `Synthetic` option will not work.

## 🚀 Setup
After setting up your Cyton Board, you'll need to install the package dependencies:

```bash
pip install -r requirements.txt
```

Once you're done simply run:

```py
python ./start.py
```

It should be accessible at [`localhost:8000`](http://localhost:8000). In case the Cyton dongle is not available you might need to run with administrator privileges.

## 🧠 How to use

The main page includes the Time Series (unprocessed) for all 8 channels, you can also see some logging information and access to the board session on top of the page. Once the session is started you'll have access to the Recording tab, a page to setup the words and amount of information you'll want to train later. Note that all the default existing words are currently hardcoded into the HTML file, but they can be changed anytime:

EMG Tab                    |  Recording Tab
:-------------------------:|:-------------------------:
![EMG Tab](https://user-images.githubusercontent.com/16140783/218353244-99ca24d5-75c7-496a-9e3e-63f4a62a2ae9.png)  |  ![Recording Tab](https://user-images.githubusercontent.com/16140783/218360435-4d74c0dc-af67-4815-9a15-9b2f6b2efbb8.png)

After recording your first session (automatically saved as a csv file), the Neural Network tab will be available for training. This is where you include all recordings and setup all the training configs. Once started, you can check the training progress in real time. After the training is complete, you'll have access to the Evaluation tab, where you can test the predicting capability of the models you've trained.

Neural Network Tab         |  Evaluator Tab
:-------------------------:|:-------------------------:
![Neural Network Tab](https://user-images.githubusercontent.com/16140783/218360970-d672cc7c-84f6-45b2-b0d8-07ab01c3c57f.png)  |  ![Evaluator Tab](https://user-images.githubusercontent.com/16140783/218363114-6beeef22-7dee-4b15-8b75-3813ef2cd1fe.png)

## 📜 License
All source code is made available under a BSD 3-clause license. You can freely use and modify the code, without warranty, so long as you provide attribution to the author. See [LICENSE](./LICENSE) for the full license text.

The manuscript text is not open source. The author reserve the rights to the article content, which is currently being held for submission and publication in the UNIVAP's INIC 2023 Congress.
