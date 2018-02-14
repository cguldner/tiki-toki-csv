# Tiki Toki .csv Plugin
This is a Python script for the Tiki Toki timeline software that allows you to convert a .csv file to a file that will work with the software.

 1. [Getting set up](#getting-set-up)
 2. [How it works](#how-it-works)
 3. [Assumptions](#assumptions)
 4. [Tools](#tools)

----------

## Getting set up
### Requirements
Python 3.0+

### How to use
Most of the "heavy" work is going to be making sure your CSV file is in a format that the reader is expecting. You will also need to create a *settings.txt* file, you can look at the provided file for an example.

Once this has been done, simply run the file

    python tiki-toki.py a.csv b.csv

Where a.csv & b.csv are the files you are trying to convert. You can include as many as you want.

## How it works
The Python script is initially configured to work with a .csv file that has the following format:

Title | Date | Intro Text | Full Description | Category | Media | Tag | Span
----  | ---- | ----       | ----             | ----     | ----  | --- | ----

The names of the columns don't matter, but the order does. To change the order, or add in your own elements, simply go to `get_events()` and change/add another `row` element.

The script reads in the values for each of these cells per event, and modifies them to work under a set of specifications. The imported values are edited as following.

**Title**, **Intro Text**, and **Full Description** have their special characters escaped, and parses user-defined keys into a desired value. For example, since Tiki-Toki supports HTML, but there isn't an easy way to tab, when `&tab` is found, it formats to `&nbsp;&nbsp;&nbsp;&nbsp;`. So put any repetitive text in the `modifiers` list in `format_text_block` and it will be parsed.

**Date** is first parsed according to the specified date format, which is found in `DATE_FORMAT`. By default it is `mm/dd/yyyy`.  The script also formats dates in BC correctly; the script looks for " BC" (including space), but it can be found anywhere in the string. Then, the date is checked to see if an event already exists with that date; this can be removed if multiple events on the same day is desired.

**Category** creates a `Category` object. This checks the provided category against the pre-defined list of `timeline_categories`. If it doesn't match, it will return an error. Each category in the pre-defined list is assigned a `category_int`, which is then associated with the category to the event.

**Media** creates a `Media` object. Media objects are fairly complex, so it would be best to read the documentation for them. Essentially, all media objects are either an Audio `mp3` file, or an Image `jpg`. All media files are assumed to be stored in subdirectory `res`. For an image, it is base64 encoded, and although audio files have the correct code generated, Chrome app sandbox limitations require you to reselect the audio file in Tiki-Toki's interface. In the csv, the different properties of a Media object are separated by `:: `. The properties used by the csv reader are `media_name`, `media_caption`, and `thumb_pos`. The other attributes are for other places where images are used.

**Tag** creates a `Tag` object. A `Tag` is very similar to a `Category`, in that there is a pre-defined list of `timeline_tags`, and that each is assigned a unique id. However, an element can have multiple tags, separated by `:: `.

**Span** creates a `Span` object. These are not linked to a specific event, but are used as a period of time, such as a stage of life, a prehistoric time period, etc. The different attributes are separated by `:: `

An `Event` takes all of the above information (besides `span`) and assembles it into a Tiki-Toki readable format. The `Event` isn't necessarily part of an event, but it allows the data from an event to be used in other places.

All of the objects have a fairly decent documentation for you to learn more about what their purpose is and how to use them.

----------

## Assumptions

 1. All images have `.jpg` extension, and all audio files have `.mp3` extensions
 2. All audio files are stored in `\res`
 3. Multiple events on the same day are not desired
 4. Date format is `mm/dd/yyyy`, e.g. `09/30/2014`
 5. Timelines are outputted to `Timelines\Generated`
 6. The attribute separator is `:: `

----------

## Tools
**Sort_and_Export.bas** - This is an Microsoft Excel VBA Bash script for use with an .xlsm file that does a couple different functions.

 - Sorts the entries based on the date
 - Autofits the cells
 - Allows the user to enter in the name of the .csv file
 - Checks if file already exists and verifies overwriting
 - Exports the .xlsm as a .csv file
