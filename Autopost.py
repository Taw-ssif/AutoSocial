import requests, supabase, random
from bytez import Bytez

#all Keys and variables
supabase_url = 'https://ogyjxjoekmeelcypdham.supabase.co'
supakey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9neWp4am9la21lZWxjeXBkaGFtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1MzcxNzcsImV4cCI6MjA4MTExMzE3N30.XZ_IpE7fPD1rfA-pvfvXFUaKofW7NwWja4Jksqmb7Qc'

FB_PAGE_ID = "820679571138113"
#"EAAbOgJSwrZAQBQBgKCz9ZAeAyaN3hZC5qqMuFxgSYA5r2VVsAnxqtvLlZCLNAbRllTkXc3ZAHVAaeVWgoo2uUb5YhX6v04nTV1yL1qSGVhZC7CsE71awAo9YxlkUbDGrIQ5xxN1jDgTBFh4yZACkYpiL3akxVVhzJVIB3aomKp0rAJ97ZAKGXFg8XnzDN3djRXbhH6uku0WW"
TOKEN = "EAAbOgJSwrZAQBQJ7ZBJ6t4FHpRhYeROIs1jvX9MkGXPpclMBK366YWkPYHG2uZAIrKcz8wUDVLYCGZC3VpqjQ3UNV8ER7H4nkvs8ZCQQcy71wKtOQWZBVjavuT8gsUC8fOBonjFHcDIVZAVraerD4As37ojZCcNbe1qPNkTkm6nR5MkAZBMustZBGMtbaJVoGQsefsToQL4Y9NRAZDZD"
main_url = f"https://graph.facebook.com/v24.0/{FB_PAGE_ID}/photos"

api_key = '39c9c7bd700817b626c0df04a553683b'

db = supabase.create_client(supabase_url, supakey)
#Promptengineering
with open('prompteng.txt','r') as f:
    mainprompt= f.read()
prompt = f"{mainprompt}"
print(prompt)
respo = (db.table("My Post Details").select("post_caption", "image_prompt").execute())
postdata = [(row["post_caption"], row["image_prompt"]) for row in respo.data]
print(postdata)
#post Caption
letter = random.choices("abcdefg")

sdk = Bytez(api_key)
model= sdk.model("Qwen/Qwen3-4B-Instruct-2507")
output= model.run([
  {
    "role": "user",
    "content": f"{prompt}.The previous posts details: {postdata} Main Prompt: {letter} no. prompt from the updated content pool. deep analysis. Do not add anything extra. Direct copy paste ready response. Dont have to add anything like: 'Here is the post caption:'. Just give me the caption and image prompt. Prompt for caption: Describe a theory or procedure related to anything i mentioned before way in a way that is easy for clients to understand. Make it large and descriptive enough. But not a huge paragraph. Attention Grabing. Check the previous posts details and create something new. Give it a title and then add the rest. The image prompt, make it have various styles everytime.... not the same thing **IMPORTANT** Add the prompt in this specific format: 'Prompt:' "
  }
])
print(output)
while output.output == None: 
    output= model.run([
  {
    "role": "user",
    "content": f"{prompt}.The previous posts details: {postdata} Main Prompt: One of the topics listed before, deep analysis. Do not add anything extra. Direct copy paste ready response. Dont have to add anything like: 'Here is the post caption:'. Just give me the caption and image prompt. Prompt for caption: Describe a theory or procedure related to anything i mentioned before way in a way that is easy for clients to understand. Make it large and descriptive enough. But not a huge paragraph. Attention Grabing. Check the previous posts details and create something new. Give it a title and then add the rest. The image prompt, make it have various styles everytime.... not the same thing **IMPORTANT** Add the prompt in this specific format: 'Prompt:' "
  }
])

print(output)
content = output.output["content"]
caption = content.split("Prompt:")[0]
image_prompt = content.split("Prompt:")[1]

print("Generated Caption:", caption)
print("generated prompt for image: ", image_prompt)
#image generation stabilityai/stable-diffusion-xl-base-1.0
image_number = (
    db.table("My Post Details").select("post_sL").order("post_sL", desc=True).limit(1).execute()
)
next_image_number = int(image_number.data[0]['post_sL']) + 1

print("Generated Image Prompt:", image_prompt)
modelimg = sdk.model("stabilityai/stable-diffusion-xl-base-1.0")
imageMain= modelimg.run(image_prompt)
print(imageMain.output)
resp = requests.get(imageMain.output)
with open(f"post{next_image_number}Pic.png","wb") as f:
    f.write(resp.content)

#posting to facebook
payloads = {
    'caption': caption,
    'access_token' : TOKEN
}
files ={
    "source": open(f"post{next_image_number}Pic.png", "rb")
}

response = requests.post(main_url, data=payloads, files=files)

print(response.json())

db.table("My Post Details").insert({
    "post_id" : response.json()["post_id"],
    "post_caption": caption,
    "image_prompt": image_prompt
}).execute() 
