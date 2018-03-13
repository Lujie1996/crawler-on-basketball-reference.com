import os
if not os.path.exists('test_1.txt'):
    open('test_1.txt', 'w')
print(os.path.getsize('test_1.txt'))
