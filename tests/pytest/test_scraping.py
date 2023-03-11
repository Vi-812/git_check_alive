from tests.scraping import scraping_testing_list


def test_scraping():
    scraping_testing_list()
    with open('testing_list.txt', 'r') as file:
        testing_list = file.read().splitlines()
    assert len(testing_list) == 100
    for test in testing_list:
        assert test.startswith('https://github.com/')