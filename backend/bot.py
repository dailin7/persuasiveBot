# Setup
# ------------------------------------------------------------------------------

# All imports
import yaml
from human_intervention import human_intervention, store_message
from telegram.ext import *
import pandas as pd
import torch
import en_core_web_sm
from pathlib import Path
from telegram import ForceReply
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sentence_transformers import SentenceTransformer, util
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.char_classes import CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex
from fse import SplitIndexedList, SIF, Vectors
import subprocess
import csv
import collections

class Bot:
    # Constructor method to initialize the bot
    def __init__(self):
        self.roberta = torch.hub.load('pytorch/fairseq', 'roberta.large.mnli')
        self.roberta.eval()  # disable dropout for evaluation

        # Dataset Aggregation
        healthver_train = pd.read_csv('./Training_Files/healthver_train.csv')
        healthver_val = pd.read_csv('./Training_Files/healthver_dev.csv')
        healthver_test = pd.read_csv('./Training_Files/healthver_test.csv')
        covid_lies_train = pd.read_csv('./Training_Files/covid_lies.csv')
        emnlp = pd.read_csv('./Training_Files/emnlp.csv')
        panacea = pd.read_csv('./Training_Files/panacea.csv')
        covid_fact = pd.read_csv('./Training_Files/covid_fact.csv')
        self.responses = collections.defaultdict(dict)
        with open('Training_Files/responses.csv', newline='') as file:
            reader = csv.DictReader(file)
            for row in list(reader):
                claim = row['misconception']
                response = row['response']
                sources = row['sources'].split("\n")
                score = float(row['score'])
                self.responses[claim]["response"] = response
                self.responses[claim]["sources"] = sources
                self.responses[claim]["score"] = score 

        # data preparation for fine-tuning
        covid_lies_label_map = {'pos': 'FALSE', 'neg': 'FALSE', 'na': 'FALSE'}

        labels = [covid_lies_label_map[x] for x in covid_lies_train['label']]
        labels.extend(['TRUE' if x == 'True' else 'FALSE' for x in emnlp['label']])
        labels.extend(
            ['FALSE' if x == 'Refutes' else 'TRUE' for x in healthver_train['label']])
        labels.extend(
            ['FALSE' if x == 'Refutes' else 'TRUE' for x in healthver_val['label']])
        labels.extend(
            ['FALSE' if x == 'Refutes' else 'TRUE' for x in healthver_test['label']])
        labels.extend(['TRUE' if x else 'FALSE' for x in panacea['label']])
        labels.extend(['TRUE' if x else 'FALSE' for x in covid_fact['label']])

        texts = [text.strip() for text in covid_lies_train['misconception']]
        texts.extend([text.strip() for text in emnlp['claim']])
        texts.extend([text.strip() for text in healthver_train['claim']])
        texts.extend([text.strip() for text in healthver_val['claim']])
        texts.extend([text.strip() for text in healthver_test['claim']])
        texts.extend([text.strip() for text in panacea['claim']])
        texts.extend([text.strip() for text in covid_fact['claim']])

        self.df = pd.DataFrame(zip(texts, labels), columns=['claim', 'label'])
        self.df = self.df.drop_duplicates(ignore_index=True)

        # Model Setup for 1st phase
        self.sents = SplitIndexedList(self.df['claim'].tolist())
        vecs = Vectors.from_pretrained("paranmt-300")
        self.model = SIF(vecs, lang_freq='en')
        self.model.train(self.sents)

        # Model & Topics Setup for second phase
        model_2 = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        url = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters#'
        google_url = 'https://www.google.com/search?q='

        topics = {'Alcohol': 'alcohol',
                'Alcohol-based sanitizer': 'alcohol-sanitizer',
                'Alcohol-based sanitizer, amount': 'sanitizer-amount',
                'Alcohol-based sanitizer, religion': 'alcohol-sanitizer-religion',
                'Bleach': 'bleach',
                'Clean hands': 'clean-hands',
                'Cold weather, snow': 'cold-weather',
                'Dexamethasone': 'dexamethasone',
                'Drugs': 'drugs',
                'Hand dryers': 'hand-dryers',
                'Hand sanitizer': 'sanitizer',
                'Hand sanitizer, essential medicine': 'sanitizer-medicine',
                'Hand sanitizer, bottle': 'sanitizer-bottle',
                'Hot and humid climates': 'climate',
                'Hot peppers': 'pepper',
                'Masks, CO2 intoxication': 'oxygen',
                'Medicines': 'medicines',
                'Methanol, ethanol': 'methanol',
                'Misinformation': 'misinformation',
                'Mosquitoes': 'mosquito-bites',
                'Older people, younger people': 'older-people',
                'Shoes': 'shoes',
                'Sunny and hot weather': 'sun',
                'Supplements': 'supplements',
                'Swimming': 'swimming',
                'Viruses, bacteria, antibiotics': 'virus'}
        topics_link = {}

        for topic in topics:
            topics_link[topic] = url + topics[topic]

        # Fix issue with hyphenated words (keep them together as one word)
        nlp = en_core_web_sm.load()

        infixes = (
            LIST_ELLIPSES
            + LIST_ICONS
            + [
                r"(?<=[0-9])[+\-\*^](?=[0-9-])",
                r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                    al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
                ),
                r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
                # ✅ Commented out regex that splits on hyphens between letters:
                # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
                r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
            ]
        )

        infix_re = compile_infix_regex(infixes)
        nlp.tokenizer.infix_finditer = infix_re.finditer

    # Method to greet the person
    def greet(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."
    

# Phase 1: User message is matched with one of the claims in the dataset
# Compares the user sentence with the different health claims in the dataset.
# If threshold is not met, then no intervention occurs and phase 2 is not
# reached given the messages that have been entered so far.

    def best_match(self, sent, thresh=0.6):
        res = self.model.sv.similar_by_sentence(
            sent.split(), model=self.model, indexable=self.sents.items, topn=1)
        best_m = res[0]
        best_claim = best_m[0]
        label = self.df.iloc[best_m[1]]['label']
        best_score = best_m[2]
        print(best_score)
        if best_score > thresh:
            tokens = self.roberta.encode(best_claim, sent)
            # 0: contradiction 1: neutral 2: entailment
            cls = self.roberta.predict('mnli', tokens).argmax()
            # sent is misinformation when (bsf_claim is misinformation and sent is
            # not contradicted with it) or (bsf_claim is not misinformation but sent is
            # contradicted with it)
            if (label == 'FALSE' and cls != 0) or (label == 'TRUE' and cls == 0):
                return best_claim
            return None
        
        
    # generate response
    def generate_response(self, input_text, firstname):

        user_text = str(input_text).lower() # Convert user message to lowercase string
        claim = self.best_match(user_text) # identify most closely matching misinformation claim
        
        if claim is None:
            return ()
        else:
            
            # prefix1 = "Hello {}! The claim that {} is not entirely accurate. ".format(firstname, input_text)
            # prefix2 = "Hello {}, the claim that {} is incorrect. ".format(firstname, input_text)
            # TODO: bug here (claim empty)
            print("$$$$$$$ claim $$$$$$$")
            print(self.responses[claim])
            response = self.responses[claim]["response"] # response (string) to output (the matched misinformation)
            sources = self.responses[claim]["sources"] # list of URLs (strings) corresponding to the information in the response
            score = self.responses[claim]["score"] # score (float between 0 and 1) assessing how well the response contradicts 'output'
        
        return (response, sources, score)


    # User ChatLog Handler
    def chatlog(self, update, message):
        username = str(update.message.from_user.username)
        chatid = str(update.message.chat_id)
        date = str(update.message.date)

        # store in firebase
        store_message(update)
        
        # The path is based on chatid
        path = "Chat_Logs/" + chatid + ".txt"
        # If the user doesn't have a username then log their user id as their username
        if username == "None":
            username = str(update.message.from_user.id)
        # The log is the username, date, message
        log = username + "," + date + "," + message

        # Check if file exists
        PATH = Path(path)
        if PATH.is_file():
            # Read file contents
            with open(path, "r") as file:
                data = file.readlines()
                file.close()
            # Check first line to see if user has sent a message before
            if username not in data[0]:
                # Change first line to include new user
                data[0] = data[0].strip("\n") + ", " + username + "\n"
                # Add a message before appending log saying this is the user's first message
                data.append(username + " has sent their first message" + "\n")
                with open(path, "w") as file:
                    file.writelines(data)
                    file.close()

        # Create the file and add initial users to the first line
        else:
            with open(path, "w") as file:
                file.writelines("PersuasiveHealthBot" + ", " + username + "\n")
                file.close()

        # Append message log to chat log
        with open(path, "a") as file:
            file.write(log + "\n")
            file.close()


    # Chatbot Log Handler (file always exists by this point)
    def botchatlog(self, update, message):
        chatid = str(update.message.chat_id)
        botname = "PersuasiveHealthBot"
        date = update.message.date
        # The path is based on chatid
        path = "Chat_Logs/" + chatid + ".txt"
        # The log is the botname, date, message
        log = botname + "," + str(date) + "," + message
        # Append bot response to chat log
        with open(path, "a") as input:
            input.write(log + "\n")


    # Start Command
    def start_command(self, update, context):
        update.message.reply_text('Type something to get started!')


    # Help Command
    def help_command(self, update, context):
        update.message.reply_text('This command is not supported yet.')


    # Interpret the message and respond if needed
    def handle_message(self, update, context):
        text = str(update.message.text).lower()
        name = update.message.from_user.first_name

        # Updates the chat logs for user messages
        self.chatlog(update, text)

        # Computes Bot Response
        # TODO: fix
        # response = self.generate_response(text, name)
        # dummy response
        response = ("covid is indeed real", 0, 0)
        if len(response) > 0:
            # len(response) > 0 means misinformation WAS detected
            human_intervention(update, response)

        # update.message.reply_text(response, reply_to_message_id=messageid)
        # self.botchatlog(update, response)


    def error(self, update, context):
        print(f"Update {update} caused error {context.error}")
            
    def start(self):
        with open('./constants.yaml', 'r') as keys_file:
            keys = yaml.load(keys_file, Loader=yaml.FullLoader)
            print(keys['api_key'])

        # Sets the telegram bot API key that is kept in the constants.py file
        self.updater = Updater(keys['api_key'], use_context=True)
        dispatcher = self.updater.dispatcher

        # Sets the start command for the bot to be handled by the start_command function
        dispatcher.add_handler(CommandHandler('start', self.start_command))
        # Sets the help command for the bot to be handled by the help_command function
        dispatcher.add_handler(CommandHandler('help', self.help_command))
        # Set messages to be handled by the handle_message function
        dispatcher.add_handler(MessageHandler(Filters.text, self.handle_message))
        # Sets errors to be handled by the error function
        dispatcher.add_error_handler(self.error)

        self.updater.start_polling()
    
    def stop(self):
        self.updater.idle()