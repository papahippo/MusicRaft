MusicRaft
=========

'MusicRaft' is an GUI for the ABC(plus) music notation. Its implementation went through a few incarnations:

- at first it was a wxpython GUI (a bit like the current easyABC which didn't exist at the time)
 - later I re-implemented it a Geany plugin. Recurrent problems with getting Geany python plugins workings on windows led
 me to abandon that approach.

 Musicraft is now built around PyQt (or alternatively PySide). It is in fact a very lightweight (and very limited!) IDE
 implemented as 'the raft' on top of which the plugin 'abcraft' is created.

![Alt text](./screenshots/Musicraft_017.png?raw=true "Editing ABCplus music source while viewing graphical ouput")

A separate plugin 'pyraft' supports editing of python3 source files. When a python script writes output with an HTML header,
pyraft dsiplays the HTML in a special 'Html' tab within  the display notebook.

![Alt text](./screenshots/Musicraft_017.png?raw=true "Editing python progam source while viewing HTML ouput")


