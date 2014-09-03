SpecHub
=======

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>


SpecHub provides a browser interface to the Fedora git repositories storing the
spec file and patches of each packages in Fedora.

Homepage: https://github.com/fedora-infra/spechub


Get it running
==============

* Retrieve the sources::

    git clone git://github.com/fedora-infra/spechub


* Make sure you have all the dependencies listed in ``requirements.txt``


* Create the folder that will receive the forks of the git repos::

    mkdir forks


* Run it::

    ./runserver.py


This will launch the application at http://127.0.0.1:5000
