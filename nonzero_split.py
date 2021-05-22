x =input()

nums = x.split(" ")

nums = [int(nums[i])for i in range(len(nums))]

i, j =0,0

while i <len(nums):
    if nums[i] ==0:
        j = i +1

        while j <len(nums):
            if nums[j] !=0:
                temp = nums[i]
                nums[i] = nums[j]
                nums[j] = temp
                break

            j +=1
    if j >=len(nums):
        break

    i +=1
print(nums)