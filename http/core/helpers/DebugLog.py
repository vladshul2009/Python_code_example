class DebugLog:

    __logger = None

    @staticmethod
    def instance():
        if DebugLog.__logger is None:
            import logging
            import os
            # create logger with 'spam_application'
            DebugLog.__logger = logging.getLogger('aiohttp_framework')
            DebugLog.__logger.setLevel(logging.DEBUG)
            # create file handler which logs even debug messages
            fh = logging.FileHandler(os.path.join('/home/dev/dev/static', 'debug.html'))
            fh.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            # add the handlers to the logger
            DebugLog.__logger.addHandler(fh)
        return DebugLog.__logger
