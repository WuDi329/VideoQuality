import configparser

def parse_config_file(config_file_path: str) -> dict:
    """
        解析配置文件，返回配置信息的字典。
    """
    config = configparser.ConfigParser()
    config.read(config_file_path)
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)
    return config_dict

def get_config_value(config: dict, section: str, key: str, default=None) -> str:
    """
        获取配置信息中指定键的值。
    """
    if section in config and key in config[section]:
        return config[section][key]
    else:
        return default