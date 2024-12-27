import logging
from scss import Compiler

class SCSSCompiler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.compiler = Compiler()

    def compile(self, scss):
        self.logger.info('Compiling SCSS to CSS...')
        return self.compiler.compile(scss)
