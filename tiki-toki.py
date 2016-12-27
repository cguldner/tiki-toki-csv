import base64
import csv
import json
import os
import re
import time
import sys
from datetime import datetime

# Defines the number of the id currently working with, to aid in error finding
NUM_ID = 1


def write_tki_file_from(csv_input_list, beautify=True):
    """
    Writes the string produced by generate_tki_string to the tki_output file
    Output file is written by default in filepath Timelines/Generated/file.csv
    TKI output file has by default form MM_DD_YY Hour-Minute

    :param list csv_input_list: Contains the different csv files desiring to convert
    :param bool beautify: Whether to beautify the outputted JSON

    .. note:: Timelines are recommended to have under 500 events, so use multiple .csv files if over
    """

    if len(csv_input_list) < 1:
        print("Usage: python <file.py> <file1.csv> <file2.csv> ...".format(csv_input_list))
        csv_input_list = input("\nEnter csv file names separated by a space: ").split(" ")

    num_files = 0
    for file in csv_input_list:
        num_files += 1
        try:
            # Check if file is empty
            if os.stat(file).st_size == 0:
                print("{} is empty".format(file))
                continue
            # Gets all the data to write to the file
            opening_metadata, event_list, closing_metadata = generate_tki_string(file)
        except (TypeError, FileNotFoundError) as error:
            print("\nNothing returned from method generate_tki_string()\nHalting execution: no .tki file produced")
            print(error)
            continue

        time_generated = time.strftime("%m_%d_%y %H-%M")
        print("Time of file generation: " + time_generated)
        # Goes to the filepath Timelines/Generated/file.csv
        tki_output = os.path.join(os.path.dirname(__file__), "Timelines", "Generated",
                                  "test {} Part {}.tki".format(time_generated, num_files))
        # Write all the data
        with open(tki_output, 'w') as output_file:
            output = ""
            output += opening_metadata

            # Iterates over list, puts indices in a list of count,event
            for count, event in enumerate(event_list):
                output += str(event)
                # Adds comma to all but the last event entered
                if count != NUM_ID - 2:
                    output += ","

            output += closing_metadata

            output = json.loads(output)
            output_file.write("var TLTimelineData = ")
            # Output the file, based on whether it should be beautified
            # TODO: Make this not mess up order
            if beautify:
                output_file.write(json.dumps(output, indent = 4))
            else:
                output_file.write(json.dumps(output))


