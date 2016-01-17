from unittest import TestLoader, TextTestRunner

def main():
    loader = TestLoader()
    tests  = loader.discover('tests')
    runner = TextTestRunner()
    runner.run(tests)

if __name__ == '__main__':
    main()