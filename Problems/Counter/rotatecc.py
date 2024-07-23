import copy

def counterclock():
    rotatedarr= [[None]* len(arr) for _ in range(len(arr))]
    counter = 0
    # rotatedarr[0][0] = 100
    
    print(rotatedarr)
    for x in range(len(arr)-1,-1,-1):
        for y in range(len(arr)):
            rotatedarr[counter][y] = arr[y][x]
            # print(f"{counter},{y} -> {y},{x} and element {rotatedarr}")
            # print(oldarr)
            # print(x)
        counter+=1
    return rotatedarr


if __name__ == "__main__":
    arr = [[1,2,3,4],
           [5,6,7,8],
           [9,10,11,12],
           [13,14,15,16]]
    
    gg=counterclock()
    for count in range(len(gg)):
        print (gg[count])
    
    
    # print(arr[2][2])
# [3,6,9]
# [2,5,8]
# [1,4,7]

# 0,0 0,1 0,2
# 1,0 1,1 1,2
# 2,0 2,1 2,2

#0,2 1,2 2,2 
#0,1 1,1 2,1
#0,0 1,0 2,0
    # print(arr)