def generate_tki_string(csv_input):
    """
    Generates the string to be written to the output file

    Includes:
        - The metadata of the file
        - The opening metadata, which includes:
            - List of valid categories with colors, in timeline_categories
            - The various relevant settings, stored in timeline_settings
            - The colors of the timeline, stored in timeline_colors
        - All of the event data, in event_list
        - The closing metadata, which includes:
            - List of valid tags, in timeline_tags
            - List of valid spans, in timeline_spans

    :param string csv_input: The name of the file to generate the .tki string from
    :rtype: tuple
    :return: metadata, eventlist
    """
    # Gets all of the different user-defined settings
    timeline_categories, timeline_tags, timeline_colors, timeline_settings = settings()

    temp_event_list, timeline_spans = get_events(csv_input)

    bc_event_list, event_list = [], []
    for count, event in enumerate(temp_event_list):
        # If " BC" is found, then add it to a separate list in order to sort it correctly
        if event.start_date.find(" BC") >= 0:
            bc_event_list.append(event)
        else:
            event_list.append(event)

    # Sorts BC events backwards by removing the BC from the date and sorting
    bc_event_list = sorted(bc_event_list, key = lambda ev: ev.start_date.strip(" BC"), reverse = True)
    # Sorts the list of events by date
    event_list = sorted(event_list, key = lambda ev: ev.start_date)
    event_list = bc_event_list + event_list
    # Puts the correct ID on each event in the sorted list
    for count, event in enumerate(event_list):
        event.id = count + 1

    for key in timeline_colors:
        # Catches invalid color codes
        try:
            Color(timeline_colors[key].strip('"'))
        except ValueError as error:
            print('\nFor "{}" in timeline_colors, {} \n'.format(key, error))

    # Escapes each string in the settings dictionary
    for key in timeline_settings:
        # Prevents images from being serialized
        if key not in ("introImage", "backgroundImage"):
            timeline_settings[key] = json.dumps(timeline_settings[key])

    # Metadata that will be printed at the beginning of the file
    opening_metadata = r'{"homePage":false' \
                       ',"showAdBlock":"false"' \
                       ',"id":1' \
                       ',"title":' + timeline_settings["title"] + \
                       ',"urlFriendlyTitle":' + timeline_settings["title"].replace(" ", "-") + \
                       ',"startDate":"{}"'.format(event_list[0].start_date) + \
                       ',"endDate":"{}"'.format(event_list[-1].start_date) + \
                       ',"introText":' + timeline_settings["introText"] + \
                       ',"aboutText":' + timeline_settings["aboutText"] + \
                       ',"authorName":""' \
                       ',"accountType":"Teacher"' \
                       ',"backgroundImage":"{}"'.format(timeline_settings["backgroundImage"].media_name) + \
                       ',"backgroundImageDataUri":"{}"'.format(
                               timeline_settings["backgroundImage"].media_data_uri[1:]) + \
                       ',"backgroundImageCredit":"{}"'.format(timeline_settings["backgroundImage"].media_credit) + \
                       ',"introImage":"{}"'.format(timeline_settings["introImage"].media_name) + \
                       ',"introImageDataUri":"{}"'.format(timeline_settings["introImage"].media_data_uri[1:]) + \
                       ',"introImageCredit":"{}"'.format(timeline_settings["introImage"].media_credit) + \
                       ',"feed":""' \
                       ',"mainColour":' + timeline_colors["mainColour"] + \
                       ',"zoom":' + timeline_settings["zoom"] + \
                       ',"initialFocus":' + timeline_settings["initialFocus"] + \
                       ',"embedHash":"7546004423"' \
                       ',"embed":"false"' \
                       ',"secret":"false"' \
                       ',"public":' + timeline_settings["public"] + \
                       ',"dontDisplayIntroPanel":' + timeline_settings["dontDisplayIntroPanel"] + \
                       ',"openReadMoreLinks":1' \
                       ',"storyDateStatus":0' \
                       ',"storySpacing":' + timeline_settings["storySpacing"] + \
                       ',"viewType":' + timeline_settings["viewType"] + \
                       ',"showTitleBlock":1' \
                       ',"backgroundColour":' + timeline_colors["backgroundColour"] + \
                       ',"storyDateFormat":"MMM ddnn, YYYY"' \
                       ',"topDateFormat":"WKD, MMMM ddnn, YYYY"' \
                       ',"sliderDateFormat":"auto"' \
                       ',"language":"english"' \
                       ',"displayStripes":' + timeline_settings["displayStripes"] + \
                       ',"htmlFormatting":1' + \
                       ',"sliderBackgroundColour":' + timeline_colors["sliderBackgroundColour"] + \
                       ',"sliderTextColour":' + timeline_colors["sliderTextColour"] + \
                       ',"sliderDetailsColour":' + timeline_colors["sliderDetailsColour"] + \
                       ',"sliderDraggerColour":' + timeline_colors["sliderDraggerColour"] + \
                       ',"headerBackgroundColour":' + timeline_colors["headerBackgroundColour"] + \
                       ',"headerTextColour":' + timeline_colors["headerTextColour"] + \
                       ',"showGroupAuthorNames":"0"' \
                       ',"durHeadlineColour":' + timeline_colors["durHeadlineColour"] + \
                       ',"cssFile":' + timeline_settings["cssFile"] + \
                       ',"altFlickrImageUrl":""' \
                       ',"fontBase":"\\"Goudy Old Style\\", Garamond, \\"Big Caslon\\", \\"Times New Roman\\", serif;"' \
                       ',"fontHead":"\\"Franklin Gothic Medium\\", \\"Franklin Gothic\\\", \\"ITC Franklin Gothic\\", Arial, sans-serif;"' \
                       ',"fontBody":"Arial, \\"Helvetica Neue\\", Helvetica, sans-serif;"' \
                       ',"lightboxStyle":' + timeline_settings["lightboxStyle"] + \
                       ',"showControls":' + timeline_settings["showControls"] + \
                       ',"lazyLoading":' + timeline_settings["lazyLoading"] + \
                       ',"expander":"2"' \
                       ',"settings3d":"' + timeline_settings["3Dstatus"] + ',' + \
                       timeline_colors["3Dcolor"] + ',' + \
                       timeline_settings["3Dzoom"] + ',' + \
                       timeline_settings["3Dpanelsize"] + ',' + \
                       timeline_settings["3Dvanishpoint"] + ',' + \
                       timeline_settings["3Dtimelinewidth"] + ',' + \
                       timeline_settings["3Ddirection"] + ',' + \
                       timeline_settings["3Dsections"] + ',' + \
                       timeline_settings["3Dbgimageopacity"] + \
                       '","bgStyle":"0","bgScale":100,"categories":['
    # Includes the categories as strings in the metadata
    for count, category in enumerate(timeline_categories):
        opening_metadata += str(category)
        if count != len(timeline_categories) - 1:
            opening_metadata += ","
    # Adds the last of the needed opening metadata
    opening_metadata += '],"feeds":[],"stories":['

    # Indents the metadata according to commas between attributes
    # opening_metadata = re.sub(re.compile(r'({|,|\[)\s?("|{)'), u"\g<1>\n\t\g<2>", opening_metadata)
    # Adds spaces after colons that are after quotes
    # opening_metadata = re.sub(re.compile(r'":'), u"\": ", opening_metadata)

    # String printed at closing_metadata of file
    closing_metadata = '\n\t],\n\t"spans": ['
    # Includes the spans as strings in the metadata
    for count, span in enumerate(timeline_spans):
        closing_metadata += str(span)
        if count != len(timeline_spans) - 1:
            closing_metadata += ","

    closing_metadata += '\n\t],\n\t"tags": ['
    # Includes the tags as strings in the metadata
    for count, tag in enumerate(timeline_tags):
        closing_metadata += str(tag)
        if count != len(timeline_tags) - 1:
            closing_metadata += ","
    closing_metadata += "\n\t]\n}"

    return opening_metadata, event_list, closing_metadata


