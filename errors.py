class AlreadyMortgagedError(Exception):
    pass


class CannotSellMortgagedProperty(Exception):
    pass


class CannotSellDevelopedProperty(Exception):
    pass


class EndGame(Exception):
    pass
