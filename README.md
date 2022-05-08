
# Example result
![](https://github.com/giulionf/birdwatch/blob/main/readme/demo.gif)

# Getting Started
## Creating a email sender
1. Create a Googlemail Account
2. Enable insecure Apps under https://www.google.com/settings/security/lesssecureapps

## Setting up the environment
1. Create a new python 3.7 environment (e.g. with conda, as follows):
    ```
    conda create -n birdwatch python==3.7
    conda activate birdwatch
    ```
2. Install the requirements
    ```
    pip3 install -r requirements.txt 
    ```
3. It might be necessarry to install opencv separately for conda
    ```
    conda install -c conda-forge opencv
    ```

## Executing the program
```
python main.py --rtsp_url [VIDEO_STREAM_URL] --sender_mail [BOT_EMAIL] --sender_pw [BOT_EMAIL_PW] --recipient_mails [RECIPIENT1] [RECIPIENT2]
```
