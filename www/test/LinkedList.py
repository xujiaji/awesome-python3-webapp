class Node(object):
    def __init__(self, item=None, next=None):
        self.item = item
        self.next = next

    def isend(self):
        return self.item is None and self.next is None

class linkedlist(object):

    def __init__(self):
        self.top = Node()

    def push(self, item):
        self.top = Node(item, self.top)

    def pop(self):
        result = self.top.item
        if not self.top.isend():
            self.top = self.top.next
        return result


if __name__ == '__main__':
    lk = linkedlist()
    for x in 'abcdefg':
        lk.push(x)

    while True:
        value = lk.pop()
        print(value)
        if value == None:
            break
