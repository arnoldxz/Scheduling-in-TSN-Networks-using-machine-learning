import json

class ConfigService:
    def __init__(self):
        self._config = ConfigService.readConfig("ILPConfig.json")
        self._networkConfig = ConfigService.readConfig("StreamsConfig.json")
        self._Bandwidth = self._networkConfig["Bandwidth"]
        self._streamsConfig = self._networkConfig["streams"]
    
    @property
    def config(self):
        return self._config
    @property
    def networkConfig(self):
        return self._networkConfig
    @property
    def streamsConfig(self):
        return self._streamsConfig
    @property
    def bandwidth(self):
        return self._Bandwidth
    @staticmethod
    def readConfig(filename):
        f = open(filename)
        return json.load(f)