def settings():
    """
    Reads in the categories, tags, colors, and other settings from the settings file

    :rtype: tuple
    :returns: list of the categories, list of tags, dictionary of colors, and dictionary of other settings
    """
    categories = []
    tags = []
    colors = {}
    settings = {}
    with open("settings.txt") as settings_file:
        for line in settings_file:
            line = line.strip()
            # Skip blank lines or lines starting with #
            if not line or line[0] is '#': continue
            # Advance to the next section
            if line in ("Categories", "Tags", "Colors", "Other"):
                cur_section = line
                continue

            if cur_section == "Categories":
                # Splits line based on 2 or more spaces, allows for multi-word categories
                name, color = re.split("\s{2,}", line)
                categories.append(Category(name, color.rstrip()))

            elif cur_section == "Tags":
                tags.append(Tag(line))

            elif cur_section == "Colors":
                name, color = line.split(None, 2)
                colors[name] = color

            elif cur_section == "Other":
                setting = re.split("\s{2,}", line)
                # Check that there is actually a value to the given property
                if len(setting) <= 1:
                    settings[setting[0]] = ""
                    continue
                name, value = setting
                try:
                    # TODO: change this if problem
                    value = float(value)
                except ValueError:
                    pass
                # Calls the Media constructor if it is one of the image settings
                if "Image" in line:
                    # Creates a list, and iterates over it using the list items as args
                    value = Media(*(value.replace('"', '').split(",")))
                settings[name] = value

            else:
                raise ValueError("Setting in unknown section {} in settings file".format(cur_section))

    return categories, tags, colors, settings


