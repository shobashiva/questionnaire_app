### Requirements<name-for-your-virtual-env>

Before starting, make sure you have the following installed:

* PostgreSQL
* libffi
* npm
  * `npm install -g gulp-cli`
* python3
* RabbitMQ
* pip
* It's recommended to use a virtual environment for dependencies.  On Mac OS:
    * `sudo pip install virtualenv`
    * `sudo pip install virtualenvwrapper`
    * Finally, add the following to your `~/.bash_profile`:
        * `source /usr/local/bin/virtualenvwrapper.sh`

### Dependencies
As mentioned, it's recommended to use a virtual environment for the project dependencies.  This will prevent your local python installation from getting clouded with dependencies that might not jive with other projects.  It also makes it easy to mymic different deployment environments.  For example:

```bash
$ mkvirtualenv <name-for-your-virtual-env> --python <path-to-python3>
New python executable in <name-for-your-virtual-env>/bin/python
Installing setuptools, pip...done.
(<name-for-your-virtual-env>)$ 
```

You can disable the virtual environment by running `deactivate` and re-enable with `workon <name-for-your-virtual-env>`.

Lastly, install the dependencies from the root directory:
```bash
(<name-for-your-virtual-env>)$ pip install -r requirements.txt
```

### Database Setup
First, copy the template for local settings:

```bash
(<name-for-your-virtual-env>)$ cd /pcusa_process_observation/settings
(<name-for-your-virtual-env>)$ cp local-dist.py local.py
```

Edit `local.py` to reflect the settings for a newly created database.

Initialize the database from the root directory:

```bash
(<name-for-your-virtual-env>)$ ./manage.py syncdb
```

### Site Resource Dependencies
The webapp uses the `npm` module `gulp` for css and javascript pre-processing.  To get setup run the following commands: (It is recommended to run these commands in a separate terminal so that the gulp "watch" tasks can run continuously.  This way if you make changes to the .less files, they will automatically be recompiled

```bash
$ npm install -g gulp-cli
$ cd base/static
$ npm install
$ gulp default
```

Since this app uses the EmailAsUsername module, instead of running Django's default createsuperuser method, follow the instructions here:
https://github.com/harmo/django-email-as-username#creating-users
for creating users through shell_plus

### Running the Server
Finally, './manage.py runserver' should get your local server up and running (if you have gulp watch tasks running, use a different terminal window)