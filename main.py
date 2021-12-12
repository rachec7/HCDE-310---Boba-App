# import urllib
import urllib.parse, urllib.request, urllib.error, json, random
from webbrowser import get

# import flask
from flask import Flask, render_template, request
import logging

# [SSL: CERTIFICATE_VERIFY_FAILED] error
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

def get_one_day_emotion(body = ""):
    headers = {
    "User-Agent": "Rachel's Food Menu App",
    "apikey": "UdBdTBiWyMZRa741w31wW9xmAvFEjLfe"
    }
    baseurl = "https://api.promptapi.com/text_to_emotion"
    data = urllib.parse.quote(body).encode("utf-8")
    req = urllib.request.Request(baseurl, headers = headers, data = data)
    resp = urllib.request.urlopen(req)
    urlread = resp.read()
    jsonurl = json.loads(urlread)
    return jsonurl

def get_one_day_emotion_safe(body = ""):
    try:
        return get_one_day_emotion(body)
    except urllib.error.URLError as e:
        print("Error trying to retrieve data:", e)
    return None

def compare_day_emotions(body1,body2):
    params1 = {}
    params2 = {}

    params1['body'] = body1
    params2['body'] = body2

    dict1 = get_one_day_emotion_safe(body = body1)
    dict2 = get_one_day_emotion_safe(body = body2)

    happy1 = dict1['Happy']
    angry1 = dict1['Angry']
    surprise1 = dict1['Surprise']
    sad1 = dict1['Sad']
    fear1 = dict1['Fear']

    happy2 = dict2['Happy']
    angry2 = dict2['Angry']
    surprise2 = dict2['Surprise']
    sad2 = dict2['Sad']
    fear2 = dict2['Fear']

    final_happy = (happy1 + happy2)/2
    final_angry = (angry1 + angry2)/2
    final_surprise = (surprise1 + surprise2)/2
    final_sad = (sad1 + sad2)/2
    final_fear = (fear1 + fear2)/2

    final_emotions_dict = {}
    final_emotions_dict['Happy'] = final_happy
    final_emotions_dict['Angry'] = final_angry
    final_emotions_dict['Surprise'] = final_surprise
    final_emotions_dict['Sad'] = final_sad
    final_emotions_dict['Fear'] = final_fear

    return final_emotions_dict

def compare_day_emotions_safe(body1,body2):
    try:
        return compare_day_emotions(body1,body2)
    except urllib.error.URLError as e:
        print("Error trying to retrieve data:", e)
    return None

"""sorts emotions from highest to lowest"""
def sortKeysByValue(dict):
    keys = dict.keys()
    return sorted(keys, key=lambda k: dict[k], reverse=True)



#### Documenu API #####

# returns the url or error
def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as error:
        print("The server couldn't fulfill the request." )
        print("Error code: ", error.code)
        print("Error: ", error)
    except urllib.error.URLError as error:
        print("We failed to reach a server")
        print("Reason: ", error.reason)
    return None

# Function called documenuREST()
#
#       Takes in parameters:
#       - baseurl (str): base url for the api
#       - params (dict): dictionary of parameters used in the url query string
#       - restaurant_id (int): Numeric ID of the restaurant to get. Required.
#
# Function takes in parameters, using safe_get to open the url query string, returning the url query string
import documenu_api_key as key
def documenuREST(baseurl = "https://api.documenu.com/v2/restaurant/",
    key = key.key,
    params = {},
    restaurant_id = 47607063122320424
    ):
    params["key"] = key
    baseurl = "https://api.documenu.com/v2/restaurant/" + str(restaurant_id)
    url = baseurl + "?" + urllib.parse.urlencode(params)

    header = {'User-Agent': 'Jocelyns Boba Menu App'}

    website = urllib.request.Request(url, headers = header)

    # return url
    return safe_get(website)


# Function called get_restaurant_id():
# 
#       Takes in parameter:
#       - restname (str): the restaurant name as a string
#
# Returns the corresponding integer for the given restaurant
def get_restaurant_id(restname):
    if restname == "Sharetea":
        return 47607063122320424
    elif restname == "Yifang":
        return 45450256122781310
    else: # restname == "CoCo Fresh Tea & Juice"
        return 47617600122192770


