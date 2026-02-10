"""Unit tests for the CLI function.

Authors:    Claude <noreply@anthropic.com>

"""

import fedora_messaging.config
import fedora_messaging.exceptions
import pytest
from click.testing import CliRunner

from bugzilla2fedmsg import cli


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('[consumer_config]\nkey = "value"\n')
    return str(config_file)


@pytest.fixture
def mock_consumer_and_relay(mocker):
    """Mock BugzillaConsumer and MessageRelay."""
    mock_relay = mocker.patch("bugzilla2fedmsg.MessageRelay", autospec=True)
    mock_consumer = mocker.patch("bugzilla2fedmsg.BugzillaConsumer", autospec=True)
    mocker.patch("fedora_messaging.config.conf.setup_logging")
    mocker.patch.dict(
        "fedora_messaging.config.conf",
        {"consumer_config": {"test": "config"}},
        clear=False,
    )
    return mock_relay, mock_consumer


def test_cli_no_config(mocker, mock_consumer_and_relay):
    """Test CLI with no config file specified."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    mock_load_config = mocker.patch("fedora_messaging.config.conf.load_config", autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    mock_load_config.assert_not_called()
    mock_relay.assert_called_once_with({"test": "config"})
    mock_consumer.assert_called_once()
    mock_consumer.return_value.consume.assert_called_once()


def test_cli_with_valid_config(mocker, mock_consumer_and_relay, temp_config_file):
    """Test CLI with a valid config file."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    mock_load_config = mocker.patch("fedora_messaging.config.conf.load_config", autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli, ["--config", temp_config_file])

    assert result.exit_code == 0
    mock_load_config.assert_called_once_with(config_path=temp_config_file)
    mock_relay.assert_called_once_with({"test": "config"})
    mock_consumer.assert_called_once()
    mock_consumer.return_value.consume.assert_called_once()


def test_cli_with_config_via_envvar(mocker, mock_consumer_and_relay, temp_config_file):
    """Test CLI with config file specified via environment variable."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    mock_load_config = mocker.patch("fedora_messaging.config.conf.load_config", autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli, [], env={"FEDORA_MESSAGING_CONF": temp_config_file})

    assert result.exit_code == 0
    mock_load_config.assert_called_once_with(config_path=temp_config_file)
    mock_relay.assert_called_once_with({"test": "config"})
    mock_consumer.assert_called_once()
    mock_consumer.return_value.consume.assert_called_once()


def test_cli_with_short_config_option(mocker, mock_consumer_and_relay, temp_config_file):
    """Test CLI with -c short option for config file."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    mock_load_config = mocker.patch("fedora_messaging.config.conf.load_config", autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli, ["-c", temp_config_file])

    assert result.exit_code == 0
    mock_load_config.assert_called_once_with(config_path=temp_config_file)
    mock_relay.assert_called_once_with({"test": "config"})
    mock_consumer.assert_called_once()
    mock_consumer.return_value.consume.assert_called_once()


def test_cli_with_nonexistent_config_file(mocker, mock_consumer_and_relay):
    """Test CLI with a config file that doesn't exist."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    mock_load_config = mocker.patch("fedora_messaging.config.conf.load_config", autospec=True)

    runner = CliRunner()
    result = runner.invoke(cli, ["--config", "/nonexistent/config.toml"])

    assert result.exit_code == 2
    assert "is not a file" in result.output
    mock_load_config.assert_not_called()
    mock_relay.assert_not_called()
    mock_consumer.assert_not_called()


def test_cli_with_invalid_config_content(mocker, mock_consumer_and_relay, temp_config_file):
    """Test CLI with a config file that has invalid content."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    mock_load_config = mocker.patch(
        "fedora_messaging.config.conf.load_config",
        autospec=True,
        side_effect=fedora_messaging.exceptions.ConfigurationException("Invalid config"),
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["--config", temp_config_file])

    assert result.exit_code == 2
    assert "Invalid config" in result.output
    mock_load_config.assert_called_once_with(config_path=temp_config_file)
    mock_relay.assert_not_called()
    mock_consumer.assert_not_called()


def test_cli_keyboard_interrupt(mocker, mock_consumer_and_relay):
    """Test CLI handles KeyboardInterrupt gracefully."""
    _, mock_consumer = mock_consumer_and_relay
    mock_consumer_instance = mock_consumer.return_value
    mock_consumer_instance.consume.side_effect = KeyboardInterrupt()

    runner = CliRunner()
    result = runner.invoke(cli, [])

    # KeyboardInterrupt is re-raised and caught by Click which converts to exit code 1
    assert result.exit_code == 1
    mock_consumer_instance.stop.assert_called_once()
    mock_consumer_instance.consume.assert_called_once()


def test_cli_consumer_config_passed(mocker, mock_consumer_and_relay):
    """Test that consumer_config is correctly passed to MessageRelay and BugzillaConsumer."""
    mock_relay, mock_consumer = mock_consumer_and_relay
    custom_config = {"custom": "value", "another": "setting"}
    mocker.patch.dict(
        "fedora_messaging.config.conf",
        {"consumer_config": custom_config},
        clear=False,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [])

    assert result.exit_code == 0
    mock_relay.assert_called_once_with(custom_config)
    mock_consumer.assert_called_once_with(custom_config, mock_relay.return_value)
