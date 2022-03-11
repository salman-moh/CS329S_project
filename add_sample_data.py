from db_communication import DatabaseCommunicator
import numpy.random as rd
from datetime import datetime, timedelta
import json


N_LABELS = 100
CONF_TO_ACCEPT = 0.5


def upload_sample_data(n_samples=200, max_n_foods=5, success_rate=0.9, insulin_low=0.05,
                       insulin_high=0.3, model="small", resp_low=0.1, resp_high=1.5, weight_min=10, weight_max=300):
    db_comm = DatabaseCommunicator()
    with open("carb_lookup_new.json", "r") as f:
        quick_lookup_dict = json.load(f)
    dict_key_list = list(quick_lookup_dict.keys())

    for i in range(n_samples):
        n_foods = rd.randint(1, 1+max_n_foods)
        entries = []
        for j in range(n_foods):
            food_key = dict_key_list[(rd.randint(0, N_LABELS))]
            confidence = rd.rand(1)[0] * (1-CONF_TO_ACCEPT) + CONF_TO_ACCEPT
            accepted = 1 if rd.rand(1) < success_rate else 0
            weight = rd.rand(1)[0] * (weight_max-weight_min) + weight_min
            entry = {
                "classname": food_key,
                "confidence": confidence,
                "accepted": accepted,
                "weigth": weight
            }
            entries.append(entry)
        insulin_factor = rd.rand(1)[0] * (insulin_high-insulin_low) + insulin_low
        ts = datetime.today() - timedelta(days=i) - timedelta(hours=rd.randn(1)[0]*24)  # Add one sample per day
        resp_t = rd.rand(1)[0] * (resp_high-resp_low) + resp_low

        # print("entries, insulin factor, model, resp_t, ts:")
        # print(entries, insulin_factor, model, resp_t, ts, sep="\n")
        print("adding entry", i)
        db_comm.add_entry(entries=entries, insulin_factor=insulin_factor, model_used=model, response_time=resp_t, ts=ts)


if __name__ == "__main__":
    upload_sample_data()


