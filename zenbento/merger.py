import logging
import tinycss2
from zenbento import bentoscss as scss # pylint: disable=E0401
from tinycss2 import ast as css_ast
from urllib.parse import urlparse

comment = "/*\n" \
    "{signature}\n\n" \
    "Packaged by Bento (https://github.com/greeeen-dev/zenbento.py)\n" \
    "*/"

class Merger:
    def __init__(
            self, logger: logging.Logger, name: str, author: str, version: str, source: str = None,
            oss_license: str = None
    ):
        self.logger = logger
        self.scss = scss.SCSSCompiler(logger)
        self.name = name
        self.author = author
        self.version = version
        self.source = source
        self.oss_license = oss_license

    @property
    def signature(self):
        text = f'{self.name} by {self.author}\nVersion {self.version}'
        if self.source:
            text += f'\n{self.source}'
        if self.oss_license:
            text += f'\n\n{self.oss_license}'
        return text

    def merge(self, file: str, recursion: int = 0):
        uses_scss = False
        recursive_string = ' ' * recursion
        self.logger.info(f'{recursive_string}Merging {file}...')

        path = file[:-len(file.split('/')[len(file.split('/')) - 1])]

        # Open file and read rules
        with open(file, 'r') as f:
            contents = f.read()
            if file.endswith('.scss'):
                uses_scss = True
                contents = self.scss.compile(contents)

            rules = tinycss2.parse_stylesheet(contents, skip_comments=True, skip_whitespace=True)

        # Iterate through rules
        for index in range(len(rules)):
            rule = rules[index]

            if type(rule) is not css_ast.AtRule or rule.at_keyword != 'import':
                continue

            if type(rule.prelude[1]) is css_ast.FunctionBlock:
                source = rule.prelude[1].arguments[0].value
            else:
                # assume type is StringToken
                source = rule.prelude[1].value

            try:
                # if this is a URL, this should be left as-is so the URL can be moved to
                # the start of the file later
                parsed = urlparse(source)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError()
            except:
                rules[index], scss = self.merge(path + source, recursion + 1)
                uses_scss = uses_scss or scss
            else:
                if uses_scss:
                    self.logger.error(f'{recursive_string}SCSS files cannot be imported from URLs. Please use ')
                    raise ValueError()

        # Remove nested lists
        merged_rules = []
        for index in range(len(rules)):
            rule = rules[index]

            if type(rule) is list:
                merged_rules.extend(rule)
            else:
                merged_rules.append(rule)

        # Reorder imports
        final_rules = []
        imports = 0
        for rule in merged_rules:
            if type(rule) is css_ast.AtRule and rule.at_keyword == 'import':
                final_rules.insert(imports, rule)
                imports += 1
            else:
                final_rules.append(rule)

        self.logger.info(f'{recursive_string}Merged {len(final_rules)} rules from {file}')

        if recursion == 0:
            self.logger.info(f'{recursive_string}Serializing CSS...')
            result = tinycss2.serialize(final_rules)
            result = comment.format(signature=self.signature) + '\n' + result
        else:
            result = final_rules

        return result, uses_scss