def get_events(csv_input):
    """
    Gets the cells of the CSV file, and puts them into their corresponding list of events
    Since spans are independent of the events, the list of spans is returned separately
    The CSV has the following format by default:

    +-------+------------+----------+------------------+----------+-------+--------+---------+
    | Title | Start Date | Subtitle | Full Description | Category | Media | Tag(s) | Span(s) |
    +=======+============+==========+==================+==========+=======+========+=========+
    |       |            |          |                  |          |       |        |         |
    +-------+------------+----------+------------------+----------+-------+--------+---------+

    Can easily be expanded to include other attributes, such as an end date

    :param string csv_input: The name of the file to generate the .tki string from
    :rtype: tuple
    :return: A list of the event data, The spans present in the timeline
    :raises ValueError: If two events have the same date
    :raises KeyError:   If a category or tag is not in the list of valid ones

    .. note:: Exceptions are handled by printing to console, and asking if user wishes to continue
    .. seealso:: Event
    """
    global NUM_ID
    # Defines the number of errors that have occurred during execution while fetching event data
    ERROR_COUNT = 0
    # What date format the events appears in the CSV as
    DATE_FORMAT = "%m/%d/%Y"
    # The string notifying how different attributes are separated
    SEPARATOR = ":: "
    # Holds the final JSON data for each event as a list item
    events = []
    spans = []

    # Get path of the current directory. Allows running the script from other directories
    csv_filepath = os.path.join(os.path.dirname(__file__), csv_input)
    with open(csv_filepath) as file:
        reader = csv.reader(file)
        # Skips the header line in the csv file
        next(reader)

        for row in reader:
            title_cell = row[0]
            start_date_cell = row[1]
            subtitle_cell = row[2]
            fulldesc_cell = row[3]
            category_cell = row[4]
            media_cell = row[5]
            tag_cell = row[6]
            span_cell = row[7]

            # Prevents having events that have no title or subtitle
            if not (title_cell and subtitle_cell): continue

            title_cell = format_text_block(title_cell)

            # Catches misformatted dates, and multiple dates that match
            try:
                bc_string = " BC" if " bc" in start_date_cell.lower() or " b.c." in start_date_cell.lower() else ""
                # Default Date format is 05/4/2012, 11/18/0020, etc.
                # Removes " BC" or any form with lower case letters/periods
                start_date_cell = datetime.strptime(re.sub(' [b|B]\.?[c|C]\.?', "", start_date_cell), DATE_FORMAT)
                # Puts date in format that timeline software desires
                start_date_cell = start_date_cell.strftime("%Y-%m-%d %H:%M:%S")
                if bc_string:
                    # Put the date in the format 2012 BC-05-18 if BC is in the date from the CSV
                    start_date_cell = start_date_cell[:4] + bc_string + start_date_cell[4:]
                # Check if there is already an event with this date
                # Can remove if desiring to have multiple events on one day
                for count, item in enumerate(events):
                    if start_date_cell == item.start_date:
                        raise ValueError("Date {} already exists at ID {}".format(start_date_cell, count + 1))
            except ValueError as error:
                ERROR_COUNT += 1
                print("ID {}: {}".format(NUM_ID, error))

            subtitle_cell = format_text_block(subtitle_cell)

            fulldesc_cell = format_text_block(fulldesc_cell)

            # Catches Categories not in the list of valid categories
            try:
                # Creates a category object out of the string defined for that event
                category_cell = Category(category_cell.strip(), valid = False).category_int
            except KeyError as error:
                category_cell = 0
                ERROR_COUNT += 1
                print(error)

            media_object = ""
            if media_cell:
                media_cell = media_cell.split(SEPARATOR)
                # Accounts for the possibility of no thumb position attribute
                thumb_pos = media_cell[2] if len(media_cell) == 3 else ""
                # Catches invalid file names
                try:
                    media_object = Media(media_cell[0], media_cell[1], thumb_pos)
                except (FileNotFoundError, ValueError, IndexError) as error:
                    print("ID {}: {}".format(NUM_ID, error))
                    ERROR_COUNT += 1

            # Splits the different tags according to comma
            tag_cell = tag_cell.split(SEPARATOR)
            tag_string = ""
            # Catches tags not present in the list of valid tags
            try:
                for count, tag in enumerate(tag_cell):
                    current_tag = Tag(tag.strip(), False)
                    # Add the tag integer to the event
                    tag_string += str(current_tag.tag_int)
                    # Add comma to all but last event
                    if count != len(tag_cell) - 1:
                        tag_string += ","
            except KeyError as error:
                ERROR_COUNT += 1
                print(error)

            # Creates the event
            event = Event(NUM_ID, title_cell, start_date_cell, start_date_cell, subtitle_cell,
                          fulldesc_cell, category_cell, media_object, tag_string)
            events.append(event)

            # Checks for misformatted dates and colors
            try:
                span_attr = span_cell.split(SEPARATOR)
                if len(span_attr) >= 6:
                    start_date = datetime.strptime(span_attr[0], DATE_FORMAT)
                    end_date = datetime.strptime(span_attr[1], DATE_FORMAT)
                    # Allows image/image credit to be left blank
                    image = "" if len(span_attr) < 7 else span_attr[6]
                    image_credit = "" if len(span_attr) < 8 else span_attr[7]
                    bg_color = Color(span_attr[3])
                    text_color = Color(span_attr[5])
                    current_span = Span(start_date, end_date, span_attr[2], bg_color,
                                        span_attr[4], text_color, image, image_credit)
                    spans.append(current_span)
                # Checks if there is 1 - 5 arguments. Prevents an error from being called on a span of 0 arguments
                elif span_attr[0] and len(span_attr) > 0:
                    print("ID {}: Not enough arguments in the span column - Should be at least 6".format(NUM_ID))
                    ERROR_COUNT += 1
            except ValueError as error:
                ERROR_COUNT += 1
                print("ID {}: For this event's span, {}".format(NUM_ID, error))

            NUM_ID += 1

            # Loop end
    # File closed

    # Checks current error count, and if any errors exist, confirm to continue execution
    if ERROR_COUNT > 0:
        print("\nOh no! The script compiled successfully, but you have {} errors to fix!".format(ERROR_COUNT))
        choice = input("Do you wish to continue? Y/N: ")
        if choice not in ("Y", "y"): return
    if ERROR_COUNT == 0: print("Successfully obtained all event data from {}. No errors.!!".format(csv_input))
    return events, spans


