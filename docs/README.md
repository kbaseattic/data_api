# Data API documentation
This is the documentation directory. The documentation is built using Sphinx.

## Build documentation

To rebuild/install the documentation use the Makefile in this directory. Giving the command `make` with no options will list all possible options.

## Edit documentation

Edit the `.rst` files with the editor of your choice. See the Sphinx documentation for details on how Sphinx works. Note that there are custom templates and CSS files in subdirectories. See `conf.py` for the main configuration.

### Live preview

If you want to get a 'live preview' of Sphinx docs as you edit the `.rst` files, do the following. In your Python environment, install the `sphinx-autobuild` package:

    pip install sphinx-autobuild 
    
Then, every time you want to edit the documentation, first run this command:

    sphinx-autobuild . _build/html 
    
Then open the URL http://127.0.0.1:8000 on your browser. Every time you save a change to a file it will automatically rebuild the docs and update the web pages.