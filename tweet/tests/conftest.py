from tweet.bills import Bill
import pytest

EXPECTED_IDENTIFIER = 'O2018-6138'
EXPECTED_TITLE = 'Fifty-fifth amending agreement with SomerCor 504, Inc. regarding Small Business Improvement Fund ' \
                 'program increases within Jefferson Park, Lawrence/Pulaski and Lincoln Avenue areas'
EXPECTED_CLASSIFICATION = ['ordinance']
EXPECTED_OCD_ID = 'ocd-bill/fdff8130-549a-45ed-9517-01419fdbeb54'
EXPECTED_DATE = '2018-07-25'
EXPECTED_BILL = Bill(EXPECTED_IDENTIFIER, EXPECTED_TITLE, EXPECTED_CLASSIFICATION, EXPECTED_OCD_ID, EXPECTED_DATE, None)
EXAMPLE_INTRODUCTIONS = [
    Bill('O2099-1111', 'Make it illegal to put ketchup on hotdogs', ['ordinance'], 'ocd-bill/hash1', '10/28/18', '123'),
    Bill('O2098-1112', 'Dye the lake green everyday', ['ordinance'], 'ocd-bill/hash2', '10/27/18', '456'),
]

def pytest_collection_modifyitems(config, items):
    if 'slow' == config.getoption("markexpr"):
        # -m slow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need -m slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
