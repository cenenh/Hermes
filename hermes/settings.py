from configobj import ConfigObj
import platform


class Conf():
    MYSQL_SERVER = 'localhost'
    SCHEMA = 'hermes'

    def set_config(self, conf_file):
        self.config = ConfigObj(conf_file)
        return self.config

CONF = Conf()
