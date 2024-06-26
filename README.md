# Man Page Server

View your local man pages in the browser.

https://github.com/Castersen/man_server_python/assets/90943238/7d9e031b-f1c7-4466-ac3b-1f24c182e471

Supports various themes, follows links, caches converted pages, shows potential man pages if section is wrong.

## Dependencies 

<b>Linux</b>  
man2html  
man  

<b>Mac</b>  
mandoc  
man  

## How to use

`python3 man_server.py`  

By default this starts up a TCP server at port 8000,
from there you can open your browser and direct it to <b>localhost:8000</b> and begin browsing man pages.

To change the port

`python3 man_server.py -p [port]`

To change the theme

`python3 man_server.py -t [theme]`

To see all options

`python3 man_server.py -h`

## Themes

<b>default</b>: This is a simple black and white terminal style theme and is the theme used if `-t` is not set

<img src="showcase/dark-theme.png">

<b>light</b>

<img src="showcase/light-theme.png">

## Creating New Themes

Simply navigate to the themes directory, and copy one of the existing themes, renaming it to whatever you would like the new theme to be called. Then modify the css file save it and run:

`python3 man_server.py -t [new_theme_name]`

Of course you can just generate your own css file from scratch but modifying one of the existing ones gives a better idea of what parts should be modified. Ultimately, have fun!

## Internals

Converting the man pages to html is done by <b>mandoc</b> (mac) or <b>man2html</b> (linux) the pages themselves are found using <b>man -wa</b> and then parsing the output for the correct section. Every time a page is converted it is stored in the cache directory and subsequently retrieved from there.

The output is then post processed before being sent to the client. This involves reading the index to generate the side view for easy access. Then <b>template.html</b> is read and the relevant parts of the man page are placed in the template. This is where the themes are loaded.

The server simply makes calls to <b>man_parser.py</b> after receiving a request with a valid query. If an invalid query is received the server sends a page with the appropriate error message. If man_parser was able to find potential man pages, i.e. you put the correct name but wrong section it will return a `Potential` object with a `__str__` method containing the potential man pages. This will be shown. If no query is received the server displays <b>startup_page.html</b>.

## Tests

Tests are found in <b>test.py</b> they should only be run when the server is not running. An instance of the server is spawned and requests are sent to it to verify that it is working. Calls are also made to the man_parser.

To run tests:

`python3 tests.py`
