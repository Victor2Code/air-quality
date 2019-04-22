# air-quality
air-quality.com 全国所有省市区的空气质量统计爬虫

# 获取实时数据
```
python3 air-quality.py
```
修改`main(url,charset)`即可，其中第一个参数是显示所有省份的首页地址，第二个参数不出意外就是'utf-8'，除非网站更改编码格式(几乎不可能)

# 下面为爬虫过程中的一些踩坑的地方
* 有些网页的“包含的地点”里面是有某些地名的，但是点击链接进去发现并没有数据，例如“湖北-恩施”，“上海-虹口区”。这个问题在get_single_page_quality中做了处理。
* 网页里面的“污染物”部分有6个常用指标，发现每次打开网页并不是按照顺序来排列的，至于按照什么顺序做的排序我暂时还没弄清楚。
* 网页中判断“包含的地点”是否存在的时候，想当然的用`attrs={'class':'main-block-content'}`做为条件去find了，结果经常出错。一查找发现一页里面有好多该标签，后来通过先找`text='包含的地点'`的标签，然后利用`find_next('div')`找到下一个标签来解决。以后找标签注意唯一性。
* 网站上显示的时间是东八区时间，但是爬下来的时候变成了utc时间。原因是网站访问的时候会带一个cookies，其中有说明timezone为8，但是爬虫的话没有带cookie所有默认是utc时间。解决方法是`str_to_datetime`函数进行一次东八区的转换。
* 因为最后会录入到数据库，所以1.字段不能少，没有找到的用'None'字符串去代替了；2.因为用空格做为字段分隔符，所以每个字段内容的空格都替换为了下划线。
* windows电脑的时间戳和linux的不一样，这个参考issue中的第二个，或者commit **a7a08f4e6a48d69f796ff6776b92bd09d22cb87f**

# 获取历史数据
```bash
cd test_phantomJS
python3 history_data.py
```
需要修改的地方是`main(driver,url,charset)`中的第二个参数

# 下面为爬虫过程中的一些踩坑的地方

* 历史数据采用JS去渲染，所以必须采用selenium+webdriver的方式去实现。最后是用selenium+webdriver获取的单页历史数据，还是采用爬取实时数据的方法用Beautifulsoup去做recursion
* 文件描述符进行write操作的时候不需要保存操作，会自动边写入边保存，但是会有滞后
* 有些网页，例如**上海徐汇区 US Embassy**，需要做额外的try操作去判断时候存在
