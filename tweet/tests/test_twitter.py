from mock import create_autospec

from tweet.bills import Bill
from tweet.conftest import EXAMPLE_INTRODUCTIONS
from tweet.twitter import TwitterClient, TwitterBot, TwitterCredentials, TWITTER_MAX_CHARS, SHORT_URL_LENGTH, \
    TWEET_TEMPLATE, REPLY_TEMPLATE

EXAMPLE_INTRODUCTION = EXAMPLE_INTRODUCTIONS[0]
TWEET = 'Make it illegal to put ketchup on hotdogs ' \
        'O2099-1111 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111'


def test_tweet_introductions():
    twitter_client = create_autospec(TwitterClient)
    twitter_bot = TwitterBot(twitter_client)

    twitter_bot.tweet_bill(EXAMPLE_INTRODUCTION)

    assert twitter_client.update_status.call_count == 1
    twitter_bot.twitter_client.update_status.assert_any_call(status=TWEET, in_reply_to_status_id=None)


def tweet_after_url_shortening(bill, reply_to=None):
    tweet_with_shortened_url = TWEET_TEMPLATE.format(
        title=bill.title,
        identifier=bill.identifier,
        url=SHORT_URL_LENGTH * 'x'
    )
    if reply_to is not None:
        tweet_with_shortened_url = REPLY_TEMPLATE.format(username=reply_to, tweet=tweet_with_shortened_url)
    return tweet_with_shortened_url


def test_shorten_shortening_required():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))
    bill_identifier = 'O2099-1111'
    tweet_with_shortened_url = tweet_after_url_shortening(Bill(bill_identifier, '', [], ''))
    allowed_chars_excluding_url = (TWITTER_MAX_CHARS - len(tweet_with_shortened_url))
    too_long_title = 'x' * (allowed_chars_excluding_url + 1)
    bill = Bill(bill_identifier, too_long_title, '', '')
    too_many_chars_tweet = tweet_after_url_shortening(bill)

    shortened_bill = bot.shorten(bill)

    assert len(too_many_chars_tweet) == TWITTER_MAX_CHARS + 1
    assert len(tweet_after_url_shortening(shortened_bill)) == TWITTER_MAX_CHARS


def test_shorten_shortening_not_required():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))
    bill_identifier = 'O2099-1111'
    bill_title = 'title'
    bill = Bill(bill_identifier, bill_title, '', '')
    shortened_bill = bot.shorten(bill)

    assert len(tweet_after_url_shortening(bill)) <= TWITTER_MAX_CHARS
    assert shortened_bill == bill


def test_shorten_with_reply():
    # seems like @username should not count against 280 chars, based on twitter api docs
    # however when trying to update status starting with @username it was being counted
    # against total.
    bot = TwitterBot(TwitterCredentials('', '', '', ''))
    user_name = 'username'
    bill = Bill(
        'O2018-6573',
        'Restructuring of debt to approve settlement payment from original owner NHS Redevelopment Corp., '
        'and allow multiple property transfers, restructuring of City loans, affordability restrictions and '
        'project rehabilitation agreements with new owner, Villa Capital Partners LLC and Villa Capital '
        'Managers LLC',
        ['ordinance'],
        'ocd-bill/c08ea55e-4017-4dfa-bfca-604b0eba0e85',
        '2018-07-25', -1
    )
    shortened_bill = bot.shorten(bill, user_name)

    assert len(tweet_after_url_shortening(shortened_bill, user_name)) == TWITTER_MAX_CHARS
    assert tweet_after_url_shortening(shortened_bill, user_name) == \
           '@username Restructuring of debt to approve settlement payment from original owner NHS Redevelopment ' \
           'Corp., and allow multiple property transfers, restructuring of City loans, affordability restrictions and ' \
           'project rehabilitation agreements wi... O2018-6573 xxxxxxxxxxxxxxxxxxxxxxx'
