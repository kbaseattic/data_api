# JavaScript API Wrappers for the Data API

The JavaScript 

- install local service
- generated api docs
- examples

## Installation

1. Clone the GitHub repository

Follow instructions at: https://github.com/kbase/data_api

2. Update JavaScript dependencies

    a. Change to the `jslib` directory and run the Node Package Manager (npm). 
    This downloads and installs a bunch of things, so it will take a couple of 
    minutes the first time, and create many screenfulls of output.
    
        cd jslib
        npm install
        
    b. Change to the top-level director and run `bower`
### Local Data API Service

If you need to run the data API service locally (as opposed to against a running
servivce on CI or Production), see the docs.

### Data API JS Client

- Clone this repo


## Usage

These notes may be a bit out of date, hang on.

- prepare dev env
    - git
    - nodejs
    - bower
    - thrift
    
- clone the repo
- update dependencies
    - npm install
    - bower install or bower update
- build it
    - grunt build
- update the runtime/config/test.yml file:
    - add your own preferred username + password for testing
    - point to the taxon data api server of your choice
    - etc.
- run grunt build again to copy the new config file into the build
    - subsequent builds will not touch the edited runtime/config/test.hml file
- if you need to, stand up a taxon service somewhere and point your config to it, rebuild.


## Testing

Testing is configured for Karma and Jasmine. Code coverage not currently set up. All test artifacts are in the test directory.
Tests operate against the built product in runtime/build.

To test from this directory:

```
karma start test/karam.conf.js
```

Tests are set up to run against Chrome, Firefox, Safari, and PhantomJS. I can't confirm PhantomJS, because it is not currently working. There are JS compatability bugs in PhantomJS < 2.0, but 2.0 does not build on El Capitan at the moment (qt5 compatiblity issues...)

### TODO

- write more tests!