Setup
==============

Installation
------------

WorldNavigator has a package for easy integration with Ren'Py, just download the latest version of the package found `here`_.


1. Download the latest version of the package `here`_.
2. Unzip the package and copy all the files inside the ``worldnavigator`` folder to your ``game`` folder.
3. That's it.

.. _here: https://github.com/IkarosKurtz/WorldNavigator/releases

Integration
-----------

Once you have the package installed, you need more steps depending if was installed on a new or existing project.

New Project
^^^^^^^^^^^

If you are starting a new project, you will notice a ``special_labels.rpy`` file in your ``game`` folder, this file contains special labels, see :doc:`/source/renpy/components/labels` for more information.

In this file you will find a label called ``after_load`` which is not defined when you start a new project. If you don't plan to use it, you can ignore this file. However, it's important to note that **this label is used to initialize WorldNavigator with your save data**, as explained in :ref:`After Load Label`.


Existing Project
^^^^^^^^^^^^^^^^
