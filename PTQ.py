import requests
import json
import time
import logging


# def get_chaos_to_ex(league='Standard')
#     q_head1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'Content-Type':'application/json'}
#     q_head2 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

#     q_url1 = 'https://www.pathofexile.com/api/trade/search/'+league
#     q_url2 = 'https://www.pathofexile.com/api/trade/fetch'

#     q_text = '{"query":{"status":{"option":"online"},"name":"Exalted Orb","type":"Currency","stats":[{"type":"and","filters":[]}]},"sort":{"price":"asc"}}'


def pull_poe_trade_trim(league='Standard', bcount=2, search='{"query":{"status":{"option":"online"},"name":"The Pariah","type":"Unset Ring","stats":[{"type":"and","filters":[]}]},"sort":{"price":"asc"}}'):

    max_items = 10          #Server will reject more per query. Search query returns 100 results.
    ex_to_chaos = 100       #Factor to convert exalted orbs to chaos orbs
    mirr_to_chaos = 14000   #Factor to convert mirrors to chaos orbs
    low_curr_const = 0.1    #Flat Value for "Bad" items

    q_head1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'Content-Type':'application/json'}
    q_head2 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    q_url1 = 'https://www.pathofexile.com/api/trade/search/'+league
    q_url2 = 'https://www.pathofexile.com/api/trade/fetch'

    q_json = json.loads(search)


    x = json.loads( requests.post(q_url1, json=q_json, headers=q_head1).text )

    logging.debug(json.dumps(x))

    q_id = x['id']
    y = {'result':[]}

    for i in range(0,bcount):
        q_url2 = 'https://www.pathofexile.com/api/trade/fetch'
        q_item = []
        for j in range (0+10*i, 10+10*i):
            logging.debug(j)
            q_item.append(x['result'][j])

            logging.debug(q_id,"    " ,json.dumps(q_item))

            item_list = json.dumps(q_item)
            item_list = item_list.replace("[","").replace(']',"").replace(" ","").replace("\"","")

        q_url2 += '/' + item_list + '?query=' + q_id

        logging.debug(q_url2)

        resp = json.loads(requests.get(q_url2, headers=q_head2).text)
        time.sleep(5)

        logging.debug(resp)
        for r in resp['result']:
            y['result'].append(r)


    for i in range(0, len(y['result'])):
        y['result'][i]['price'] = y['result'][i]['listing']['price']
        del y['result'][i]['listing']
        del y['result'][i]['item']['extended']
        del y['result'][i]['id']
        del y['result'][i]['item']['id']
        del y['result'][i]['item']['icon']
        del y['result'][i]['item']['league']

    logging.debug(y)

    #convert currency
    for listing in y['result']:
        bleh = json.dumps(listing['price'])
        logging.debug(bleh)
        if listing['price']['currency'] == "exalted":
            listing['price']['currency'] = "chaos"
            listing['price']['amount'] *= ex_to_chaos
            logging.debug(listing['price'])
        elif listing['price']['currency'] == "mirror":
            listing['price']['currency'] = "chaos"
            listing['price']['amount'] *= ex_to_chaos
            logging.debug(listing['price'])
        elif listing['price']['currency'] != "chaos":
            listing['price']['currency'] = "chaos"
            listing['price']['amount'] = low_curr_const
            logging.debug(listing['price'])

    return y



#Test Func
#pull_poe_trade_trim()