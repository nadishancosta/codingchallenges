class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        ans=[]
        for x in range(len(nums)):
            for y in range(x+1,len(nums)):
                if(nums[x]+nums[y+x]==target):
                    ans.append(x)
                    ans.append(y)
                    return ans
                