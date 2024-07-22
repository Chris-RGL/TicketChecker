This project was created to assist TSD workers at the UO. The purpose of this project is to determine wether there is a ticket object present in the HTML code of a website. 

HOW IT WORKS:
When the program is started 2 windows open, one is visible to the user and the other is opened on a seperate thread hidden from the user
The first window takes login information from the user and stores it for use on the second window
The first window is then closed and the second window is autopopulated with the login info obtained
The second window continues through several different prompts until a DUO window is presented
The number presented from the DUO window is scraped from the HTML and given to the user
Once approving DUO the second window checks the HTML of the site every 60 seconds looking for a specific tag indicating there is a ticket present
