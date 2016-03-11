# Tiki Toki .csv Plugin
This is a Python script for the Tiki Toki timeline software that allows you to convert a .csv file to a file that will work with the software.

----------
## How it works
The Python script is initially configured to work with a .csv file that has the following format:

Title | Date | Intro Text | Full Description | Category | Media | Tag | Span
----  | ---- | ----       | ----             | ----     | ----  | --- | ----

The names of the columns don't matter, but the order does. To change the order, or add in your own elements, simply go to `get_events()` and change/add another `row` element.

The script reads in the values for each of these cells per event, and modifies them to work under a set of specifications. The imported values are edited as following.

`Title`, `Intro Text`, and `Full Description` have their special characters escaped, and parses user-defined keys into a desired value. For example, since Tiki-Toki supports HTML, but there isn't an easy way to tab, when `&tab` is found, it formats to `&nbsp;&nbsp;&nbsp;&nbsp;`. So put any repetitive text in the `modifiers` list in `format_text_block` and it will be parsed.



 