class Node:

    def __init__(self,data): 
        self.data = data 
        self.next = None 
        self.prev = None

class DoublyLinkedList:

    def __init__(self):
        self.head = None 
        self.tail = None

    def traverseAndPrint(self):

        current_node = self.head
        print('null',end='<->')
        while current_node: # If the current node is None it will be broke
            print(current_node.data,end="<->")
            current_node = current_node.next 

        print("null")

    def rpush(self,data):
        node = Node(data) 

        if self.head is None:
            self.head = node
            self.tail = node 
            return 
        
        self.tail.next = node
        node.prev = self.tail
        self.tail = node

    def lpush(self,data):
        node = Node(data) 

        if self.head is None:
            self.head = node 
            self.tail = node 
            return 
        
        node.next = self.head
        self.head.prev = node
        self.head =node 


    def lpop(self):
        if self.head is None:
            return None
        poped_node = self.head 
        self.head = poped_node.next

        if self.head is None:
            self.tail = None

        else:
            self.head.prev = None

        return poped_node.data

    def rpop(self):
        if self.tail is None:
            return None 
        poped_data = self.tail 
        self.tail = poped_data.prev

        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None

        return poped_data.data
    