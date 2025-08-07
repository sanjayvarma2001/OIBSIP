import speech_recognition as sr
import spacy
from transformers import AutoTokenizer,AutoModelForCausalLM
import pyttsx3
import subprocess
import wikipedia
from wikipedia.exceptions import DisambiguationError,HTTPTimeoutError,PageError
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import platform
import re
import os
from dotenv import load_dotenv
import time

load_dotenv()

class speechRecognition:
    def __init__(self):
        self.sr = sr.Recognizer()

    def recognizer(self):
        try :
            with sr.Microphone() as source:
                print("Listening...")
                self.sr.adjust_for_ambient_noise(source)  
                audio = self.sr.listen(source,timeout = 5, phrase_time_limit = 5)
                text = self.sr.recognize_google(audio)
        except sr.WaitTimeoutError:
            print("Listening timed out. Please start speaking sooner.")
            return ""
        except sr.UnknownValueError:
            print("Couldn’t understand anything.")
            return ""
        except sr.RequestError as e:
            print(f"Speech Recognition service error: {e}")
            return ""
        return text.lower()

class NaturalLanguageProcessing:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.predefined_qa = {
        "who_are_you": {
            "questions": [
                "who are you",
                "what is your name",
                "tell me about yourself",
                "who created you"
            ],
            "answer": "Hi, I am MAN, your voice assistant. I was created by Sanjay."
        },
        "help": {
            "questions": [
                "how can you help me",
                "what can you do",
                "help me"
            ],
            "answer": "I can help you with many tasks like opening apps, answering questions, and more."
        }
        }
    
    def generating(self,text):
        new_user_input_ids = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors='pt')
        chat_history_ids = self.model.generate(new_user_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(chat_history_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)
 
    def processing(self, text):
        doc = self.nlp(text)
        name = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        return name
    def predefined_speech(self,user_input):
        user_input = user_input.lower()
        for intent, data in self.predefined_qa.items():
            if any(q in user_input for q in data['questions']):
                return data['answer']
        return None

class TaskManager:
    data_location = requests.get("http://ip-api.com/json/")
    data_loc = data_location.json()
    def __init__(self,input_text):
        self.input_text = input_text.lower().strip()

    def launch_task(self):
        command = self.input_text.split()
        try:
            if "chrome" in command:
                subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
            else:
                subprocess.Popen(command)
        except FileNotFoundError as e:
            return e
        except Exception as e:
            return e

    def search_task(self):
        command = self.input_text
        try:
            results =wikipedia.search(command)
            if results:
                page =wikipedia.page(results[0])
                summary = wikipedia.summary(page.title,sentences =2)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            msg = f"Topic '{command}' is too ambiguous. Try one of these: {', '.join(e.options[:5])}"
            return msg
        except wikipedia.exceptions.PageError:
            msg = f"No page found for '{command}'. Please check the spelling."
            return msg
        except wikipedia.exceptions.HTTPTimeoutError:
            msg = "Wikipedia request timed out. Try again later."
            return msg
        except Exception as e:
            msg = f"Unexpected error: {e}"
            return msg
    def weather_task(self, city= None):
        if not city:
            city = self.__class__.data_loc['city']
        
        try:
            Wea_API = os.getenv("Weather_Api_key")
            url= f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={Wea_API}&units=metric"
            response = requests.get(url).json()
            if response.get('cod') != 200:
                return f"Sorry, i could'nt retrieve the weather"
            temp = response['main']['temp']
            condition= response['weather'][0]['description']
            return f"the weather now in {city} is {temp} and {condition}"
        except Exception as e:
            return f"Something is wrong :{e}"
    
    def spotify_access(self,song_name):
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id = os.getenv("CLIENT_ID"),
            client_secret = os.getenv("CLIENT_SECRET"),
            redirect_uri = os.getenv("SPOTIFY_URI"),
            scope= "user-read-playback-state user-modify-playback-state",
            show_dialog= True
        ))
        devices_info = sp.devices()
        devices = devices_info.get("devices",[])

        current_device = platform.node().lower()
        device_id = None

        for device in devices:
            if current_device in device['name']:
                device_id = device['id']
                break
        
        result = sp.search(q= song_name, type="track", limit = 1)
        tracks = result.get('tracks',{}).get('items',[])
        if tracks:
            track_uri = tracks[0]['uri']
            sp.start_playback(device_id,uris=[track_uri])
            print(f"🎵 Now playing: {tracks[0]['name']} by {tracks[0]['artists'][0]['name']}")
        else:
            print("❌ Song not found.")
        
                

class speaker:
    def __init__(self):
        pass
    
    def speak(self, text):
        print(f"[Speaking] : {text}")
        try:
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)
            engine.setProperty("rate", 150)

            engine.say(text)
            engine.runAndWait()
            engine.stop() 
        except Exception as e:
            print(f"Error in speaking: {e}")


class Assistant:
    def __init__(self):
        self.recognize = speechRecognition()
        self.nlp = NaturalLanguageProcessing()
        self.speaker = speaker()
    
    def handle_text(self,text):
        #predefined question and awnsers
        predefined = self.nlp.predefined_speech(text)
        if predefined:
            self.speaker.speak(predefined)
            return
        
        #launch app
        re_launch = re.search(r"(open|launch|start)\s+([a-zA-Z0-9 ]+)",text,re.IGNORECASE)
        if re_launch:
            app_name = re_launch.group(2).strip().lower()
            TaskManager(app_name).launch_task()
            self.speaker.speak(f"Opening : {app_name}")
            return
        
        #weather access
        re_weather = re.search(r"(what('?s| is)? the)?\s*weather( today|\s+in\s+(?P<city>[a-zA-Z\s]+))?",text,re.IGNORECASE)
        if re_weather:
            city_name= re_weather.group("city")
            weather=TaskManager(text).weather_task(city_name)
            self.speaker.speak(weather)
            return
        
        #spotify access
        song_name = re.search(r"play\s+(?P<song>[a-zA-Z0-9\s]+)",text, re.IGNORECASE)
        if song_name:
            song= song_name.group("song")
            TaskManager(text).spotify_access(song)
            self.speaker.speak(f"playing : {song}")

        #conversational and search
        wiki_pattern= [r"who is\s(.+)",
                       r"what is\s(.+)",
                       r"tell me about\s(.+)",
                       r"define\s(.+)",
                       r"when did\s(.+)",
                       r"where is\s(.+)"]
        wiki_text = None
        for pattern in wiki_pattern:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                wiki_text = match.group(0)  
                break
        if wiki_text:
            response = TaskManager(wiki_text).search_task()
        else:
            response = self.nlp.generating(text)

        self.speaker.speak(response)


    def run(self):
        self.speaker.speak("Hi, how can i help you")
        while True:
            speech= self.recognize.recognizer().lower()
            self.speaker.speak(f"You : {speech}")
            if not speech:
                continue
            time.sleep(0.5)
            if "ok bye" == speech or "stop" == speech:
                self.speaker.speak("see you again.")
                break
            self.handle_text(speech)
            time.sleep(2)

def main():
    assistant = Assistant()
    assistant.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interupted by keyboard")
        speak = speaker()
        speak.speak("Okay, Bye. exiting now")