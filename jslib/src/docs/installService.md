# Installing Data API Service for Dev Usage

- set up a vm
    - create vm

    ```
    mkdir service
    cd service
    vagrant init ubuntu/trusty64
    ```

    - get data_api

        ```
        git clone -b develop https://github.com/eapearson/data_api.git
        ```

    -  edit Vagrantfile and add the networking line

        ```
        config.vm.network "private_network", type: "dhcp"
        ```

    - and enable and edit the virtualbox provider section so that it looks like this:

            ```
            config.vm.provider "virtualbox" do |vb|
                 vb.memory = "2048"
            end
            ```    

    - Finally, bring up vagrant and go in:

        ```
        vagrant up
        vagrant ssh
        ```

- update vm system

    ```
    sudo su
    apt-get update
    apt-get upgrade
    apt-get dist-upgrade
    ```

    - If anything happened in dist-upgrade, exit, then vagrant reload.

- install system dependencies:

    ```
    apt-get install nginx-extras
    apt-get install libfreetype6-dev
    apt-get install pkg-config
    ```

- install thrift

    Although the thrift docs give some manual steps for installing thrift, and the Ubuntu distro is a little out of date, the ubuntu distro does work (perhaps a PPA is more up to date.)

    ```
    apt-get install thrift-compiler
    ```

- install python extra tools:

    ```
    apt-get install python-dev
    apt-get install python-setuptools
    apt-get install python-pip
    pip install --upgrade pip
    ```

    - the latter solves a problem with pandas install

- install python dependencies

    ```
    cd /vagrant/data_api
    pip install -r requirements.txt
    ```

    - relax, this takes a while, as there are many c binaries to compile and install.
    - I could not get numpy to install with python setup.py install, so had to use pip.

-  You can drop out of root now.

- if not using branch with http service, install 

    ```lib/doekbase/data_api/tests/taxon_service_http_binary_driver.py```

    from the same named sample file found here.

- generate python thrift pieces and install in the proper location.

    ```
    mkdir temp
    thrift --gen py:new_style -out temp thrift/specs/taxonomy/taxon/taxon.thrift
    cp -pr temp/taxon/* lib/doekbase/data_api/taxonomy/taxon/service
    ```

    - Thrift will install the generated files in ```taxon``` into whichever "out" directory you specify. However, data_api expects it to be in ```lib/doekbase/data_api/taxonomy/taxon/service```.

    - Therefore we can't just generate the files and point them to the correct location. So we generate them in a temp location and then copy them.

- regenerate the egg

    ```
    sudo python setup.py install
    ```

- set up nginx

    - edit the default config

    ```
    sudo vi /etc/nginx/sites-enabled/default
    ```

    - replace the content with the sample "nginx_config.conf" file found here

    - this sets up CORS and the reverse proxy.

    - restart nginx

    ```
    sudo service nginx restart
    ```

- start the thrift service

    ```
    python lib/doekbase/data_api/tests/taxon_service_http_binary_driver.py
    ```

- map ```euk.kbase.us``` to the server

    - on your local dev host, you'll need to map the euk.kbase.us (or whatever 
host name you want to use) host to the IP of the VM:
    - in the vm issue
    
    ```
    ifconfig
    ```

    - note the ipaddress for eth1.

    - in the local dev host (mac) edit the hosts file

    ```
    sudo vi /etc/hosts
    ```

    - at the end of the file place

    ```
    IP euk.kbase.us
    ```

    where IP is the ip address you noted above.

## TODO

- use nginx extra headers to allow CORS to work with 502s - DONE
- startup binary over http service


## FIN

<style type="text/css">
    body {
        font-family: sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        xcolor: #FFF;
        color: blue;
    }
    h3 {
        padding: 4px;
        background-color: gray;
        color: #FFF;
    }
     code {
        xmargin: 1em;
        xdisplay: block;
        xpadding: 1em;
        xcolor: lime;
        background-color: #CCC;
    }
    pre > code {
        font-size: 80%;
        margin: 1em;
        display: block;
        padding: 1em;
        color: lime;
        background-color: black;
    }
</style>