class Solution(object):
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        """
        j=0
        if (x<0):
            return False
            
        for y in range(x):
            j = j*10
            if((x%(10**(y+1)))!=0):
                j = j + (x%(10**(y+1)))
            else:
                break
        if (j==x):
            return True
        else:
            return False