# Function called get_restaurant_info()
#
#       Takes in parameter:
#       - restaurant (int): restaurant id of the restaurant
#
# Calls documenuREST and gets the json information about the restaurant.
#       Gets the restaurant name, restaurant id, and restaurant menu. 
#       Loops through the restaurant menu, creating a menu dictionary containing:
#               - restaurant name
#               - drink sections (drink name, drink description, and price)
# Prints the restaurant name, restaurant id, and menu dictionary. Loops through the menu dictionary when
# printing the menu information. Only prints drink name and price if description is blank (Ex: "").
# Returns the menu dictionary. 
def get_restaurant_info(restaurant): #(restaurant_list):
    menudict = {}
    #print(restaurant)
    restaurantrequest = documenuREST(restaurant_id = restaurant)
    #print(restaurantrequest)
    if restaurantrequest is None:
        return None
    else:
        restaurantrequeststr = restaurantrequest.read()
        restaurantdata = json.loads(restaurantrequeststr)

        menulist = restaurantdata["result"]["menus"]

        menusection = menulist[0]["menu_sections"]
        for chunk in menusection:
            sectionname = chunk["section_name"]
            
            if sectionname not in menudict:
                menudict[sectionname] = {}

            for drink in chunk["menu_items"]:
                drinkname = drink["name"]

                # Check if drink name has "Hot" or "Cold", removing these if they are in the drink name
                if drinkname[:4] == "Hot ":
                    drinkname = drinkname[4:]
                elif drinkname[:5] == "Cold ":
                    drinkname = drinkname[5:]

                if drinkname not in menudict[sectionname]:
                    menudict[sectionname][drinkname] = {}
                    menudict[sectionname][drinkname]["description"] = drink["description"]
                    menudict[sectionname][drinkname]["price"] = drink["price"]
    return menudict

# Function called make_recommendation_dict()
#
#       Takes in parameter:
#       - mdict (dict): menu dictionary of the boba restaurants
#
# Loops through the current restaurant menu dictionary, creating a new menu dictionary containing:
#               - restaurant name
#               - 5 drink sections (drink name, drink description, and price)
#                   ~ fruit tea
#                   ~ tea
#                   ~ milk tea
#                   ~ fresh milk/tea latte
#                   ~ other
# * this new menu only has five sections (to be assigned an emotion later when generating a drink for the user), so some of the sections of the
#   current menu are combined/renamed to match *
# Loops through the given menu dictionary creating the new one based off the current one. Looks at the section names to overwrite so all
# menus from all three boba restaurants will match in this format:
#           - if the section is "fruit tea" or "fruit", rename the section as "fruit tea"
#           - if the section is "brewed tea" or "tea" or "fresh tea", rename the section as "tea"
#           - if the section is "milk tea" or "cheese cream drinks", rename the section as "milk tea"
#           - if the section is "fresh tea" or "tea latte", rename the section as "fresh milk"
#           - else, rename the section as "other" ("ice blended", "winter special", "chocolate", "yakult", "macchiato", "slush and smoothie")
#
# Returns the newly created dictionary. 
def make_recommendation_dict(mdict):
    rdict = {}
    for section in mdict:
        lsection = section.lower()
        if lsection == "fruit tea":
            newsection = "fruit tea"
        elif lsection == "traditional taiwanese drink" or lsection == "fresh tea" or lsection == "brewed tea":
            newsection = "tea"
        elif lsection == "milk tea" or lsection == "cheese cream drinks":
            newsection = "milk tea"
        elif lsection == "fresh milk" or lsection == "tea latte" or lsection == "brown sugar drinks" or lsection == "taro":
            newsection = "fresh milk"
        else: # everything else
            newsection = "other"
        
        if newsection not in rdict:
            rdict[newsection] = {}
        
        for drink in mdict[section]:
            if drink not in rdict:
                rdict[newsection][drink] = mdict[section][drink]
    return rdict


