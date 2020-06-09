# _*_ coding:utf-8 _*_

import xmind
workbook = xmind.load('直播-V5.9.xmind')
print(workbook.getData())
#print(workbook.to_prettify_json())
sheet = workbook.getPrimarySheet()
print(sheet.getData())
root_topic = sheet.getRootTopic()
print("root_topic: ", root_topic.getData())
print("root_topic_title: ",root_topic.getData()['title'])
sub_topics = root_topic.getData().get("topics")
print("sub_topics: ", sub_topics)
for topic in sub_topics:
    print("topic: ",topic)
    topic_title = topic['title']
    print("sub_topic_title: ", topic_title)
    topic_3 = topic.get("topics")
    for topp in topic_3:
        sub_title = topp['title']
        module_title = topic_title + sub_title
        print("topic3_title: ", sub_title)
        print("module: ",module_title )
