from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from scipy.special import softmax


# #MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
# #tokenizer.save_pretrained('models/roberta/tokenizer/')
# #model.save_pretrained('models/roberta/', from_pt=True)
# #config.save_pretrained('models/roberta/config/')

MODEL = 'models/roberta/'
tokenizer = AutoTokenizer.from_pretrained(MODEL+'tokenizer/')
config = AutoConfig.from_pretrained(MODEL+'config/')
model = AutoModelForSequenceClassification.from_pretrained(MODEL+'model/')

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def get_rank(text):
    text = preprocess(text)
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    return scores

def get_severity_level(score):
    if score <= 0.5:
        return 1
    elif score > 0.5 and score < 0.8:
        return 2
    elif score >= 0.8:
        return 3

async def severity_inference_pipeline(text):
    text = preprocess(text)
    rank = get_rank(text)
    sl = get_severity_level(rank[0])
    return sl