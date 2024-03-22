################
Installation
################

.. contents:: Table of Contents


*********************
Package Requirements
*********************

.. literalinclude:: ../../../requirements/requirements.in

****************
CI Requirements
****************

.. literalinclude:: ../../../requirements/requirements_dev.in

*************
Installation
*************

From source

.. code-block:: bash

    git clone git@bitbucket.org:3rdplace/ travelagent.git
    cd "$(basename "git@bitbucket.org:3rdplace/ travelagent.git" .git)"
    make install
