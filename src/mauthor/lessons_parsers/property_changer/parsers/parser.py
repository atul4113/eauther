from abc import ABCMeta, abstractmethod


class Parser(object, metaclass=ABCMeta):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def parse(self, config, page_xml):
        pass

    def _change_log(self, old_value, new_value, property_name, **kwargs):
        self.logger.add_log(action="PROPERTY_CHANGE",
                            type="INFO",
                            old_value=old_value,
                            new_value=new_value,
                            property_name=property_name,
                            **kwargs)

    def _non_valid_log(self, message):
        self.logger.add_log(action="PASSED_CHANGE",
                            type="WARNING",
                            message=message)