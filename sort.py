from random import randint
from time import process_time
import sys
sys.setrecursionlimit(999999999)
num_lists=[[]for n in range(4)]
for n in range(500):
    num_lists[0].append(randint(-400,400))
for n in range(1000):
    num_lists[1].append(randint(-8000,8000))

for n in range(5001):
    num_lists[2].append(randint(-2000,2000))
for n in range(10000):
    num_lists[3].append(randint(-9000,9000))


def bubble_sort(num_list):
    for n in range(len(num_list)-1):
        for m in range(len(num_list)-1-n):
            if num_list[m]>num_list[m+1]:
                num_list[m+1],num_list[m]=num_list[m],num_list[m+1]
    return num_list

def select_sort(num_list):
    for n in range(len(num_list)-1):
        min_index=n
        for m in range(n,len(num_list)):
            if num_list[m]<num_list[min_index]:
                num_list[min_index],num_list[m]=num_list[m],num_list[min_index]
    return num_list
def insert_sort(num_list):
    for n in range(1,len(num_list)+1):
        for m in range(n):
            if n<len(num_list):
                if num_list[n]<=num_list[m]:
                    num_list[n],num_list[m]=num_list[m],num_list[n]
    return num_list
def shell_sort(num_list):
    gap=len(num_list)//2
    while gap>=1:
        for n in range(gap,len(num_list)):
            while(n-gap)>=0:
                if num_list[n]<num_list[n-gap]:
                    num_list[n],num_list[n-gap]=num_list[n-gap],num_list[n]
                    n-=gap
                else:
                    break
        gap//=2
    return num_list

def merge_sort(num_list):
    if len(num_list)<=1:
        return num_list
    middle=len(num_list)//2
    list_before=merge_sort(num_list[:middle])
    list_after=merge_sort(num_list[middle:])
    return mer_compare(list_before,list_after)

def mer_compare(list_before,list_after):
    result_list=[]
    before_index=after_index=0
    while before_index<len(list_before) and after_index<len(list_after):
        if list_before[before_index]<list_after[after_index]:
            result_list.append(list_before[before_index])
            before_index+=1
        elif list_after[after_index]<=list_before[before_index]:
            result_list.append(list_after[after_index])
            after_index+=1
    if before_index==len(list_before):
        for n in list_after[after_index:]:
            result_list.append(n)
    elif after_index==len(list_after):
        for n in list_before[before_index:]:
            result_list.append(n)
        return result_list


def quick_sort(num_list):
    quick_recursion(num_list,0,len(num_list)-1)

def quick_recursion(num_list,head_index,tail_index):
    if head_index<tail_index:
        pivot_index=quick_partition(num_list,head_index,tail_index)
        quick_recursion(num_list,head_index,pivot_index)
        quick_recursion(num_list,pivot_index+1,tail_index)
    return num_list

def quick_partition(num_list,head_index,tail_index):
    pivot=num_list[tail_index]
    exchange_index=head_index-1
    for n in range(head_index,tail_index):
        if num_list[n]<pivot:
            exchange_index+=1
            num_list[exchange_index],num_list[n]=num_list[n],num_list[exchange_index]
    num_list[exchange_index+1],num_list[tail_index]=num_list[tail_index],num_list[exchange_index+1]
    return exchange_index+1

