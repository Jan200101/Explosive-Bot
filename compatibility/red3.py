from sys import modules
from typing import Sequence
from pathlib import Path
import re

from __main__ import bot
from discord.ext import commands

class CogI18n:
    def __init__(self, name, file_location):
        self.cog_folder = Path(file_location).resolve().parent
        self.cog_name = name
        self.translations = {}

        _i18n_cogs.update({self.cog_name: self})

        self.load_translations()

    def __call__(self, untranslated: str):
        normalized_untranslated = _normalize(untranslated, True)
        try:
            return self.translations[normalized_untranslated]
        except KeyError:
            return untranslated

    def load_translations(self):
        self.translations = {}
        translation_file = None
        locale_path = get_locale_path(self.cog_folder, 'po')
        try:

            try:
                translation_file = locale_path.open('ru', encoding='utf-8')
            except ValueError:  # We are using Windows
                translation_file = locale_path.open('r', encoding='utf-8')
            self._parse(translation_file)
        except (IOError, FileNotFoundError):  # The translation is unavailable
            pass
        finally:
            if translation_file is not None:
                translation_file.close()

    def _parse(self, translation_file):
        self.translations = {}
        for translation in _parse(translation_file):
            self._add_translation(*translation)

    def _add_translation(self, untranslated, translated):
        untranslated = _normalize(untranslated, True)
        translated = _normalize(translated)
        if translated:
            self.translations.update({untranslated: translated})

def box(text: str, lang: str = ""):
    ret = "```{}\n{}\n```".format(lang, text)
    return ret

def escape(text: str, *, mass_mentions: bool = False,
           formatting: bool = False):
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = (text.replace("`", "\\`")
                .replace("*", "\\*")
                .replace("_", "\\_")
                .replace("~", "\\~"))
    return text

def pagify(text: str,
           delims: Sequence[str] = ["\n"],
           *,
           priority: bool= False,
           escape_mass_mentions: bool=  True,
           shorten_by: int = 8,
           page_length: int = 2000):

    in_text = text
    page_length -= shorten_by
    while len(in_text) > page_length:
        this_page_len = page_length
        if escape_mass_mentions:
            this_page_len -= (in_text.count("@here", 0, page_length) +
                              in_text.count("@everyone", 0, page_length))
        closest_delim = (in_text.rfind(d, 1, this_page_len)
                         for d in delims)
        if priority:
            closest_delim = next((x for x in closest_delim if x > 0), -1)
        else:
            closest_delim = max(closest_delim)
        closest_delim = closest_delim if closest_delim != -1 else this_page_len
        if escape_mass_mentions:
            to_send = escape(in_text[:closest_delim], mass_mentions=True)
        else:
            to_send = in_text[:closest_delim]
        if len(to_send.strip()) > 0:
            yield to_send
        in_text = in_text[closest_delim:]

    if len(in_text.strip()) > 0:
        if escape_mass_mentions:
            yield escape(in_text, mass_mentions=True)
        else:
            yield in_text

def _normalize(string, remove_newline=False):
    def normalize_whitespace(s):
        if not s:
            return str(s)  # not the same reference
        starts_with_space = (s[0] in ' \n\t\r')
        ends_with_space = (s[-1] in ' \n\t\r')
        if remove_newline:
            newline_re = re.compile('[\r\n]+')
            s = ' '.join(filter(bool, newline_re.split(s)))
        s = ' '.join(filter(bool, s.split('\t')))
        s = ' '.join(filter(bool, s.split(' ')))
        if starts_with_space:
            s = ' ' + s
        if ends_with_space:
            s += ' '
        return s

    string = string.replace('\\n\\n', '\n\n')
    string = string.replace('\\n', ' ')
    string = string.replace('\\"', '"')
    string = string.replace("\'", "'")
    string = normalize_whitespace(string)
    string = string.strip('\n')
    string = string.strip('\t')
    return string

def _parse(translation_file):
    """
    Custom gettext parsing of translation files. All credit for this code goes
    to ProgVal/Valentin Lorentz and the Limnoria project.
    https://github.com/ProgVal/Limnoria/blob/master/src/i18n.py
    :param translation_file:
        An open file-like object containing translations.
    :return:
        A set of 2-tuples containing the original string and the translated version.
    """
    step = WAITING_FOR_MSGID
    translations = set()
    for line in translation_file:
        line = line[0:-1]  # Remove the ending \n
        line = line

        if line.startswith(MSGID):
            # Don't check if step is WAITING_FOR_MSGID
            untranslated = ''
            translated = ''
            data = line[len(MSGID):-1]
            if len(data) == 0:  # Multiline mode
                step = IN_MSGID
            else:
                untranslated += data
                step = WAITING_FOR_MSGSTR

        elif step is IN_MSGID and line.startswith('"') and \
                line.endswith('"'):
            untranslated += line[1:-1]
        elif step is IN_MSGID and untranslated == '':  # Empty MSGID
            step = WAITING_FOR_MSGID
        elif step is IN_MSGID:  # the MSGID is finished
            step = WAITING_FOR_MSGSTR

        if step is WAITING_FOR_MSGSTR and line.startswith(MSGSTR):
            data = line[len(MSGSTR):-1]
            if len(data) == 0:  # Multiline mode
                step = IN_MSGSTR
            else:
                translations |= {(untranslated, data)}
                step = WAITING_FOR_MSGID

        elif step is IN_MSGSTR and line.startswith('"') and \
                line.endswith('"'):
            translated += line[1:-1]
        elif step is IN_MSGSTR:  # the MSGSTR is finished
            step = WAITING_FOR_MSGID
            if translated == '':
                translated = untranslated
            translations |= {(untranslated, translated)}
    if step is IN_MSGSTR:
        if translated == '':
            translated = untranslated
        translations |= {(untranslated, translated)}
    return translations

def get_locale_path(cog_folder: Path, extension: str):
    return cog_folder / 'locales' / "{}.{}".format(get_locale(), extension)

def get_locale():
    return _current_locale

_current_locale = 'en_us'
_i18n_cogs = {}

WAITING_FOR_MSGID = 1
IN_MSGID = 2
WAITING_FOR_MSGSTR = 3
IN_MSGSTR = 4

MSGID = 'msgid "'
MSGSTR = 'msgstr "'

class redbot:
    # I find strong disgust in the way Red Version 3 functions are Loaded"
    class core:
        commands = commands
        """
        https://www.strawpoll.me/15341645
        Red Version 3 may get its own command soon
        preparing for that
        """

        class i18n:
            CogI18n = CogI18n
        class utils:
            class chat_formatting:
                box = box
                pagify = pagify


modules['redbot'] = redbot
modules['redbot.core'] = redbot.core
modules['redbot.core.i18n'] = redbot.core.i18n
modules['redbot.core.i18n.CogI18n'] = redbot.core.i18n.CogI18n
modules['redbot.core.utils'] = redbot.core.utils
modules['redbot.core.utils.chat_formatting'] = redbot.core.utils.chat_formatting
