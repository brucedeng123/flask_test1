# class Solution:
#     def maxProfit(self, prices):
#         n=len(prices)
#         container_of_buy=[]
#         container_of_sell=[]
#         if (n == 0 or n == 1):
#             return
#
#         container_of_sell = [0 for _ in range(n)]
#         container_of_buy = [0 for _ in range(n)]
#         container_of_cool = [0 for _ in range(n)]
#         container_of_buy[0] = -prices[0]
#         for i in range(1, n):
#             container_of_sell[i] = max(container_of_buy[i - 1] + prices[i], container_of_sell[i - 1])
#             container_of_buy[i] = max(container_of_cool[i - 1] - prices[i], container_of_buy[i - 1])
#             container_of_cool[i] = max(container_of_sell[i - 1], container_of_buy[i - 1], container_of_cool[i - 1])
#         return container_of_sell[-1]
        # print(-prices[0])
        # # print(container_of_buy[0])
        # container_of_buy.append(prices[0])
        # container_of_sell.append(0)
        # container_of_buy.append(max(-prices[0], -prices[1]))
        # container_of_sell.append(max(0, container_of_buy[0] + prices[1]))
        # # for (int i=2;i < n;i++):
        # for i in range(2,n):
        #     container_of_buy.append(max(container_of_sell[i - 2] - prices[i], container_of_buy[i - 1]))
        #     container_of_sell.append(max(container_of_sell[i - 1], container_of_buy[i - 1] + prices[i]))
        # return container_of_sell[n - 1]
        # elem,max_profit=prices[0],0
        # for i in range(len(prices)):
        #     elem=min(elem,prices[i])
        #     print(i,"*"*10,elem)
        #     max_profit=max(max_profit,prices[i]-elem)
        #     print(i,"*"*10,max_profit)
        # return max_profit
# class Solution:
#     def maxProfit(self, prices):
#         minPrice = 9999999
#         maxPro = 0
#         for i in range(len(prices)):
#             if prices[i] < minPrice:
#                 minPrice = prices[i]
#             else:
#                 if prices[i] - minPrice > maxPro:
#                     maxPro = prices[i] - minPrice
#         return maxPro
class Solution:
    def maxProfit(self, prices):
        # min_price = float('inf')
        # max_profit = 0
        non_occupated=[]
        occupated = []
        good = [x for x in prices if x is 0]
        bad = [x for x in prices if x  is not 0]
        print(good,bad)
        for i in range(len(prices)):
            print(type(prices[i]))
            if prices[i] is not int(0):
                occupated.append(i)
            else:
                non_occupated.append(i)
        # for j,k in zip(non_occupated,occupated):
        if len(non_occupated)==0:
            return
        print(non_occupated)
        print(",occupated", occupated)
        print([f"{j}{k}" for j,k in zip(non_occupated,occupated)])
        min_price = max([f"{abs(j-k)}" for j,k in zip(non_occupated,occupated)])
            # min_price = min(j,k)

            # min_price = min(prices[i], min_price)
            # max_profit = max(max_profit, prices[i]-min_price)
        return min_price

test=[1,2,3,0,2,0,0,0,0,4,6,0,0,4]
s=Solution()
print(s.maxProfit(test))