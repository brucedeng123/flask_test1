rank_news_list=[]
news_dict_list = [1,2,4]
# if rank_news_list:
#     for news_obj in rank_news_list:
#         # news_dict = news_obj
#         news_dict_list.append(news_obj+1)
for news_obj in rank_news_list if rank_news_list else []:
    news_dict_list.append(news_obj + 1)

print(news_dict_list)