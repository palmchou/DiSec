# DiSec
Distributed Image Search Engine Crawler
### Dependency
Beautiful Soup 4, install it using pip: `pip install bs4`.
### Features
* Craw image results with given keywords
* Support **baidu**, **google**, ~~**bing**~~
* Distributed Server-Worker design
* Keywords could be categorised

### Get Started
1. Set up settings by creating `local_settings.json`, there is an example of it provided
2. Create `keyword_list.json` and fill keywords into it.
3. Use `keywords_creater.py` who reads the user defined `keyword_list.json` then generates `keywords.json` 
which will be used by the manager server.
4. Run `manager_server.py`, the manager server will start and listen to the port
setted in `local_settings.json`
5. Run `SEARCH_ENGINE_worker.py` to start crawling.

## 说明文档
### 依赖
Beautiful Soup 4, 使用 pip 安装： `pip install bs4`.
### 功能
* 依据 所给关键词列表 爬取图片搜索结果
* 支持 **baidu**, **google**, ~~**bing**~~
* 分布式设计，支持多个 worker 进程同时爬取。
* 支持关键词分类

### 如何使用
1. 参考样例，配置 `local_settings.json`
2. 参考样例，创建 `keyword_list.json` 填写所需爬取的关键词列表.
3. 使用 `keywords_creater.py` 来读取用户定义的 `keyword_list.json` 并生成 `keywords.sjon`
4. 运行 `manager_server.py`，manager server 将会监听 `local_settings.json` 所设置的端口
5. 运行 `SEARCH_ENGINE_worker.py` 开始爬取.