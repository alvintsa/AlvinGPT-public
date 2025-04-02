import math

class Node:
    def __init__(self, value = None, next = None, skip = None, tf_idf = 0):
        self.value = value
        self.next = next
        self.skip = skip
        self.tf_idf = tf_idf

class LinkedList:
    def __init__(self, total_num_docs = 0):
        self.total_num_docs = total_num_docs
        self.head = None
        self.tail = None
        self.length, self.n_skips, self.idf = 0, 0, 0.0
        self.skip_length = None
        self.skip_ptrs = []

    def traverse_list(self):
        traversal = []
        
        ptr = self.head
        while ptr:
            traversal.append(ptr.value)
            ptr = ptr.next
            
        return traversal

    def traverse_skips(self):
        skips_traversal = []
        
        ptr = self.head
        while ptr:
            if isinstance(ptr.skip, Node):
                skips_traversal.append(ptr.value)
                while isinstance(ptr.skip, Node):
                    ptr = ptr.skip
                    skips_traversal.append(ptr.value)
            else:
                ptr = ptr.next
        return skips_traversal
    
    def calculate_tf_idf(self):
        ptr = self.head
        
        while ptr:
            idf = self.total_num_docs / self.length
            tf_idf = ptr.tf_idf * idf
            ptr.tf_idf = tf_idf
            ptr = ptr.next
        
        return
            

    def add_skip_connections(self):
        if self.length > 2:
            n_skips = math.floor(math.sqrt(self.length))
            if self.length == n_skips * n_skips:
                n_skips = math.floor(math.sqrt(self.length - 1))
            skip_length = round(math.sqrt(self.length), 0)

            left_ptr, right_ptr = self.head, self.head.next
            i, j = 0, 1
            curr_num_skips = 0
            while curr_num_skips < n_skips and right_ptr:
                if j - i == skip_length:
                    left_ptr.skip = right_ptr
                    right_ptr.skip = True
                    left_ptr = right_ptr
                    right_ptr = right_ptr.next
                    i = 0
                    j = 1
                    curr_num_skips += 1
                else:
                    right_ptr = right_ptr.next
                    j += 1
                
        return
        
    def insert_at_front(self, value, tf_idf):
        new_node = Node(value = value, next = self.head, tf_idf= tf_idf)
        self.head = new_node
        self.length += 1
        return
    
    def insert_at_end(self, value, tf_idf):
    
        new_node = Node(value = value, next = None, tf_idf= tf_idf)
        self.tail.next = new_node
        self.tail = new_node
        self.length += 1
        return
        
        
    def sorted_insert(self, value, tf_idf): 
        """ Write logic to add new elements to the linked list.
            Insert the element at an appropriate position, such that elements to the left are lower than the inserted
            element, and elements to the right are greater than the inserted element.
            To be implemented. """
        
        if not self.head: # first insertion
            self.head = Node(value = value, tf_idf = tf_idf)
            self.tail = self.head
            self.length += 1
            return
        
        elif value < self.head.value:
            self.insert_at_front(value, tf_idf)
            return
        
        elif value > self.tail.value:
            self.insert_at_end(value, tf_idf)
            return   
            
        else:
            prev_ptr, next_ptr = self.head, self.head.next
            
            while next_ptr:
                if value > prev_ptr.value and value < next_ptr.value:
                    prev_ptr.next = Node(value = value, next = next_ptr, tf_idf= tf_idf)
                    self.length += 1
                    return
                prev_ptr = prev_ptr.next
                next_ptr = next_ptr.next
        
        return
        
        
                    
                    
    def sort_by_tf_idf(self):
        result = []
        real_result = []
        
        ptr = self.head
        
        while ptr:
            result.append((ptr.value, ptr.tf_idf))
            ptr = ptr.next
        
        result.sort(key = lambda node: node[1], reverse = True)
        
        for doc_id, tf_idf in result:
            real_result.append(doc_id)
            
        
        return real_result
        
        
        
        
        
        
                    
                    
                
                
                
                            
                                    
            # 5, 8, 10, 17, 18
            # new doc id = 9
            