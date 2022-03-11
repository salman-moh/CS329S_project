import difflib
import requests
import pandas as pd
import json

MY_API_KEY = "rXIzMt8684GCgDpFzpI15WWBPZi02Qx5YjGpnkz7"
CARB_NUTR_POSITION = 2

correction_dict = {
    "eels on rice": "DNE",  # 1
    "chicken-'n'-egg on rice": "Rice, fried, with chicken",  # 3
    "chip butty": "DNE",  # 15
    "hamburger": "Hamburger (McDonalds)",  # 16
    "fried noodle": "noodle",  # 25
    "spaghetti": "pasta, cooked",  # 26
    "takoyaki": "DNE",  # 27
    "Japanese-style pancake": "pancake",  # 28
    "gratin": "Potatoes, au gratin, home-prepared from recipe using butter",  # 29
    "sauteed vegetables": "Babyfood, vegetables, mix vegetables junior",  # 30
    "grilled eggplant": "Eggplant, raw",  # 32
    "sauteed spinach": "SPINACH",  # 33
    "omelet": "Egg, whole, cooked, omelet",  # 39
    "ganmodoki": "DNE",  # 40
    "jiaozi": "DNE",  # 41
    "teriyaki grilled fish": "Fish cake or patty, NS as to fish",  # 43
    "lightly roasted fish": "Fish cake or patty, NS as to fish",  # 51
    "steamed egg hotchpotch": "Vegetable stew without meat",  # 52
    "nanbanzuke": "DNE",  # 56
    "spicy chili-flavored tofu": "tofu",  # 63
    "rolled omelet": "Egg, whole, cooked, omelet",  # 66
    "egg sunny-side up": "EGG",  # 67
    "fermented soybeans": "Tempeh, cooked",  # 68
    "cold tofu": "tofu",  # 69
    "boiled chicken and vegetables": "Restaurant, Chinese, chicken and vegetables",  # 74
    "fish-shaped pancake with bean jam": "pancake",  # 77
    "shrimp with chill source": "SHRIMP",  # 78
    "fried shrimp": "SHRIMP",  # 84
    "rice ball": "rice",  # 93
    "mixed rice": "rice",  # 98
    "goya chanpuru": "DNE",  # 99
}

# Format:
# "items": {
#     "food_query" =
#     {
#     "nutr_db_name:": "example",
#     "carbs:": 25
#      }
# }
quick_look_up_dict = {

}


# def salman_script():
#     resp = requests.post("http://34.134.211.187:8080/",
#                          files={'file': open('626.jpg', 'rb')})
#
#     print(resp.json().values())


def test_all():
    df = pd.read_csv("category.txt", delimiter="\t")
    for i, row in df.iterrows():
        print(i)
        food = row["name"]

        if food in correction_dict:
            new_query = correction_dict[food]
            if new_query == "DNE":
                carbs = 0
                db_name = "DNE"
            else:
                carbs, db_name = get_carbs(new_query, 0)
        else:
            carbs, db_name = get_carbs(food, 0)

        new_data = {
            "nutr_db_name": db_name,
            "carbs": carbs
        }
        # food = food.replace(" ", "-")
        quick_look_up_dict[food] = new_data

        print("Carbs [%]:", carbs, end="\n\n")
    with open("quick_lookup.json", "w") as f:
        json.dump(quick_look_up_dict, f)


def get_carbs(food_query, food_nr):
    response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search/?api_key="
                            + MY_API_KEY + "&query=" + food_query)
    print("Got query:", food_query)


    resp_json = response.json()

    # Alternative approach that didnt seem any better in the end
    # Get the items that match the strings as close as possible
    # foods_list = [item["description"] for item in resp_json["foods"]]
    # close_matches = difflib.get_close_matches(food_query, foods_list, len(foods_list), 0)
    # # Smarter thing to do
    # # https://stackoverflow.com/questions/50861237/is-there-an-alternative-to-difflib-get-close-matches-that-returns-indexes-l
    # # Terribly inefficient rn
    #
    # # Go through the foods in the list
    # for match in close_matches:
    #     for i, item in enumerate(foods_list):
    #         if item == match:
    #             food = resp_json["foods"][i]
    #             break

    if len(resp_json["foods"]) == 0:
        print("Could not find any such item")
        return 0
    food = resp_json["foods"][food_nr]

    desc = food["description"]
    print("Picking database item:", desc)

    # Get carbs
    nutr_ind = None
    for i, nutr in enumerate(food["foodNutrients"]):
        if nutr["nutrientName"] == "Carbohydrate, by difference":
            nutr_ind = i
            break
    if nutr_ind is None:
        print("COULD NOT FIND CARBS FOR FOOD ITEM:", food["description"])
    else:
        carb_per_100 = food["foodNutrients"][nutr_ind]["value"]
        return carb_per_100, desc

    # Old setup
    # for food in resp_json["foods"]:
    #
    #     print("Picking database item:", food["description"])
    #
    #     # Get carbs
    #     nutr_ind = None
    #     for i, nutr in enumerate(food["foodNutrients"]):
    #         if nutr["nutrientName"] == "Carbohydrate, by difference":
    #             nutr_ind = i
    #             break
    #     if nutr_ind is None:
    #         print("COULD NOT FIND CARBS FOR FOOD ITEM:", food["description"])
    #     else:
    #         carb_per_100 = food["foodNutrients"][nutr_ind]["value"]
    #         return carb_per_100


def main():
    test_all()


if __name__ == "__main__":
    main()