def format_text_block(replace_str):
    r"""
    Modifiers are defined to convert into a format that the software can understand
        - ``&tab;`` 4 n-sized spaces, essentially a tab with format &nbsp;&nbsp;&nbsp;&nbsp;
        - ``\n`` A new line character, but the software defines it as ;xNLx;
    Escapes special chars that might break the timeline software by calling json.dumps().
    Allows for further expansion

    :param string replace_str: The string that we want to replace the matches in
    :rtype: string
    :return: A string with the user defined values replaced by the timeline specific ones
    """
    # Escapes special and newline chars
    string = json.dumps(replace_str)
    # Add shorthand text you would use often in the
    # Title, Subtitle, or Description attributes
    modifiers = {
        "&tab;": "&nbsp;&nbsp;&nbsp;&nbsp;",
        "\\n"  : ";xNLx;"
    }
    for key, value in modifiers.items():
        string = string.replace(key, value)
    return string


class Event:
    """
    Holds event data for one single event

    :param int event_id: The identifier for the event. Only one event per number
    :param string title: The main name of the event
    :param string start_date: When the event started
    :param string end_date: When the event ended
    :param string subtitle: A little more insight into the event
    :param string fulldesc: The entire description of what happened during the event
    :param int category: Which category the event belongs to
    :param Media media: Optional- An image to go with the event
    :param int tag: Optional- Which tags are associated with the image
    """

    def __init__(self, event_id, title, start_date, end_date, subtitle, fulldesc, category, media, tag):
        self.id = event_id
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.subtitle = subtitle
        self.fulldesc = fulldesc
        self.category = category
        self.media = media
        self.tag = tag

    def __str__(self):
        """
        Returns event as a string that is friendly with Tiki-Toki software
        """
        return '{' + \
               '"id": {}'.format(self.id) + \
               ',"ownerId": "100"' + \
               ',"ownerName": ""' + \
               ',"title": ' + self.title + \
               ',"startDate": "{}"'.format(self.start_date) + \
               ',"endDate": "{}"'.format(self.end_date) + \
               ',"text": ' + self.subtitle + \
               ',"fullText": ' + self.fulldesc + \
               ',"category": {}'.format(self.category) + \
               ',"dateFormat": "auto"' + \
               ',"externalLink": ""' + \
               ',"media": [{}]'.format(self.media) + \
               ',"tags": "{}"'.format(self.tag) + \
               '}'


