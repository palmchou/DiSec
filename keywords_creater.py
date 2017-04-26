# -*- coding:utf-8 -*-
import json

keywords = {
    "baidu": {
    },
    "google": {
    },
    "bing": {
    },
}
idx = {
    'baidu': 0, 'google': 0, 'bing': 0
}

if __name__ == '__main__':
    with open('keyword_list.json', 'r') as kl_f:
        kw_lists = json.load(kl_f)['lists']
    for kw_list in kw_lists:
        if '__name__' in kw_list:
            print 'processing', kw_list['__name__'], 'list.'
        for se in kw_list['search_engines']:
            print '\t', 'search engine:', se
            for cate in kw_list['categories']:
                cate_desc = cate['category']
                print '\t\t', 'category: ', cate_desc
                for kw in cate['keywords']:
                    keywords[se][str(idx[se])] = {}
                    keywords[se][str(idx[se])]['words'] = kw
                    keywords[se][str(idx[se])]['last_acquired'] = 0
                    keywords[se][str(idx[se])]['succ_count'] = 0
                    keywords[se][str(idx[se])]['classification'] = cate_desc
                    idx[se] += 1
    json.dump(keywords, open('keywords.json', 'w'), indent=2)
