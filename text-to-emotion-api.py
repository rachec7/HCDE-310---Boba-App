import urllib.parse, urllib.request, urllib.error, json

from flask import Flask, render_template, request

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

@app.route("/", methods = ["GET","POST"])
def input_form():
  input_1 = request.form.get('{input_1}')
  input_2 = request.form.get('{input_2}')
  app.logger.info(input_1)
  app.logger.info(input_2)
  if request.method == "POST":
    if input_1 and input_2:
    # if form filled in, return string of strongest emotion
      final_emotions_dict_safe = compare_day_emotions_safe(input_1,input_2)
      print(final_emotions_dict_safe)
      emotionstring = sortKeysByValue(final_emotions_dict_safe)[0]
      #return render_template('emotionstring.html',page_title="Success",emotionstring = emotionstring)
    else:
    # if not, then show the form again with a correction to the user
      return render_template('application.html',
                           page_title="Boba Form - Error",
                           prompt="How can I generate a boba drink for you if you don't enter how you are feeling on both days?")
  else:
    return render_template('application.html', page_title = "Input Form")

if __name__ == "__main__":
  app.run(host="localhost", port=8080, debug=True)