class Category:
    """
    A category consists of a user-defined name and color

    :param string str_name: Name of the category
    :param string color: What color is associated with the category
    :param bool valid: Whether the Category will be added to a list of valid categories
    :param int category_int: The integer that the category corresponds to (used in event data)
    """

    # The category ID for a category defined as one of the valid category choices
    VALID_CATEGORY_ID = 0
    # The list of valid category options
    VALID_CATEGORIES = {}

    def __init__(self, str_name, color="#FFFFFF", valid=True):
        """
        If valid is true:
            - The category must have the color defined
            - It will be used for the opening metadata
            - Category integer will be automatically assigned by the constructor
        If valid is false:
            - It will be used for individual events
            - They are brought in from the csv file
            - Name must match one of the categories in the VALID_CATEGORIES list
        """
        self.str_name = str_name
        # If a category has the valid property as true, it is going to be for the opening metadata
        if valid:
            Category.VALID_CATEGORY_ID += 1
            self.category_int = Category.VALID_CATEGORY_ID
            # Adds the category to the list of possible valid category choices
            Category.VALID_CATEGORIES[self.str_name] = self.category_int
            try:
                self.color = Color(color)
            except ValueError:
                raise ValueError('For category "{}", the color code "{}" is invalid.'.format(self.str_name, color))
        # These categories are brought in from the csv file
        else:
            # Gets the category integer from the matching entry in the VALID_CATEGORIES list
            if self.str_name in Category.VALID_CATEGORIES:
                self.category_int = Category.VALID_CATEGORIES[self.str_name]
            else:
                raise KeyError('ID {}: Category "{}" is undefined.'.format(NUM_ID, self.str_name))

    def __str__(self):
        """
        Returns the full category description, to be used in the opening metadata
        """
        return '{' + \
               '"id":{}'.format(self.category_int) + \
               ',"title":' + json.dumps(self.str_name) + \
               ',"colour":"{}"'.format(self.color) + \
               ',"layout":"0"' + \
               ',"rows":"3"' + \
               ',"order":"10"' + \
               ',"size":"10"' + \
               '}'


class Tag:
    """
    A tag consists of a user-defined name

    :param string str_name: Name of the tag
    :param bool valid: Whether the tag will be added to a list of valid tags
    :param int tag_int: The integer that the tag corresponds to (used in event data)
    """

    # Category ID for a category defined as one of the valid category choices
    VALID_TAG_ID = 0
    # The list of valid category options
    VALID_TAGS = {}

    def __init__(self, str_name="", valid=True):
        """
        If valid is true:
            - It will be used for the closing metadata
            - Its' tag integer will be automatically assigned by the constructor
        If valid is false:
            - It will be used for individual events
            - They are brought in from the csv file
            - The name must match one of the tags in the VALID_TAGS list
        """
        self.str_name = str_name
        # Inititally set to None to prevent error if no Tag is present for that event
        self.tag_int = ""
        if not self.str_name: return
        if valid:
            Tag.VALID_TAG_ID += 1
            self.tag_int = Tag.VALID_TAG_ID
            # Adds the tag to the list of possible valid tag choices
            Tag.VALID_TAGS[self.str_name] = self.tag_int
        else:
            if self.str_name in Tag.VALID_TAGS:
                self.tag_int = Tag.VALID_TAGS[self.str_name]
            else:
                raise KeyError('ID {}: Tag "{}" is undefined.'.format(NUM_ID, self.str_name))

    def __str__(self):
        """
        Returns the full tag description, to be used in the closing metadata
        """
        if not self.str_name: return ""
        return '{' + \
               '"id": {}'.format(self.tag_int) + \
               ',"text": ' + json.dumps(self.str_name) + \
               '}'