# Function called get_boba_section():
# 
#       Takes in parameters:
#       - emotion (str): the user input emotion
#       - recommendationdict (dict): the recommendation dictionary
# 
# Loops through the given recommendation menu dictionary, the output from make_recommendation_dict(), passed in as a parameter to get the drink section
# to recommend to the user based on the input emotion and input bobastore.
#       Drink sections will be recommended to users corresponding to an emotion with this format:
#           - EXAMPLE: emotion -> drink section
#               ~ angry -> tea
#               ~ fear -> fruit tea
#               ~ happy -> milk tea
#               ~ sad -> other
#               ~ surprise -> fresh milk
# Returns the curated drink section suggestion dictionary.
def get_boba_section(emotionstr, recommendationdict):
    if emotionstr == "Angry":
        drinksuggestion = recommendationdict["tea"]
    elif emotionstr == "Fear":
        drinksuggestion = recommendationdict["fruit tea"]
    elif emotionstr == "Happy":
        drinksuggestion = recommendationdict["milk tea"]
    elif emotionstr == "Sad":
        drinksuggestion = recommendationdict["other"]
    else: #emotionstr == "Surprise"
        drinksuggestion = recommendationdict["fresh milk"]
    return drinksuggestion

# Function called get_boba_drink():
# 
#       Takes in parameter:
#       - drinkdict (dict): the suggested drink section dictionary
#
# Gets a list of all the drinks in the given drink dictionary (the output from get_boba_section()) and uses random to get a random drink.
# Returns the drink.
def get_boba_drink(drinkdict):
    drinklist = list(drinkdict.items())
    randomdrink = random.choice(drinklist)
    return randomdrink


# Function called get_drink_url():
# 
#       Takes in parameters:
#       - bobalocation (str): string of the restaurant chosen by the user
#       - suggesteddrink (tuple): the randomly chosen drink
#
# Takes in the given boba location and drink suggestion recommendation, building up the drink url to be used in the html
# Removes all white space in the drink name. Returns the drink url.
def get_drink_url(bobalocation, suggesteddrink):
    drink = ""
    removespace = suggesteddrink[0].split()
    for item in removespace:
        drink += item
    drinkurl = bobalocation[0] + "/" + drink + ".jpeg"
    return drinkurl 



### Flask ###


@app.route("/", methods = ["GET","POST"])
def input_form():
    if request.method == "POST":
        # get yesterday's emotion
        input_1 = request.form.get('{input_1}')
        app.logger.info("yesterday's emotion")
        app.logger.info(input_1)

        # get today's emotion
        input_2 = request.form.get('{input_2}')
        app.logger.info("today's emotion")
        app.logger.info(input_2)

        # get restaurant
        restaurant = request.form.getlist('restaurant_type')
        app.logger.info("user chosen restaurant")
        app.logger.info(restaurant)

        # if form filled in, greet them using this data
        if input_1 and input_2 and restaurant:
            # if form filled in, return string of strongest emotion
            final_emotions_dict_safe = compare_day_emotions_safe(input_1,input_2)
            emotionstring = sortKeysByValue(final_emotions_dict_safe)[0]
            
            print(emotionstring)
            app.logger.info("got emotion: " + emotionstring)
            # get restaurant data
            restaurantid = [get_restaurant_id(restname = b) for b in restaurant][0]
            app.logger.info("got restaurant id: " + str(restaurantid))
            app.logger.info("getting restaurant menu")
            md = get_restaurant_info(restaurantid)
            app.logger.info("got menu dictionary")
            rd = make_recommendation_dict(md)
            app.logger.info("got recommendation menu")
            bs = get_boba_section(emotionstr = emotionstring, recommendationdict = rd)
            app.logger.info("got boba section")
            sd = get_boba_drink(bs)
            app.logger.info("got boba drink")
            print(sd) 
            url = get_drink_url(bobalocation = restaurant, suggesteddrink = sd)
            app.logger.info(url)
            print(url)            
            
            return render_template('response.html',
                drink_url = url,
                page_title = "Boba Drink Suggestion Response for %s"%restaurant[0],
                gif_url = "bobabee.gif",
                boba = sd)      

        #if not, then show the form again with a correction to the user
        else:
            return render_template('input-template.html',
            page_title = "Boba Form - Error",
            gif_url = "bobabeesad.gif",
            prompt = "How can we give you a drink suggestion if you don't fill everything out? Please fill out the form :)")    
    else:
        return render_template('input-template.html',
        gif_url = "bobabee.gif",
        page_title = "Input Form")


if __name__ == "__main__":
    # Used when running locally only. 
	# When deploying to Google AppEngine, a webserver process will
	# serve your app.     
    app.run(host="localhost", port=8080, debug=True)