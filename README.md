# Tiki Toki .csv Plugin
This is a Python script for the Tiki Toki timeline software that allows you to convert a .csv file to a file that will work with the software.

----------
## How it works
The Python script is initially configured to work with a .csv file that has the following format:
Title | Date | Intro Text | Full Description | Category | Media | Tag | Span
----  | ---- | ----       | ----             | ----     | ----  | --- | ----

The names of the columns don't matter, but the order does. To change the order, or add in your own elements, simply go to `get_events()` and change/add another `row` element.

 