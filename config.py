import configparser

config = configparser.ConfigParser()
config.read("config.ini")

abbreviations_file = config["Files"]["Abbreviations"]
start_log_file = config["Files"]["StartLog"]
end_log_file = config["Files"]["EndLog"]
db_path = config["Files"]["DB_path"]
