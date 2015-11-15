import click
import todoist

import ConfigParser, os

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
    click.echo('TODO')
    click.echo('======================================')

def get_api():
    api_key = get_api_key() 
    if (api_key == None):
        raise click.ClickException('Specify an API key.')

    api = todoist.TodoistAPI(api_key)

    return api
    
def get_color(value):
    return "\033[31m"


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
    if os.path.exists('.todo'):
        if config.has_option("Todoist", "project"):
            return config.get("Todoist", "project")
    return None

@cli.command('list')
def list_items():
    result = get_api().sync(resource_types=['items'], query='p:Personal')
    print result
    for item in result['Items']:
        click.echo(("{color} [ ] {task}\033[0m").format(color=get_color('red'), task=item['content']))
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
