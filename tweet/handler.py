from twython import TwythonError

from tweet.config import OCD_BILLS_API, QUERY, BILLS, TWITTER_BOT, LOGGER


def get_new_introductions(ocd_api, query_params, bills):
    introductions = ocd_api.get_bills(query_params)
    new_introductions = [introduction for introduction in introductions
                         if not bills.exists(introduction.identifier)]
    return new_introductions


def tweet(ocd_api, query_params, bills, twitter_bot, logger):
    new_introductions = get_new_introductions(ocd_api, query_params, bills)
    logger.info("call: {} new introductions".format(len(new_introductions)))
    if len(new_introductions) > 0:
        for new_introduction in new_introductions:
            try:
                twitter_bot.tweet_introductions(new_introduction)
            except TwythonError as e:
                logger.info("handler: {} error:  {}".format(e.error_code, e.msg))
            else:
                bills.insert(new_introduction)


def call(event, context):
    tweet(OCD_BILLS_API, QUERY, BILLS, TWITTER_BOT, LOGGER)
