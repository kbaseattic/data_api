# Installation

### Local Data API Service

If you need to run the data API service locally (as opposed to against a running
servivce on CI or Production), see

- [Local Service Installation](installService.html)

### Data API JS Client

- prepare your local developer environment. The following applications are required:
    - git
    - nodejs
    - bower
    - thrift

E.g. on mac you might want to use homebrew http://brew.sh/ or macports (https://www.macports.org).

#### Brew

```
brew install git
brew install nodejs
sudo npm install -g bower
brew install thrift
```

#### Macports

```
sudo port install git
sudo port install nodejs
sudo npm install -g bower
sudo port install boost -no_static
sudo port install thrift
```

(it may not be so simple, though. There are sometimes incompatibilities, as currently, after a new Mac OS X release, and some packages may require special attention to install. E.g. the boost library needs to be installed as -no_static, because the default +no_static install conflicts with thrift and possibly other packages.)

- clone the repo

```
git clone https://github.com/eapearson/kbase-data-api-js-wrappers.git
```

- The following tasks are described using command line tools. You may use your favorite developer tools to manage the following tasks. E.g. netbeans integrates all of these tools to provide a smooth development process.

- install dependencies

```
npm install
bower install or bower update
```

- build it

```
grunt build
```

This will build not only the distribution, but also a local environment for running
demos, tests, and viewing documentation.

- A config file is generated for the runnable components, such as test and demo. In
order for this to be useful, you need to update the ```runtime/config/test.yml``` file;
    - add your own preferred ```username``` + ```password``` for testing
        - note that the ```runtime``` directory is ingored by git, so local settings will NOT be saved.
    - point to the taxon data API server of your choice
        - if this is a kbase taxon service, you'll need that url, otherwise for 
a local install, it will be the local host mapping you set up.

- Set up a local web server or use the included nodejs test server. The nodejs server
has no dependencies, so it can be run straight from the command line. 
    - open a terminal in the project, and change to the tools directory
    - fire up the server. The server will automatically point to the correct runtime
directory (```runtime/build```).

```
node server.js
```