class Span:
    """
    A span is a duration of time where one encapsulating event was taking place
    Examples are Winter Vacation, time period, presidency, etc.

    :param datetime start_date: The date that the span begins
    :param datetime end_date: The date that the span ends
    :param string title: The title of the span
    :param Color bgcolor: The background color
    :param string opacity: How visible the image is behind the color
    :param Color text_color: Color of the informative text (title, dates, etc.)
    :param string image: Name of the image to serve as the background
    :param string image_credit: Any credit that might need to be given for the image
    """
    SPAN_ID = 0
    # Show the title and date info in top left corner, 0 - Enabled, 1 - Disabled
    SHOW_TEXT = 0
    # How the span appears in the actual timeline
    # 0 - Image only, 1 - Colored overlay with optional image,
    # 2 - Colored stage block with optional image
    STYLE = 2
    # Whether to show the color/image of the span in the slider, # 0 - Disabled, 1 - Enabled
    SHOW_IN_SLIDER = 1

    def __init__(self, start_date, end_date, title, bgcolor, opacity, text_color, image="", image_credit=""):
        Span.SPAN_ID += 1
        self.id = Span.SPAN_ID
        self.start_date = start_date
        self.end_date = end_date
        self.title = title
        self.bgimage = Media(image, media_credit = image_credit)
        self.bgcolor = bgcolor
        self.opacity = opacity
        self.text_color = text_color

    def __str__(self):
        return '{' + \
               '"id": {}'.format(self.id) + \
               ',"start": "{}"'.format(self.start_date) + \
               ',"end": "{}"'.format(self.end_date) + \
               ',"title": ' + json.dumps(self.title) + \
               ',"image": "{}"'.format(self.bgimage.media_name) + \
               ',"imageDataUri": "{}"'.format(self.bgimage.media_data_uri) + \
               ',"color": "{}"'.format(self.bgcolor) + \
               ',"opacity": "{}"'.format(self.opacity) + \
               ',"showText": {}'.format(Span.SHOW_TEXT) + \
               ',"textColor": "{}"'.format(self.text_color) + \
               ',"imageCredit": "{}"'.format(self.bgimage.media_credit) + \
               ',"style": {}'.format(Span.STYLE) + \
               ',"showInSlider": {}'.format(Span.SHOW_IN_SLIDER) + \
               '}'


