import discord
import os, shutil
import random
from PIL import Image

width = 2000
height = 2000
layer_height = 600
layer_width = 600

def clear_temp():
    folder = 'temp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def new_canvas(width, height):
    im = Image.new('RGBA', (width, height), (255, 255, 255))
    im.save("layers/0.png")

def get_canvas():
    max = "0.png"
    if (len(os.listdir('layers')) == 0):
        new_canvas(width, height)
    else:
        for fname in os.listdir('layers'):
            name = fname.split(".")
            if(int(name[0]) > int(max.split(".")[0]) and name[1] == "png"):
                max = fname
    
    return "layers/" + max

def add_layer(layer):
    canvas_filename = get_canvas()
    canvas = Image.open(canvas_filename)
    layer = Image.open("temp/" + layer)
    layer = layer.convert(mode="RGBA")

    prescale_width, prescale_height = layer.size

    if(prescale_width > layer_width or prescale_height > layer_height):
        newsize = (layer_width, layer_height)
        if(prescale_width > prescale_height):
            newsize = (layer_width, int(prescale_height/(prescale_width/layer_width)))
        else:
            newsize = (int(prescale_width/(prescale_height/layer_height)), layer_height)

        layer = layer.resize(newsize)
    
    postscale_width, postscale_height = layer.size

    canvas.alpha_composite(layer, dest=(random.randint(0, width-postscale_width), random.randint(0, height-postscale_height)))

    outfile = "layers/" + str(int(canvas_filename.split(".")[0].split("/")[-1]) + 1) + ".png"
    
    canvas.save(outfile)
    clear_temp()

async def display_canvas(channel):
    f = discord.File(get_canvas())
    await channel.send(file=f)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    split = message.content.split(" ")

    if(message.channel.id == 778465037072990248):
        if(split[0] == "!layer"):
            if(len(message.attachments) == 1 and (message.attachments[0].filename.endswith(".png") or message.attachments[0].filename.endswith(".jpg"))):
                await message.attachments[0].save("temp/" + message.attachments[0].filename)
                add_layer(message.attachments[0].filename)
                await display_canvas(message.channel)
                return
            await message.channel.send("Attach an image to add to the canvas")
        if(split[0] == "!canvas"):
            await display_canvas(message.channel)
        

clear_temp()
client.run(open("client-token", "r").readline())
