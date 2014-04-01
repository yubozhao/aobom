#aobom
Distributed Sina Weibo Crawler via API ready for TBs of data
======
## 重要提示
因新浪微博API数据获取政策调整，目前大规模获取微博用户的接口收到限制。
如果想要大规模获取用户微博数据，您可能需要：
* 拥有第三方客户端的APP，这样的APP的Token，抓取权限不受影响；
* 拥有一般APP的高级授权，可以通过batch的接口（需另外申请），最多获取每个用户的200条微博。
否则目前难于通过API来大规模获取用户微博数据。


## See [English Version Document](https://github.com/haobibo/aobom/wiki/aobom-readme)
Project aobom, written in python, is a distributed Sina Weibo crawler which download data through Weibo API.
aobom can be used when you want to download data from Sina Weibo or other SNS sites provides APIs.
aobom needs Zero-configuration, Small, Easy, Extendable, Scalable, Schedules Dynamicly, Providing easy access for monitoring and Platform independent.

## 查看[中文版详尽文档](https://github.com/haobibo/aobom/wiki/aobom%E4%B8%AD%E6%96%87%E6%96%87%E6%A1%A3)
aobom是一个用Python编写的**分布式**新浪微博爬虫（亦可在单机模式下运行），aobom通过新浪微博开放平台下载数据，并且易于扩展为其他网站平台的爬虫。aobom具有零配置、小巧、可扩展、动态资源调度、平台独立等优点。


## Acknowledgments
* This project is released as an open source software by Hao Bibo, a member of [CCPL](http://ccpl.psych.ac.cn). The author gratefully thanks Li Lin for his support and experiences on Weibo crawler written in C#.
* If you use aobom to collect data for an academic publication, please refer this project in the reference part of you publication.
* If you make publications with the help of aobom, it will be the author's pleasure to know your achievements, contact author through way listed below.

## If you want to:
* Report bug or contribute to project: report an issue through GitHub.
* Know more about the author or contacts: see his [CV](http://en.wikipedia.org/wiki/User:Haobibo) or browse his [Sina Weibo](http://weibo.com/peteraeon).
