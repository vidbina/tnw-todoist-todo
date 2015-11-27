import click
import todoist
import pycurl
from StringIO import StringIO
import base64
import json
import pyaudio
import wave
import alchemy


import ConfigParser, os

debug = False
#@click.command()
#@click.argument('command', default='list')
#@click.option('--apikey', envvar='TODOIST_API_KEY')
#@click.option('--as-cowboy', '-c', is_flag=True, help='Greet as a cowboy.')
#@click.argument('name', default='world', required=False)
#def api_key(key):#
#    return key#
 
#def main(command='list', descr=None):
#    """A CLI for Todoist"""
#
#    if(command == 'list'):
#        list_tasks(api)
#    if(command == 'add'):
#        add_task(api, 
#
#    #click.echo("Do %s" % (descr)) if descr else 'non'
#    #greet = 'Howdy' if as_cowboy else 'Hello'
#    #click.echo('{0}, {1}.'.format(greet, name))
#    #click.echo()

cached_list = []

@click.group()
@click.pass_context
def cli(ctx):
    #click.echo('TODO')
    #click.echo('======================================')
    None

def get_api():
    api_key = get_api_key() 
    if (api_key == None):
        raise click.ClickException('Specify an API key.')

    api = todoist.TodoistAPI(api_key)

    return api
    
def get_color(value):
    if(value < -0.2):
        return "\033[31m" # red
    #if(value < -0.2):
    #    return "\034[31m" # light red
    if(value > 0.2):
        return "\033[32m" # green
    #if(value > 0.2):
    #    return "\034[32m" # light green
    return "\033[33m" # yellow


def get_configuration():
    config = ConfigParser.ConfigParser()
    if os.path.exists('.todo'):
        config.read('.todo')
        return config
    return False

def get_api_key():
    config = get_configuration()
    if config:
        if config.has_section("Todoist"):
            if config.has_option("Todoist", "api_key"):
                return config.get("Todoist", "api_key")
    return os.getenv("TODOLIST_API_KEY", None)

def get_project():
    config = get_configuration()
    if config.has_option("Todoist", "project"):
        return config.get("Todoist", "project")
    return None

def get_watson_credentials():
    config = get_configuration()
    if config:
        if config.has_section("Watson"):
            if(config.has_option("Watson", "user") and config.has_option("Watson", "pass")):
                user = config.get("Watson", "user")
                password = config.get("Watson", "pass")
                return '%s:%s' % (user, password)

def get_watson_voice():
    config = get_configuration()
    if config:
        if config.has_section("Watson"):
            if(config.has_option("Watson", "voice")):
                return config.get("Watson", "voice")

def get_alchemy_key():
    config = get_configuration()
    if config:
        if config.has_section("AlchemyAPI"):
            if(config.has_option("AlchemyAPI", "key")):
                return config.get("AlchemyAPI", "key")

def play_text_to_speech_resource_for(content):
    buffer = StringIO()
    c = pycurl.Curl()
    token = 'Basic %s' % base64.b64encode(get_watson_credentials())
    if debug:
        print "token is %s" % token

    headers = [
            'Authorization: %s' % token,
            'Accept: audio/wav',
            'Content-Type: application/json',
            ]

    data = json.dumps({
        'text': content
        })

    if debug:
        print data
    c.setopt(c.URL, 'https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize')
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, data)

    with open('/tmp/todo.wav', 'wb') as f:
        c.setopt(c.WRITEDATA, f)
        c.perform()
        c.close()

    play_sample()

def play_sample():
    chunk = 1024  
    
    #open a wav format music  
    f = wave.open(r"/tmp/todo.wav","rb")  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  
    
    #paly stream  
    while data != '':  
        stream.write(data)  
        data = f.readframes(chunk)  
    
    #stop stream  
    stream.stop_stream()  
    stream.close()  
    
    #close PyAudio  
    p.terminate()

def sentiment_analyse(item):
    sentiment = 0
    alchemy_key = get_alchemy_key()
    f = open('api_key.txt', 'w')
    f.write(alchemy_key)
    f.close()
    analysis = alchemy.AlchemyAPI().sentiment('text', item['content'])
    if analysis and analysis['docSentiment']:
        if 'score' in analysis['docSentiment'].keys():
            sentiment = analysis['docSentiment']['score']
        else:
            sentiment = 0
    os.remove('api_key.txt')
    return [sentiment, item]

def gather_sentiment(result):
    #print alchemy.AlchemyAPI()
    return list(map(sentiment_analyse, result))

@cli.command('list')
@click.option('--aloud', default=True, count=True)
def list_items(aloud):
    result = get_api().sync(resource_types=['items'], query='p:Personal')
    project_id = get_project()

    items = filter(lambda x: str(x['project_id']) == project_id, result['Items'])

    readable_items = []
    readable_items.append('<p><s>Hey there, your <emphasis>toodoos</emphasis> for this project are:</s>')
    for idx, s in enumerate(gather_sentiment(items)):
        readable_items.append('<s>%s</s>' % s[1]['content'])
        click.echo((u'{color} [ ] {task} ({score})\033[0m').format(color=get_color(float(s[0])), task=s[1]['content'], score=s[0]))

    if(len(readable_items) > 0):
        play_text_to_speech_resource_for(u'%s<break time="1s"/><s><emphasis>Good</emphasis> luck with <emphasis>that</emphasis>!</s></p>' % ''.join(readable_items))

    None

@cli.command('add')
@click.argument('description', nargs=-1)
def add_item(description):
    api = get_api()
    if get_api():
        api.items.add(' '.join(description), get_project())
        print api.commit()

@cli.command('remove')
def remove_item():
    None

@cli.command('complete')
def complete_item(description):
    None

cli(obj={})
