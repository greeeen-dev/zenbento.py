import os
import sys
import json
import logging
import shutil
from zenbento import logger, merger, bentoscss as scss

args = sys.argv[1:]
logger = logger.buildlogger('zenbento', 'merger', logging.DEBUG)

class BentoReturn:
    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message

def package(config: dict):
    try:
        m = merger.Merger(
            logger, config['package']['name'], config['package']['author'], config['package']['version'],
            source=config['package'].get('source'), oss_license=config['package'].get('license')
        )
    except KeyError:
        return BentoReturn(False, 'Your bento.json file is missing required fields.')

    scss_compiler = scss.SCSSCompiler(logger)

    if not config['package']['include']:
        return BentoReturn(False, 'You didn\'t provide any components to package.')

    if not os.path.exists('.zenbento'):
        os.mkdir('.zenbento')
    if not os.path.exists('.zenbento/package'):
        os.mkdir('.zenbento/package')
    else:
        for file in os.listdir('.zenbento/package'):
            os.remove(f'.zenbento/package/{file}')

    for component in config['package']['include']:
        if component == 'userChrome':
            userchrome, uses_scss = m.merge('userChrome.css')
            if uses_scss:
                userchrome = scss_compiler.compile(userchrome)
            with open('.zenbento/package/userChrome.css', 'w+') as f:
                f.write(userchrome)
        elif component == 'userContent':
            usercontent, uses_scss = m.merge('userContent.css')
            if uses_scss:
                usercontent = scss_compiler.compile(usercontent)
            with open('.zenbento/package/userContent.css', 'w+') as f:
                f.write(usercontent)

    print('\n\U0001F371 \x1b[32;1mSUCCESS!\x1b[0m Bento has successfully packaged your files.')
    print('You can now use it on Zen Browser to share your rice.')
    print(f'Location: {os.getcwd()}/.zenbento/package')
    return BentoReturn(True, 'Success')

def purge(_config: dict):
    if not os.path.exists('.zenbento') or not os.path.exists('.zenbento/package'):
        return BentoReturn(False, 'Nothing to purge here.')
    shutil.rmtree('.zenbento')
    print('\n\U0001F371 \x1b[32;1mSUCCESS!\x1b[0m Bento has purged its files.')
    return BentoReturn(True, 'Success')

def main():
    mappings = {
        'package': package,
        'purge': purge
    }

    if len(args) < 1:
        logger.error('You didn\'t provide an action, so Bento can\'t run.')
        sys.exit(1)

    action = args[0]
    path = args[1] if len(args) > 1 else None
    if not action in mappings:
        logger.error(f'Unknown action: {action}')
        sys.exit(1)
    if path:
        os.chdir(path)

    try:
        with open('bento.json', 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        logger.exception('Your bento.json file has an error.')
        sys.exit(1)
    except FileNotFoundError:
        logger.error('You don\'t have a bento.json file.')
        sys.exit(1)
    except:
        logger.exception('An unknown error occurred!')
        logger.critical('This shouldn\'t happen. Please report this to the developers.')
        sys.exit(1)

    if config['package'].get('license_filepath'):
        try:
            with open(config['package']['license_filepath'], 'r') as f:
                config['package'].update({'license': f.read()})
        except FileNotFoundError:
            logger.error('The license file path is invalid.')
            sys.exit(1)
        except:
            logger.exception('An unknown error occurred!')
            logger.critical('This shouldn\'t happen. Please report this to the developers.')
            sys.exit(1)

    try:
        result = mappings[action](config)
    except:
        logger.exception('An unknown error occurred!')
        logger.critical('This shouldn\'t happen. Please report this to the developers.')
        sys.exit(1)

    if not result:
        # result is None, assume success
        logger.warning('Bento didn\'t return a result, so we\'re assuming the action was successful.')
        sys.exit(0)

    if not result.success:
        logger.error(result.message)
        sys.exit(1)


if __name__ == '__main__':
    main()
