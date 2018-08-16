from unittest.mock import patch

from test_handler import example_introductions
from twitter import TwitterBot


@patch('twitter.Twython.update_status')
def test_bot(mock_twitter):
    bot = TwitterBot()
    bot.tweet_introductions(example_introductions)

    mock_twitter.assert_any_call(
        status='O2099-1111 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111 #ordinance\n'
               'Make it illegal to put ketchup on hotdogs'
    )
    mock_twitter.assert_any_call(
        status='O2098-1112 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2098-1112 #ordinance\n'
               'Dye the lake green everyday'
    )
    assert mock_twitter.call_count == 2