def heap_sort(num_list):
    list_len=len(num_list)
    for n in range(list_len//2,-1,-1):
        heapify(num_list,list_len,n)
    for n in range(list_len-1,list_len,n):
        num_list[0],num_list[n]=num_list[n],num_list[0]
        list_len-=1
        heapify(num_list,list_len,0)
    return num_list
def heapify(num_list,list_len,parent_index):
    left_index=2*parent_index+1
    right_index=left_index+1
    max_index=parent_index
    if left_index<list_len and num_list[left_index]>num_list[max_index]:
        max_index=left_index
    if right_index<list_len and num_list[right_index]>num_list[max_index]:
        max_index=right_index
    if max_index!=parent_index:
        num_list[parent_index],num_list[max_index]=num_list[max_index],num_list[parent_index]
        heapify(num_list,list_len,max_index)

def count_sort(num_list):
    max_num=max(num_list)
    min_num=min(num_list)
    neg_list=[]
    pos_list=[]
    for num in num_list:
        if num<0:
            neg_list.append(num)
        if num>=0:
            pos_list.append(num)
    if len(neg_list):
        neg_count_list=[0 for n in range(min_num,0)]
        for n in range(len(neg_list)):
            neg_count_list[neg_list[n]]+=1
        neg_index=0
        for n in range(-len(neg_count_list),0):
            while neg_count_list[n]>0:
                neg_list[neg_index]=n
                neg_index+=1
                neg_count_list[n]-=1
    if len(pos_list)!=0:
        pos_counts_list=[0 for n in range(max_num+1)]
        for n in range(len(pos_list)):
            pos_counts_list[pos_list[n]]+=1
        pos_index=0
        while pos_counts_list[n]>0:
            pos_list[pos_index]=n
            pos_index+=1
            pos_counts_list[n]-=1
    result_list=neg_list+pos_list
    return result_list

def bucket_sort(num_list):
    bucket_list=[0 for n in range(max(num_list)-min(num_list)+1)]
    for n in range(len(num_list)):
        bucket_list[num_list[n]-min(num_list)]+=1
    result_list=[]
    for n in range(len(bucket_list)):
        if bucket_list[n]!=0:
            result_list+=[n+min(num_list)]*bucket_list[n]
    return result_list
def radix_sort(num_list):
    pos_list=[]
    neg_list=[]
    for num in num_list:
        if num<0:
            neg_list.append(num)
        if num>=0:
            pos_list.append(num)
    if len(neg_list)!=0:
        neg_num_digit=0
        while neg_num_digit<len(str(min(neg_list))):
            neg_value_lists=[[] for n in range(10)]
            for neg_num in neg_list:
                neg_value_lists[int(neg_num/(10**neg_num_digit))%10].append(neg_num)
            neg_list.clear()
            for neg_value_list in neg_value_lists:
                for neg_num in neg_value_list:
                    neg_list.append(neg_num)
                neg_num_digit+=1
    if len(pos_list)!=0:
        pos_num_digit=0
        while pos_num_digit<len(str(max(pos_list))):
            pos_values_lists=[[]for n in range(10)]
            for pos_num in pos_list:
                pos_values_lists[int(pos_num/(10**pos_num_digit))%10].append(pos_num)
            pos_list.clear()
            for pos_values_list in pos_values_lists:
                for pos_num in pos_values_list:
                    pos_list.append(pos_num)
            pos_num_digit+=1
    result_list=neg_list+pos_list
    return result_list

sort_time_dict={
    bubble_sort:["bubble_sort"],
    select_sort:["select_sort"],
    insert_sort:["Insert sort"],
    shell_sort:["shell_sort"],
    merge_sort:["merge_sort"],
    quick_sort:["quick_sort"],
    heap_sort:["heap_sort"],
    count_sort:["count_sort"],
    bucket_sort:["bucket_sort"],
    radix_sort:["radix_sort"]
}

# for num_list in num_lists:
#     print("正在对第"+str(num_lists.index(num_list)+1)+"个"+"长为"+str(len(num_list))+"的随机数列执行quicksort算法")
#     start_time=process_time()
#     quick_sort(num_list)
#     end_time=process_time()
#     sorts_time_dict=[]
#     sorts_time_dict[quick_sort].append(end_time-start_time)
# for num_list in num_lists:
#     for func_sort,time_list in sort_time_dict.items():
#         if func_sort!=quick_sort:
#             print("正在对第"+str(num_lists.index(num_list)+1)+"个长为"+str(len(num_list))+"的随机数列执行"+time_list[0]+"算法")
#             start_time=process_time()
#             func_sort(num_list.copy())
#             end_time=process_time()
#             time_list.append(end_time-start_time)
#         print("十种排序算法对于不同长度的随机无序数列的排序时间结果如下")
#         print("{:20s}{:<15d}{:<15d}{:<15d}{:<15d}".format(("length of series:",500,1000,5001,10000)))
#         for time_list in sorts_time_dict:
#             for sort_time in time_list:
#                 if not isinstance(sort_time,float):
#                     print("{:20s}".format(sort_time+":"),end=" ")
#                 else:
#                     print("{:<15.4f}".format(sort_time),end=" ")

count_sort_list=[]
for n in range(10000):
    count_sort_list.append(randint(-80000,100000))
start_time_count_sort=process_time()
count_sort(count_sort_list.copy())
end_time_count_sort=process_time()
print("计数排序所用时间:",end_time_count_sort-start_time_count_sort)
