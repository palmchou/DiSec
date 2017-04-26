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

chinese = {
    'black_frame_glasses': [
        '黑框眼镜', '黑框眼镜女孩', '黑框眼镜男孩', '黑框眼镜女生', '黑框眼镜男生', '黑框眼镜美女', '黑框眼镜帅哥',
        '黑框眼镜美女生活照', '黑框眼镜帅哥生活照', '大黑框眼镜', '黑框眼镜发型', '黑框眼镜气质美女', '黑框眼镜气质帅哥',
        '黑框眼镜男生头像', '黑框眼镜女生头像',
    ]
}

english = {
    'black_frame_glasses': [
        'black glasses', 'Black Frame Glasses', 'Black Frame Glasses for Men, Black Frame Glasses for women',
        'Black Eye Glasses', 'Black Eye Frames', 'Black Eye Eyeglasses Frames', 'Black Eye Brand Eyeglasses',
        '45 Eye Eyeglasses Black Crystal', 'Black Crystal Glasses', 'Black Rimmed Glasses',
        'black glasses frames for women', 'black glasses frames for men', 'black glasses frames for boy',
        'black glasses frames for girl', 'black glasses frames for baby',
    ]
}


def put_into_kw_list(raw_list, search_engine, i=0):
    for class_, kws in raw_list.items():
        for kw in kws:
            i += 1
            keywords[search_engine][i] = {}
            keywords[search_engine][i]['words'] = kw
            keywords[search_engine][i]['last_acquired'] = 0
            keywords[search_engine][i]['succ_count'] = 0
            keywords[search_engine][i]['classification'] = class_
    return i

put_into_kw_list(chinese, 'baidu')
last_idx_g = put_into_kw_list(chinese, 'google')
put_into_kw_list(english, 'google', i=last_idx_g)
last_idx_bing = put_into_kw_list(english, 'bing')
put_into_kw_list(chinese, 'bing', i=last_idx_bing)

json.dump(keywords, open('keywords.json', 'w'), indent=2)
