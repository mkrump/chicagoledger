from tweet.bills import Bill

EXPECTED_IDENTIFIER = 'O2018-6138'
EXPECTED_TITLE = 'Fifty-fifth amending agreement with SomerCor 504, Inc. regarding Small Business Improvement Fund ' \
                 'program increases within Jefferson Park, Lawrence/Pulaski and Lincoln Avenue areas'
EXPECTED_CLASSIFICATION = ['ordinance']
EXPECTED_OCD_ID = 'ocd-bill/fdff8130-549a-45ed-9517-01419fdbeb54'
EXPECTED_BILL = Bill(EXPECTED_IDENTIFIER, EXPECTED_TITLE, EXPECTED_CLASSIFICATION, EXPECTED_OCD_ID)
EXAMPLE_INTRODUCTIONS = [
    Bill('O2099-1111', 'Make it illegal to put ketchup on hotdogs', ['ordinance'], 'ocd-bill/hash1'),
    Bill('O2098-1112', 'Dye the lake green everyday', ['ordinance'], 'ocd-bill/hash2'),
]



