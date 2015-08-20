# Phabricator Generic Task Server for Jetbrains (PhpStorm, PyCharm, etc.)

We love [PyCharm](https://www.jetbrains.com/pycharm/) and [PhpStorm](https://www.jetbrains.com/phpstorm/). We also love [Phabricator](http://phabricator.org/). Currently there is no support for [Phabricator](http://phabricator.org/) in the [JetBrains](https://www.jetbrains.com/) products so we made our quick hack using the [Generic Task Server](https://www.jetbrains.com/idea/help/servers-2.html) implementation.

Now we can have Tasks inside PyCharm / PhpStorm:

![open task](https://raw.githubusercontent.com/Newsman/phabricator-jetbrains-generic-task-server/master/assets/open_task.png)

## Configure the Generic Task Server inside your IDE

1. Go to `Tools > Tasks & Contexts > Configure Servers` and add a new `Generic` server type.
2. Enter your Phabricator url, username and password (conduit certificate)
3. Make sure you check HTTP Authentication
4. Configure the Server in `Server Configuration` tab (JSONPath, tasks / task urls)

![generic server general configuration tab](https://raw.githubusercontent.com/Newsman/phabricator-jetbrains-generic-task-server/master/assets/server_configuration_general.png)
![generic server configuration tab](https://raw.githubusercontent.com/Newsman/phabricator-jetbrains-generic-task-server/master/assets/server_configuration.png)

## Apache WSGI application configuration

Include in your VirtualHost WSGI code to start the server.
```
    WSGIDaemonProcess phab_task_server user=www-data group=www-data threads=5
    WSGIScriptAlias / /home/catalin/work/PhabGenericTaskServer/server.wsgi
    WSGIPassAuthorization On

    <Directory /home/catalin/work/PhabGenericTaskServer>
        WSGIProcessGroup phab_task_server
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
```

## Instal the requirements

```bash
pip install -r requirements.txt
```

## Task server `config.py`

The only config you have to make is the Phabricator url inside `config.py`. Update `PHAB_API_URL`.

# License

This code is released under [MIT License](https://github.com/Newsman/phabricator-jetbrains-generic-task-server/blob/master/LICENSE) by [NewsmanApp - Smart Email Service Provider](https://www.newsmanapp.com).