class Media:
    r"""
    A media object is either an image or an audio file.

    A few assumptions are made about media files:
        - All image files are .jpg, all audio files are .mp3
        - All media files are stored in ``\res``
        - For audio files, the thumbnail has the same name as the audio, but with the .jpg extension

    A media object is intended to be used in 2 different ways:
        ``Media(media_name, media_caption, media_thumb_position, increment=True)``
            - This generates a media object with a filename, caption, and thumb position
        ``Media(media_name, media_credit)``
            - Intended to be used for images only
            - Used in places not in a timeline event, such as for spans or the intro

    :param string media_name: The filename of the media
    :param int media_id: Individual ID for the media - only used for media in event data
    :param string media_caption: Short sentence to describe the picture
    :param string media_thumb_position: Positioning of thumbnail when in smaller frames, default "0,0"
    :param string media_type: Either "Image" or "Audio"
    :param string external_media_thumb: ``LocalFile://"audio thumbnail name"`` for audio files, blank otherwise
    :param string external_media_type: "file" for audio files, blank otherwise
    :param string media_data_uri: The base64 encoding of the image
    :param string media_credit: Credit given for the image
    :param bool increment: Whether the creation of the media object will increment the media id

    .. note:: Due to limitations of the Chrome app sandbox, audio files must be selected via the file browser
        directly in Tiki-Toki. An audio media object will generate all the correct code, but you will
        have to reload the audio file once you are in the software
    """
    IMAGE_EXTENSION = "jpg"
    AUDIO_EXTENTION = "mp3"

    MEDIA_ID = 0

    # Each media cell is stored as
    # Medianame: Caption: thumbPosition(optional)
    def __init__(self, media_name="", media_caption="", media_thumb_position="0,0", increment=False, media_credit=""):
        self.media_name = media_name
        # Prevents empty media objects from incrementing media id, and from throwing an error
        # Also prevents this for images used anywhere else, such as in a span or the intro 
        if increment:
            # Increments the media ID
            Media.MEDIA_ID += 1
            try:
                # Gets the media filepath and tests it, assuming the file is in a folder named "res"
                open(os.path.join("res", self.media_name))
            except FileNotFoundError:
                raise FileNotFoundError('Can\'t find the media file "{}"'.format(self.media_name))

        self.media_id = Media.MEDIA_ID
        self.media_caption = media_caption
        self.media_thumb_position = self.format_thumb_position(media_thumb_position)
        self.media_type = self.get_media_type()
        # Strips the .mp3 from the file name, and append .jpg
        self.external_media_thumb = self.media_name.rsplit(".", 1)[
                                        0] + "." + Media.IMAGE_EXTENSION if self.media_type == "Audio" else ""
        self.external_media_type = "file" if self.media_type == "Audio" else ""
        self.media_data_uri = self.get_base64_encoding()
        self.media_credit = media_credit

    def __str__(self):
        """
        Turns media object into string compatible with the software.
        Only valid when using with the event data
        """
        if not self.media_name: return ""
        media_src = self.media_name
        # Appends LocalFile:// to the media source if the file is Audio
        if self.media_type == "Audio":
            media_src = "LocalFile://" + media_src
        media_str = '{' + \
                    '"id": {}'.format(self.media_id) + \
                    ',"src": "' + media_src + \
                    '","caption": "' + self.media_caption + \
                    '","type": "' + self.media_type + \
                    '","thumbPosition": "' + self.media_thumb_position + \
                    '","externalMediaThumb": "' + self.external_media_thumb + \
                    '","externalMediaType": "' + self.external_media_type + \
                    '","externalMediaId": "' + self.external_media_type + \
                    '","orderIndex": 10' + \
                    ',"mediaDataUri": ' + self.media_data_uri + \
                    '",\t"bookmarkData": ""' + \
                    '}'
        return media_str

    def get_media_type(self):
        """
        Compares file extension of the media to preset file extensions.

        :rtype: string
        :return: The media type, either 'Image' or 'Audio'
        :raises IndexError: If the file has no extension
        :raises ValueError: If the file extension is not one of the defined extensions
        """
        if not self.media_name: return ""
        try:
            media_ext = self.media_name.rsplit(".", 1)[1]
        except IndexError:
            raise IndexError("ID {}: A valid file has a file extension".format(NUM_ID))
        if media_ext == Media.IMAGE_EXTENSION:
            return "Image"
        elif media_ext == Media.AUDIO_EXTENTION:
            return "Audio"
        else:
            raise ValueError("ID {}: {} is not a valid file format".format(NUM_ID, media_ext))

    def format_thumb_position(self, thumb_pos):
        """
        Checks that thumb position argument was given in the form (float,float), and that they are in bounds [-1,1]

        :rtype: String
        :return: "x,y" , where x and y are floats
        :raises ValueError: if x or y are not between -1 and 1
        """
        if not thumb_pos:
            return "0,0"
        try:
            # Assigns the values to xpos and ypos
            xpos, ypos = thumb_pos.replace(' ', '').split(',')
            if not -1 <= float(xpos) <= 1:
                raise ValueError("ID {}: x position is out of range".format(NUM_ID))
            if not -1 <= float(ypos) <= 1:
                raise ValueError("ID {}: y position is out of range".format(NUM_ID))
        except ValueError as error:
            raise error
        return "{},{}".format(xpos, ypos)

    def get_base64_encoding(self):
        """
        Encodes the image in a base64 format to prevent the need for a filepath
        If type is audio, looks for thumbnail with the same name, different extension

        :rtype: string
        :return: Base64 encoding for the media file.
        """
        if self.media_type == "Image":
            open_media_thumbnail = open(os.path.join("res", self.media_name), "rb")
        elif self.media_type == "Audio":
            try:
                open_media_thumbnail = open(os.path.join("res", self.external_media_thumb), "rb")
            except FileNotFoundError:
                raise FileNotFoundError(
                        "ID {}: Audio file \"{}\" doesn't have accompanying thumbnail.".format(NUM_ID, self.media_name))
        else:
            return ""
        # Encodes the image, and converts it to a string
        encoding = str(base64.b64encode(open_media_thumbnail.read()))
        # Strips the quotes and the leading r
        data_uri = "\"data:image/" + Media.IMAGE_EXTENSION + ";base64," + encoding[1:].strip("\'")
        return data_uri


class Color:
    """
    A three or six digit hexadecimal number used as a color code.
    Allows for a universal way to check if color codes are valid.
    Used everywhere a color is defined for an entity.
    """

    def __init__(self, color):
        self.color = color
        # Matches valid color codes, excluding codes of only 2 characters
        if re.match('^#?(?:[0-9a-fA-F]{3}){1,2}$', color) is None:
            raise ValueError

    def __str__(self):
        return self.color


# This runs the python script
write_tki_file_from(sys.argv[1:], False)
