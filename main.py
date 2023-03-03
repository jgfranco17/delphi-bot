from delphi import DelphiBot


def main():
    delphi = DelphiBot(config="config.yaml")
    delphi.run()


if __name__ == "__main__":
    main()
