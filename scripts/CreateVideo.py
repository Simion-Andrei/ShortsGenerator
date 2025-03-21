import json
import os

class VideoCreator:
    def __init__(self):
        """
        Initializer for VideoCreator object
        Loads the json file
        """

        self.__data = None
        with open("data/content.json", mode="r", encoding="utf-8") as file:
            self.__data = json.load(file)

    def create_video(self):
        """
        Function that creates a new video

        :return: None
        """

    def get_data(self):
        return self.__data