#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
str1="你好10"
res1 = ''.join(re.findall('[\u4e00-\u9fa5]',str1))
res2 = ''.join([i for i in str1 if i.isdigit()])
res3 =''.join(re.findall(r'[A-Za-z]', str1))

for _ in range(0,int(res2)):
    print(res1)
    print(res3)






