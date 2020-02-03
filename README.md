# Sample Code for Cisco Collaboration xAPI Usage -- Estimating Meeting Room Utilization

Python version required: 3.7 or newer.


## Description

This code is for testing Cisco xAPIs for customers to play around with. It is meant as a starting point for figuring out how to use these APIs and wed them with other APIs, such as those for Microsoft Exchange. It is built off of the pyxows Cisco Collaboration xAPI Python library, and the script is the "RoomUtilization.py" file.


## Installing

Make sure you setup pyxows (the necessary code is included in this repo, so this command is all that is needed)

    python setup.py install [--user]

And then you can run the script with:

    python RoomUtilization.py

Note that the code will error out if you do not change the required input variable information in the file. The code almost certainly will produce errors even with proper input values, as I was unable to test it since I don't have access to a Microsoft Exchange server to test my API usage.