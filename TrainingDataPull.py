import PTQ
import json
import numpy
import csv
import logging

# Search Template
# search = '{                         \
# "query": {                          \
#         "status": {                 \
#             "option": "online"      \
#         },                          \
#         "name": "The Pariah",       \
#         "type": "Unset Ring",       \
#         "stats": [{                 \
#             "type": "and",          \
#             "filters": []           \
#         }]                          \
#     },                              \
#     "sort": {                       \
#         "price": "asc"              \
#     }                               \
# }

def get_rare_item_search(slot, min_chaos_price):
    if slot == "chest":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"armour.chest"}}}}},"sort":{"price":"asc"}}'
    elif slot == "head":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"armour.helmet"}}}}},"sort":{"price":"asc"}}'
    elif slot == "gloves":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"armour.gloves"}}}}},"sort":{"price":"asc"}}'
    elif slot == "boots":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"armour.boots"}}}}},"sort":{"price":"asc"}}'
    elif slot == "ring":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"accessory.ring"}}}}},"sort":{"price":"asc"}}'
    elif slot == "neck":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"accessory.amulet"}}}}},"sort":{"price":"asc"}}'
    elif slot == "belt":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"accessory.belt"}}}}},"sort":{"price":"asc"}}'
    elif slot == "wep":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"weapon"}}}}},"sort":{"price":"asc"}}'
    elif slot == "shield":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"armour.shield"}}}}},"sort":{"price":"asc"}}'
    elif slot == "quiver":
        ret = '{"query":{"status":{"option":"online"},"stats":[{"type":"and","filters":[]}],"filters":{"trade_filters":{"disabled":false,"filters":{"price":{"min":2}}},"type_filters":{"filters":{"rarity":{"option":"rare"},"category":{"option":"armour.quiver"}}}}},"sort":{"price":"asc"}}'

    ret = json.loads(ret)
    ret['query']['filters']['trade_filters']['filters']['price']['min'] = min_chaos_price
    
    return ret
    

def build_training_set(league = "Standard", samp_sz = 50):
    item_types = ["chest", "head", "gloves", "boots", "ring", "neck", "belt", "wep", "shield", "quiver"]
    price_points = [0,1,5,10,50,100,500,1000,5000,10000]

    #item_types = ["chest"]
    #price_points = [0,1,10]

    fullsz = samp_sz*len(item_types)*len(price_points)
    pull_count = int(samp_sz/10)

    it_t = open("item_train.csv", "w")
    pr_t = open("price_train.csv", "w")
    it_v = open("item_verif.csv", "w")
    pr_v = open("price_verif.csv", "w")

    for t in item_types:
        logging.info("Currently Pulling: "+t+"\n")
        for p in price_points:
            logging.info("Pulling " +t+ " at Price: "+str(p)+"\n")
            search_object = json.dumps(get_rare_item_search(t, p))
            tbatch = PTQ.pull_poe_trade_trim(league, pull_count, search_object)
            for i in range(0, len(tbatch['result'])):

                istr = json.dumps(tbatch['result'][i]['item']).replace('{','').replace('}','').replace(',','').replace('[','').replace(']','').replace('"','').replace('\n','').split()
                pstr = json.dumps(tbatch['result'][i]['price']['amount'])

                if i%10 < 7:
                    csv.writer(it_t).writerow(istr)
                    csv.writer(pr_t).writerow(pstr)
                    #it_t.write(istr); it_t.write('\n')
                    #pr_t.write(pstr); pr_t.write('\n')
                    logging.info("Wrote: "+str(i)+" to training.\n")
                else:
                    csv.writer(it_v).writerow(istr)
                    csv.writer(pr_v).writerow(pstr)
                    #it_v.write(istr); it_v.write('\n')
                    #pr_v.write(pstr); pr_v.write('\n')
                    logging.info("Wrote: "+str(i)+" to verification.\n")

logging.basicConfig(level=logging.INFO)
build_training_set(league="Sentinel")

#search = get_rare_item_search('wep',5000)
#print(json.dumps(search))

# search = '{                         \
# "query": {                          \
#         "status": {                 \
#             "option": "online"      \
#         },                          \
#         "stats": [{                 \
#             "type": "and",          \
#             "filters": []           \
#         }],                         \
#         "filters": {                \
#             "type_filters": {           \
#                 "filters": {            \
#                     "rarity":{          \
#                         "option":"rare" \
#                     }                   \
#                 }                       \
#             }                       \
#         }                           \
#     },                              \
#     "sort": {                       \
#         "price": "asc"              \
#     }                               \
# }'

#PTQ.pull_poe_trade_trim("Sentinel", 2, json.dumps(search))
