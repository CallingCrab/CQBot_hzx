# -*- coding: utf-8 -*-
from cqhttp import CQHttp
import setting
import modian
from lottery import bind_qq, inquire, patch_msg, handlePointPickMsg


bot = CQHttp(api_root='http://127.0.0.1:5700/')
# 也可以添加access_token和secret，更加安全
# bot = CQHttp(api_root='http://127.0.0.1:5700/',
#              access_token='your-token',
#              secret='your-secret')
# 如果设置了access_token和secret，请修改http-API插件的配置文件中对应的部分


# 群消息操作
@bot.on_message('group')
def handle_msg(context):
    if context['group_id'] in setting.groupid() and context['user_id'] != context['self_id']:
        # 关键词禁言
        if setting.shutup():
            for word in setting.shutup():
                if word in context['message']:
                    bot.set_group_ban(group_id=context['group_id'], user_id=context['user_id'], duration=30*60)
        # 关键词回复
        if context['message'] == '集资' or context['message'] == 'jz' or context['message'] == '打卡' or context['message'] == 'dk':
            jz = ''
            jz_array = modian.md_init(setting.pro_id())
            for jz_dict in jz_array:
                jz += jz_dict['name'] + '\n' + jz_dict['url_short'] + '\n'
            bot.send(context, jz)
        elif context['message'] == 'wds20' or context['message'] == 'jz20' or context['message'] == 'rank' or context['message'] == '聚聚榜' or context['message'] == 'jzb' or context['message'] == '集资榜':
            rank1_array = modian.rank(1)
            for rank1_msg in rank1_array:
                bot.send(context, rank1_msg)
        elif context['message'] == 'dkb' or context['message'] == '打卡榜' or context['message'] == 'dk20' or context['message'] == 'dakabang':
            rank2_array = modian.rank(2)
            for rank2_msg in rank2_array:
                bot.send(context, rank2_msg)
        elif "独占" in context['message']:
            dz = ''
            dz_array = modian.md_init(setting.pro_id())
            for dz_dict in dz_array:
                dz += dz_dict['name'] + '\n' + dz_dict['url_short'] + '\n'
            duzhan = "独占请集资" + '\n' + dz
            bot.send(context, duzhan)
        elif context['message'] == '欢迎新人':
            bot.send(context, setting.welcome())
        elif context['message'] == '项目进度' or context['message'] == '进度':
            jd_array = modian.result(setting.pro_id())
            jd = ''
            for jd_msg in jd_array:
                jd += jd_msg + '\n'
            bot.send(context, jd)
        # lottery
        # 抽卡相关
        if context['message'] == '抽卡':
            lot_reg = "卡池:包括R卡11张、SR卡11张、SSR卡11张\n" +\
                "10.7～106.99是单抽，每10.7抽一次，只能抽到R和SR\n" +\
                "107~519.99是【3】连抽，可以抽到R、SR、SSR\n" +\
                "520及以上是【11】连抽，保底SR一张\n" +\
                "【抽卡链接】:\n"
            ck_array = modian.md_init(setting.pro_id())
            for ck_dict in ck_array:
                lot_reg += ck_dict['name'] + '\n' + ck_dict['url_short'] + '\n'
            bot.send(context, lot_reg)
        if context['message'] == '查卡':
            chaka = inquire(context['user_id'])
            if chaka:
                bot.send(context, chaka)
            else:
                inq_reg = "请指定摩点id或先进行绑定操作\n" + "查询命令格式“查卡#123456”" +\
                    "\n绑卡命令可将您的qq和摩点数字id绑定，数字id可以通过摩点app或直接集资查询。\n" +\
                    "命令格式为“绑定#123456”"
                bot.send(context, inq_reg)
        if context['message'].startswith('查卡#'):
            try:
                chaka_uid = int(context['message'].split("#")[1])
            except Exception as e:
                print(e)
                bot.send(context, "查询失败")
            else:
                chaka_result = inquire(context['user_id'], chaka_uid)
                if chaka_result:
                    bot.send(context, chaka_result)
                else:
                    bot.send(context, "查询失败")
        if context['message'].startswith('绑定#'):
            try:
                bangka_uid = int(context['message'].split("#")[1])
            except Exception as e:
                bot.send(context, "绑定失败")
            else:
                if bind_qq(context['user_id'], bangka_uid):
                    bot.send(context, "绑定成功")
                else:
                    bot.send(context, "绑定失败")
        if context['message'].startswith('积分抽'):
            if context['message'][3:] in ["R", "SR", "SSR"]:
                jfck_msg = handlePointPickMsg(context['message'], context['user_id'])
            else:
                jfck_msg = "重复的卡牌会自动转为积分(R:5点, SR:20点, SSR:100点)\n" +\
                        "已绑定摩点的用户可以用积分抽卡\n" +\
                        " 积分抽R   会消耗40积分随机抽一张R卡\n" +\
                        " 积分抽SR  会消耗100积分随机抽一张SR卡\n" +\
                        " 积分抽SSR 会消耗400积分随机抽一张SSR卡"
            bot.send(context, jfck_msg)


# 新人加群提醒
@bot.on_notice('group_increase')
def handle_group_increase(context):
    if context['group_id'] == setting.groupid()[0]:
        # ret = bot.get_stranger_info(user_id=context['user_id'], no_cache=False)
        # welcome = '欢迎新聚聚：@' + ret['nickname'] + ' 加入本群\n\n' + setting.welcome()
        welcome = [{'type': 'text', 'data': {'text': '欢迎新聚聚：'}},
        {'type': 'at', 'data': {'qq': str(context['user_id'])}},
        {'type': 'text', 'data': {'text': ' 加入本群\n\n%s' % setting.welcome()}}
        ]
        bot.send(context, message=welcome, auto_escape=True)  # 发送欢迎新人


# 如果修改了端口，请修改http-API插件的配置文件中对应的post_url
bot.run(host='127.0.0.1', port=8080)
