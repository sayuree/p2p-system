



How to launch server:

1) open terminal
2) Go to the folder of application
3) type "python new_server.py"

How to open GUI for peer:

1) open terminal
2) Go to the folder of application
3) type "python client.py"
4) For launching other peers, just repeat step 3

------------------------------------------------

Folders:

    "peer_downloaded" contains downloaded files of each peer from other peers 
    when peer would be created, its port number as a individaul folder would be 
    initiated in "peer_downloaded" 

    "CLIENT_FILES" contains 11 images

    when peer is launched, it just takes random number (up to 5) of images from "CLIENT_FILES"
    and assign to itself

    It might be a case, that peer can take zero number of images from "CLIENT_FILES" so 
    that, we can see a case of rejection from server 

