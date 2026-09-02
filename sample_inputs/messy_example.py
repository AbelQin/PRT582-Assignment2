"""A deliberately messy sample file used to demonstrate pyanalyzer."""


def calculateTotal(itemList, taxRate):
    subtotal = 0
    discount = 0.1
    for item in itemList:
        subtotal = subtotal + item
    if taxRate > 0:
        tax = subtotal * taxRate
    else:
        tax = 0
    return subtotal + tax


def calculateTotalAlt(itemList, taxRate):
    subtotal = 0
    discount = 0.1
    for item in itemList:
        subtotal = subtotal + item
    if taxRate > 0:
        tax = subtotal * taxRate
    else:
        tax = 0
    return subtotal + tax


class order_summary:
    def __init__(self, items):
        self.items = items

    def total(self, taxRate):
        if taxRate < 0:
            raise ValueError("negative tax rate")
        elif taxRate > 1:
            raise ValueError("tax rate above 100%")
        return calculateTotal(self.items, taxRate)
