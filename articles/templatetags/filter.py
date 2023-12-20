
from django import template
from html.parser import HTMLParser
register = template.Library()
from datetime import datetime

@register.filter(name='truncate_description')
def truncate_description(value, num):
    words = value.split()
    if len(words) > num:
        return ' '.join(words[:num]) + '...'
    return value


@register.filter(name='truncate_words')
def truncate_words(value, word_count=30):
    class ParagraphParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.data = []
            self.is_paragraph = False

        def handle_starttag(self, tag, attrs):
            if tag == 'p':
                self.is_paragraph = True

        def handle_endtag(self, tag):
            if tag == 'p':
                self.is_paragraph = False

        def handle_data(self, data):
            if self.is_paragraph:
                self.data.append(data)

    parser = ParagraphParser()
    parser.feed(value)
    paragraph_content = ' '.join(parser.data)

    words = paragraph_content.split()[:word_count]
    return ' '.join(words)




@register.filter(name='get_val')
def get_val(dictionary, key):
    return dictionary.get(key, None)


@register.filter(name='custom_date_format')
def custom_date_format(value):
    # Check if the value is a datetime object
    if isinstance(value, datetime):
        return value.strftime('%b. %d, %Y, %I:%M %p')
    return value 
