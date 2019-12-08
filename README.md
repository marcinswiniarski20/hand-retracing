# Robot retracing hand movements
## Authors:
* ##### Dawid Szałwiński
* ##### Marcin Świniarski
## Quick Description
This repository contains content about our thesis: "Industrial robot retracing hand movements". 
More information will be provided soon.
## Main Goal
Main goal is to create software based on computer vision, which will allow the robot to retrace movement of human hand.
## Setup
 Create conda enviroment with python 3.6:<br/>
``conda create -n env_name python=3.6``<br/>

Activate conda enviroment: <br/>
``conda activate env_name`` <br/>

Install PyTorch <br/>
``conda install pytorch torchvision cudatoolkit=10.0 -c pytorch`` <br/>

Clone our repository: <br/>
``git clone https://github.com/marcinswiniarski20/hand-retracing.git``<br/>

Install all required packages: <br/>
``cd hand-retracing && pip install -r requirements.txt``<br/>

Download weights from ``https://drive.google.com/file/d/1A3qcJnHByh0VxzxqyUmeu51IBkz8pQYl/view?usp=sharing``
and extract it to ``weights`` directory.

To run inference demo with camera available: <br/>
``python inference.py --source 0``
