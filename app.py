from fastapi import FastAPI, Request  # Request for acessing the information of HTTP request
from pydantic import BaseModel 
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch 
import re
from fastapi.templating import Jinja2Templates  # to render html pages / templates 
from fastapi.responses import HTMLResponse # Used to return HTML content/pages as the HTTP response
from fastapi.staticfiles import StaticFiles # Used to serve static files like CSS, JavaScript, and images


# initialize our fastapi app
app = FastAPI(title = "Text Summarizer App", description = "Text summarization using T5", version ="1.0" )

app.mount("/static" , StaticFiles(directory = "./static"), name = "static") #Project ke ./static folder ko website ke /static URL se connect karo, taaki CSS, JS, images etc. browser access kar sake.

# load model & tokenizer from Hugging Face
model_name = "Vansh-02/t5-text-summarizer"

model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)

# devices 
if torch.backends.mps.is_available() :
    device = torch.device("mps")
elif torch.cuda.is_available() :
    device = torch.device("cuda")
else : 
    device = torch.device("cpu")

print("device: ", device)
model.to(device)

# templating  ==> Jinja2 templating is used to render HTML pages and dynamically display backend data on the webpage.
templates = Jinja2Templates(directory = "./template")

# Input schema for dialogue 
class DialogueInput(BaseModel) :
    dialogue : str 


# clean data funtion 
def clean_data(text):
    text = re.sub(r"\r\n", " ", text) # lines 
    text = re.sub(r"\s+"," ", text) # spaces 
    text = re.sub(r"<.*?>"," ", text) #html tags <p> <h1>
    text = text.strip().lower()
    return text 


# summarization function 
def summarize_dialogue(dialogue : str) -> str:
    #Inference preprocessing ideally training preprocessing ke compatible hona chahiye.
    dialogue = clean_data(dialogue) # clean 

    # tokenize because T5 directly string process nahi krta 
    inputs = tokenizer(
        dialogue, 
        padding = "max_length" , 
        max_length = 512, 
        truncation = True, 
        return_tensors = "pt" # so it returns pytorch tensors
    ).to(device)

    # generate the summary => token ids will be generated
    model.to(device) # move t5 model 
    targets = model.generate(  # actually generate the summary
        input_ids = inputs["input_ids"], 
        attention_mask = inputs["attention_mask"],
        max_length = 150, #Generated output can contain at most 150 tokens.
        num_beams = 4, # While generating the summary, T5 will keep 4 promising output sequences (paths) at each stage instead of following only one.
        early_stopping = True #If the beam search has finished generating valid sequences earlier, generation can stop rather than unnecessarily continuing toward the maximum.
    )

    # token ids convert to summary => decoding 
    summary = tokenizer.decode(targets[0], skip_special_tokens = True) # target[0]=> because we want token sequence for the first dialogue in the batch.
    return summary 


# Define API endpoints 

@app.post("/summarize/")
async def summarize(dialogue_input : DialogueInput) :
    summary = summarize_dialogue(dialogue_input.dialogue)
    return {"summary" : summary} 

@app.get("/", response_class = HTMLResponse)  # Specifies that this endpoint returns an HTML response
async def home(request : Request) : 
    return templates.TemplateResponse(request= request, name = "index.html")
# Template Response => it renders the index.html template and return  that as response