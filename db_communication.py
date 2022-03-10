import pymongo
import json
import datetime


# Data format:
# { entries = [
#   { classname: rice,
#     confidence: 0.87,
#     accepted: 0
#     weight: 250.0},
#   { classname: miso-soup,
#     confidence: 0.91,
#     accepted: 1,
#     weigth: 77.0}]
#
# {timestamp: 01-01-2022, entries[..], insulin_factor: 0.06, model_used: medium, insulin_amount: 5.96, response_time: 0.25}
# TODO: consider adding carbs or tbh just go back to using class_id instead of classname

class DatabaseCommunicator:
    """
    Class that handles the communication with the pymongo database for inference results

    usage:
    db_comm = DatabaseCommunicator()
    db_comm.add_entry(  # see data format above )
    entries_in_db = db_comm.retrieve_information()
    """
    def __init__(self):
        # Hard coded settings. TODO implement proper safety measures
        USER = "appUser"
        PASS = "Salman12345"
        DB_NAME = "onlineLogs"
        COLLECTION_NAME = "logs"
        connection_string = "mongodb+srv://" + USER + ":" + PASS + \
                            "@food2insulincluster.e5vdq.mongodb.net/" + DB_NAME + "?retryWrites=true&w=majority"

        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client.onlineLogs
        self.collection = self.db[COLLECTION_NAME]


    def retrieve_information(self):
        """
        :return: All documents in self.collection
        """
        return self.collection.find({})


    def add_entry(self, entries: list, insulin_factor: float, model_used: str, response_time: float,
                  insulin_amount: float, ts=None):
        """
        Adds an entry to the database.

        :param entries: list of dict with keys "classname" (str), "confidence" (float: 0-1), "accepted" (int: 0 or 1), "weight" (float)
        :param insulin_factor: float representing insulin factor
        :param model_used: nano, small, medium or other model that was used
        :param response_time: time it took to get the response in seconds
        :param insulin_amount: insulin amount calculated from the carbs and the insulin
        :param ts: timestamp, if not submitted current time is taken
        :return:
        """
        if not ts:
            ts = datetime.datetime.now()
        entry = {
            "entries": entries,
            "insulin_factor": insulin_factor,
            "model_used": model_used,
            "response_time": response_time,
            "insulin_amount": insulin_amount,
            "timestamp": ts
        }
        status = self.collection.insert_one(entry)

        # print("attempted to upload entry:", entry)
        print("status of upload:", status.acknowledged)
        return status.acknowledged



if __name__ == "__main__":
    # Code for testing
    logs_db_communicator = DatabaseCommunicator()

    entries_in_db = logs_db_communicator.retrieve_information()
    # print("Entries:")
    # for entry in entries_in_db:
    #     print(entry)

    with open('data_in_db.json', 'w', encoding='utf-8') as f:
        data = list(entries_in_db)
        for dat in data:
            del dat["_id"]
            dat["timestamp"] = str(dat["timestamp"])
        json.dump(data, f, ensure_ascii=False, indent=4)



