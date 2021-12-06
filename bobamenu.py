#import urllib
import urllib.parse, urllib.request, urllib.error, json, random
from webbrowser import get

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


# returns the url or error
def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as error:
        print("The server couldn't fulfill the request." )
        print("Error code: ", error.code)
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
# Function takes in parameters, using safe_get to open the url query string, returning the json restaurant data for the given restaurant
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

    restaurantrequest = safe_get(website)
    restaurantrequeststr = restaurantrequest.read()
    restaurantdata = json.loads(restaurantrequeststr)

    # return JSON
    return restaurantdata



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
    restaurant_data = documenuREST(restaurant_id = restaurant)

    name = restaurant_data["result"]["restaurant_name"]
    id = restaurant_data["result"]["restaurant_id"]
    menulist = restaurant_data["result"]["menus"]

    if name not in menudict:
        menudict[name] = {}

    menusection = menulist[0]["menu_sections"]
    for chunk in menusection:
        sectionname = chunk["section_name"]
        
        if sectionname not in menudict[name]:
            menudict[name][sectionname] = {}

        sectionitems = chunk["menu_items"]
        for drink in sectionitems:
            drinkname = drink["name"]
            drinkdescription = drink["description"]
            drinkprice = drink["price"]

            if drinkname not in menudict[name][sectionname]:
                menudict[name][sectionname][drinkname] = {}
                menudict[name][sectionname][drinkname]["description"] = drinkdescription
                menudict[name][sectionname][drinkname]["price"] = drinkprice
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
#                   ~ fresh milk
#                   ~ other
# * this new menu only has five sections (to be assigned an emotion later when generating a drink for the user), so some of the sections of the
#   current menu are combined/renamed to match *
# Loops through the given menu dictionary creating the new one based off the current one. Looks at the section names to overwrite so all
# menus from all three boba restaurants will match in this format:
#           - if the section is "fruit tea" or "fruit", rename the section as "fruit tea"
#           - if the section is "brewed tea" or "tea" or "fresh tea", rename the section as "tea"
#           - if the section is "milk tea" or "flavored tea", rename the section as "milk tea"
#           - if the section is "fresh tea" or "tea latte", rename the section as "fresh milk"
#           - else, rename the section as "other" ("ice blended", "traditional taste", "chocolate", "yakult", "macchiato", "slush and smoothie")
#
# Returns the newly created dictionary. 
def make_recommendation_dict(mdict):
    rdict = {}
    for location in mdict:
        if location not in rdict:
            rdict[location] = {}
        
        for section in mdict[location]:
            lsection = section.lower()
            if lsection == "fruit tea" or lsection == "fruit":
                newsection = "fruit tea"
            elif lsection == "brewed tea" or lsection == "tea" or lsection == "fresh tea":
                newsection = "tea"
            elif lsection == "milk tea" or lsection == "flavored tea":
                newsection = "milk tea"
            elif lsection == "fresh milk" or lsection == "tea latte":
                newsection = "fresh milk"
            else: # everything else
                newsection = "other"
            
            if newsection not in rdict:
                rdict[location][newsection] = {}
            
            for drink in mdict[location][section]:
                if drink not in rdict:
                    rdict[location][newsection][drink] = mdict[location][section][drink]
    return rdict



# Function called get_boba_section():
# 
#       Takes in parameters:
#       - emotion (str): the user input emotion
#       - bobastore (str): the user input boba store (they pick from "Yifang Taiwan Fruit Tea", "Sharetea", and "Coco Fresh Tea & Juice")
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
def get_boba_section(emotionstr, bobastore, recommendationdict):
    rd = recommendationdict[bobastore]
    if emotionstr == "Angry":
        drinksuggestion = rd["tea"]
    elif emotionstr == "Fear":
        drinksuggestion = rd["fruit tea"]
    elif emotionstr == "Happy":
        drinksuggestion = rd["milk tea"]
    elif emotionstr == "Sad":
        drinksuggestion = rd["other"]
    else: #emotionstr == "Surprise"
        drinksuggestion = rd["fresh milk"]
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

# Function called print_suggested_drink():
# 
#       Takes in parameter:
#       - suggesteddrink (tuple): the randomly chosen drink
#
# Prints out the drink and drink information of the given drink (the output from get_boba_drink()) with the following format and information:
#   {{drink name}} [{{drink price}}] - {{drink description}}
#
# If the drink description is blank (ex: ""), the drink and drink information is printed out with the following format and information:
#   {{drink name}} [{{drink price}}]
def print_suggested_drink(suggesteddrink):
    dname = suggesteddrink[0]
    dinfo = suggesteddrink[1]
    dprice = dinfo["price"]
    ddescription = dinfo["description"]
    if ddescription == "":
        print("{} [{}]".format(dname, dprice))
    else:
        print("{} [{}] - {}".format(dname, dprice, ddescription))


def get_restaurant_id(restname):
    if restname == "Sharetea":
        return 47607063122320424
    elif restname == "Yifang Taiwan Fruit Tea":
        return 47829994122274430
    else: # restname == "CoCo Fresh Tea & Juice"
        return 47617600122192770

# Get the restaurant information of three restaurants in a list.
# Iterate through each restaurant in the list, using get_restaurant_info.
# Get the boba shop name using get_restaurant_name and names the csvfile accordingly with: the boba shop name + "_bobamenu.csv" (ex: Sharetea_bobamenu.csv)
# Writes the menu output from get_restaurant_info() to a csv file.
###restaurant_list = [47607063122320424, 47829994122274430, 47617600122192770]
#restaurant_list = [47607063122320424]
###for restaurantid in restaurant_list:
###    md = get_restaurant_info(restaurantid)
###    name = get_restaurant_name(restaurantid)
###    csvfilename = str(name+"_bobamenu.csv")
###    write_menu(md, csvfilename)

###rd = make_recommendation_dict(md)
###bs = get_boba_section("Sad", "Sharetea", rd)
###sd = get_boba_drink(bs)
###print_suggested_drink(sd)

# import emotionstring from filename as __
from flask import Flask, render_template, request
import logging

app = Flask(__name__)

@app.route("/")#, methods=['GET', 'POST'])
def main_handler():
    app.logger.info("In MainHandler")
    if request.method == 'POST':
        # get user input (restaurant)
        restaurant = request.form.getlist('restaurant_type')
        app.logger.info(request.form.getlist('restaurant_type'))

        # get user input (emotion)
        emotion = request.args.get('input_1}')
        app.logger.info(emotion)

        # if form filled in, greet them using this data
        if restaurant:
            # get user input (restaurant)
            #restaurant = request.form.getlist('restaurant_type')
            #app.logger.info(request.form.getlist('restaurant_type'))  
            restaurantid = get_restaurant_id(restaurant)
            md = get_restaurant_info(restaurantid)
            rd = make_recommendation_dict(md)
            bs = get_boba_section(emotionstr = "Sad", bobastore = restaurant, recommendationdict = rd)
            sd = get_boba_drink(bs)
            return render_template('response.html',
                page_title = "Boba Drink Suggestion Response for %s"%restaurant,
                boba = sd)
        #restaurant_type = request.form.getlist('restaurant_type')
        #app.logger.info(restaurant_type)


        #if not, then show the form again with a correction to the user
        else:
            return render_template('input-template.html',
            page_title = "Boba Form - Error",
            prompt = "How can we give you a drink suggestion if you don't fill anything out?")    
    else:
        return render_template('input-template.html', page_title = "Input Form")


if __name__ == "__main__":
  app.run(host="localhost", port=8080, debug=True)