Installing WorldNavigator
=========================

Getting Started
---------------

WorldNavigator can be installed using pip, the Python package manager. Follow these simple steps to get started:

1. Requirements
^^^^^^^^^^^^^^^

* Python 3.8 or higher
* pip (Python package manager)

2. Installation
^^^^^^^^^^^^^^^

Run the following command in your terminal:

.. code-block:: bash

   pip install worldnavigator

Alternatively, you can install from source:

.. code-block:: bash

   git clone https://github.com/your-username/worldnavigator.git
   cd worldnavigator
   pip install -e .

3. Verification
^^^^^^^^^^^^^^^

To verify that WorldNavigator was installed correctly, run:

.. code-block:: python

   import worldnavigator
   print(worldnavigator.__version__)
