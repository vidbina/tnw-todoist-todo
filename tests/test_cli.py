import pytest
from click.testing import CliRunner
from todo import cli

test_api_key = '14afee5b870d35f35cdb5fe1aa70ee13702709fe'

@pytest.fixture
def runner():
    return CliRunner()

def test_lists_content(runner):
    result = runner.invoke(cli.main, ['--apikey', test_api_key])
    assert result.exit_code == 0
#
#def test_fails_with_invalid_key(runner):
#    result = runner.invoke(cli.main, ['--apikey', 'getstuffdone'])
#    #assert result.output.strip() == 'Hello, world.'
#    assert result.exit_code == 0
#    assert not result.exception
#    #assert result.output.strip() == 'Hello, world.'

def test_fails_without_an_api_key(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip().find('Specify an API key.') != -1
#
#
#def test_cli_with_option(runner):
#    result = runner.invoke(cli.main, ['--as-cowboy'])
#    assert not result.exception
#    assert result.exit_code == 0
#    assert result.output.strip() == 'Howdy, world.'


#def test_cli_with_arg(runner):
#    result = runner.invoke(cli.main, ['David'])
#    assert result.exit_code == 0
#    assert not result.exception
#    assert result.output.strip() == 'Hello, David.'
