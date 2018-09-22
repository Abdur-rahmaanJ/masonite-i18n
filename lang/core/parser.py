"""
Parses a file to locate all function calls containing
translatable text and their optional params.
"""


class LanguageParser:

    kTAG_SIMPLE = "__("
    kTAG_PLURAL = "_n("

    class Param:
        sort = None
        item = None
        type = None
        content = None

        def __init__(self, sort=None, item=None, type_=None, content=None):
            self.sort = sort
            self.item = item
            self.type = type_
            self.content = content

    class Item:
        quotes = None
        begin = None
        end = None
        text = None
        params = None
        needle = None

        def __init__(
            self, quotes=None, begin=None, end=None, text=None, params=None, needle=None
        ):
            self.quotes = quotes
            self.begin = begin
            self.end = end
            self.text = text
            self.params = params
            self.needle = needle

    @staticmethod
    def get_text_between_string_tags(haystack, needle=None):

        index = 0

        if needle:
            index = haystack.find(needle, 0)

        needle = needle or ""

        begin_pos = index + len(needle)
        quotes = haystack[begin_pos]

        try:
            content = haystack[begin_pos:]
            triple = content[0] + content[1] + content[2]
            if triple == '"""' or triple == "'''":
                quotes = triple
        except IndexError:
            pass

        begin_pos = begin_pos + len(quotes)
        end_pos = haystack.find(quotes, begin_pos)

        text = haystack[begin_pos:end_pos]

        return text, begin_pos, end_pos, quotes

    @staticmethod
    def get_function_calls(haystack, needle):
        """
        This function will return an array of LanguageParser.Item
        that holds the positions and contents of each translation function found in the haystack
        :param haystack: a string with the data
        :param needle: what needs to be found
        :return: array of LanguageParser.Item
        """
        results = []
        index = haystack.find(needle, 0)

        # Maybe regex should be used instead to match __( function calls.
        # But flexibility and readability are more important.

        while index >= 0:

            haystack = haystack[index:]

            text, begin_pos, end_pos, quotes = LanguageParser.get_text_between_string_tags(
                haystack, needle
            )

            final_pos = haystack.find(")", end_pos)

            params = haystack[end_pos + len(quotes) : final_pos].split(",")

            items = []
            for sort, item in enumerate(params):

                item = item.strip()

                if not item == "":

                    item_type = "text"
                    should_split = True

                    if item.find("comment") > -1:
                        item_type = "comment"
                    elif item.find("note") > -1:
                        item_type = "note"
                    elif item.find("textdomain") > -1:
                        item_type = "textdomain"
                    else:
                        should_split = False

                    item_content = item

                    if should_split:
                        parts = item.split("=")
                        item_content = parts[1]

                    item_content = LanguageParser.get_text_between_string_tags(
                        item_content
                    )[0]

                    _param = LanguageParser.Param(
                        sort=sort - 1, item=item, type_=item_type, content=item_content
                    )

                    items.append(_param)

            _item = LanguageParser.Item(
                quotes=quotes,
                begin=begin_pos,
                end=end_pos,
                text=text,
                params=items,
                needle=needle,
            )

            results.append(_item)
            index = haystack.find(needle, index + 1)

        return results

    def parse(self, fs, filename):

        if not fs.exists(filename):
            raise FileNotFoundError(filename)

        content = fs.gettext(filename)
        get_simple = LanguageParser.get_function_calls(
            content, LanguageParser.kTAG_SIMPLE
        )
        translate_plural = LanguageParser.get_function_calls(
            content, LanguageParser.kTAG_PLURAL
        )