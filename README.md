## The deployment of project
##### Set project settings
1. Move to project directory
2. The copy of file .env.example rename to .env
3. The copy of file rozetka.db.example rename to rozetka.db
4. Change settings in .env file:
    * set telegram bot token;
    * set chat ids of telegram users separated by commas;
    * set page link for scrapping.
##### Set environment
1. Install virtual environment in project directory
    ```
    python3.7 -m venv env
    ```
2. Install requirements.txt
    ```
    python3.7 -m pip install -r requirements.txt
    ```
3. Test project
   ```
   python3.7 main.py
   ```
##### Set systemd service
1. Copy file rozetka.service to directory /etc/systemd/system
2. Reload daemon, enable and start service
   ```
   systemctl daemon-reload
   systemctl enable rozetka.service
   systemctl start rozetka.service
   ```
3. Once project files are changed reload daemon and restart service
   ``` 
   systemctl daemon-reload
   systemctl restart rozetka.service
   ```


