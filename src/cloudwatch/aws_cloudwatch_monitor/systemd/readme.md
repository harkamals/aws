## Setup systemd sceduled task
* Copy file to /usr/local/aws-cloudwatch-monitor
    ```
    aws-cloudwatch-monitor
    ``` 
* Copy files to /etc/systemd/system/
    ```
    aws-cloudwatch-monitor.service
    aws-cloudwatch-monitor.timer
    ``` 

* Run the following commands,
    ```
    sudo systemctl enable aws-cloudwatch-monitor.service
    sudo systemctl enable aws-cloudwatch-monitor.timer
    sudo systemctl start aws-cloudwatch-monitor.service
    sudo systemctl start aws-cloudwatch-monitor.timer
    
    systemctl list-timers --all
    ```

* Enjoy your metric on AWS CloudWatch