=====
uterm
=====

A micropython-friendly terminal.

Just run ``uterm`` to start.

Bring up a menu with ``esc`` where you can:

- upload files
- browse remote files (``del`` to delete)

Quit from the menu or ``ctrl-a``, ``ctrl-q``.

.. image:: demo.gif
   :alt: Demo of uterm running

Some basic command line functions have also been added
(run ``uterm --help`` for details)::

    uterm ls
    uterm get FILE
    uterm exec COMMAND
